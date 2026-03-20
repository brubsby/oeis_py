import logging
import math
import threading
import time
import gmpy2
from flask import Flask, request, jsonify
from oeisfactor.db import OEISFactorDB, WorkerPreferences, CompositeOrdering, _compute_optimal_gpu_b1
from oeisfactor.worker.common import fmt_seconds

# Number of upcoming GPU composites to pre-warm the B1 cache for
GPU_WARMUP_LOOKAHEAD = 5

# --- PID controller configuration ---
TARGET_BUFFER_SECONDS = 86400  # target queue depth: 1 day of current-fleet capacity
THROUGHPUT_WINDOW_SECONDS = 21600  # 6h rolling window for throughput T measurement
K_MIN = 0.1                 # minimum B2 multiplier (B2 = B1 * 100 * k)
K_MAX = 10.0                # maximum B2 multiplier
K_MIN_LOG = math.log10(K_MIN)   # -1.0
K_MAX_LOG = math.log10(K_MAX)   # +1.0
PID_KP = 1e-8               # proportional gain  (tune empirically)
PID_KI = 1e-11              # integral gain
PID_KD = 1e-6               # derivative gain (on PV, not error)

app = Flask(__name__)
db = OEISFactorDB()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_warmup_lock = threading.Lock()

def _background_warm_gpu_cache(curves: int, n: int = GPU_WARMUP_LOOKAHEAD):
    """Precompute optimal B1 for the next N GPU composites in the background."""
    if not _warmup_lock.acquire(blocking=False):
        return  # another warmup is already running
    try:
        prefs = WorkerPreferences(skip_outstanding_residues=True)
        count = 0
        for row in db.iter_unfactored_composites(prefs, validate=False):
            if count >= n:
                break
            _compute_optimal_gpu_b1(curves, round(float(row['t_level'] or 0), 1))
            count += 1
        logger.debug(f"GPU B1 cache warmed for {count} composites (curves={curves})")
    except Exception as e:
        logger.warning(f"GPU cache warmup error: {e}")
    finally:
        _warmup_lock.release()

# Warm cache on startup for the default GPU curve count
threading.Thread(target=_background_warm_gpu_cache, args=(8192,), daemon=True).start()

# --- PID controller ---
_current_b2_multiplier = 1.0

def _run_pid_tick():
    global _current_b2_multiplier
    now = time.time()
    u, integral, last_pv, last_update = db.get_pid_state()

    dt = now - last_update if last_update > 0 else 0

    pv = db.get_pending_stage2_pv()
    T = db.get_throughput_t(THROUGHPUT_WINDOW_SECONDS)

    if T < 1e-10:
        # No throughput data yet — hold at neutral, reset state
        logger.debug("PID: no throughput data yet, holding k=1.0")
        db.update_pid_state(0.0, 0.0, pv, now)
        _current_b2_multiplier = 1.0
        return

    sp = T * TARGET_BUFFER_SECONDS
    error = sp - pv

    # Derivative on PV (not error) to avoid derivative kick on setpoint changes
    d_pv = (pv - last_pv) / dt if dt > 0 else 0.0

    u_raw = PID_KP * error + integral - PID_KD * d_pv
    u_clamped = max(K_MIN_LOG, min(K_MAX_LOG, u_raw))

    # Anti-windup: only accumulate integral when not saturated in the wrong direction
    if (u_raw > K_MAX_LOG and error > 0) or (u_raw < K_MIN_LOG and error < 0):
        new_integral = integral  # saturated and error keeps pushing → freeze
    else:
        new_integral = integral + PID_KI * error * dt

    k = 10 ** u_clamped
    _current_b2_multiplier = k
    db.update_pid_state(u_clamped, new_integral, pv, now)
    logger.info(f"PID: PV={fmt_seconds(pv)} SP={fmt_seconds(sp)} err={fmt_seconds(error)} u={u_clamped:.3f} k={k:.3f}")


@app.route('/api/worker/register', methods=['POST'])
def register_worker():
    data = request.json
    name = data.get("name")
    client_type = data.get("type", "CPU")
    if not name:
        return jsonify({"error": "name is required"}), 400
    
    try:
        db.register_client(name, type=client_type)
        return jsonify({"status": "success", "message": f"Registered worker {name}"}), 200
    except Exception as e:
        logger.error(f"Error registering worker: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/work/gpu', methods=['GET'])
def get_gpu_work():
    client_name = request.args.get("client_name")
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400
    
    curves = int(request.args.get("curves", 8192))
    prefs = WorkerPreferences(
        digit_limit=int(request.args.get("digit_limit", 300)),
        pretest=float(request.args.get("pretest", 0.3)),
        skip_outstanding_residues=request.args.get("skip_outstanding_residues", "true").lower() == "true",
        ordering=CompositeOrdering(request.args.get("ordering", CompositeOrdering.T_LEVEL.value)),
    )

    work = db.request_stage1_GPU_work(client_name, curves=curves, prefs=prefs)
    if work:
        composite, b1, completion_time, expression, t_level_val = work
        threading.Thread(target=_background_warm_gpu_cache, args=(curves,), daemon=True).start()
        return jsonify({
            "composite": str(composite),
            "b1": b1,
            "completion_time": completion_time,
            "expression": expression,
            "t_level": t_level_val,
        })
    else:
        return jsonify({"status": "no work available"}), 404

@app.route('/api/submit/gpu', methods=['POST'])
def submit_gpu_work():
    data = request.json
    client_name = data.get("client_name")
    composite = gmpy2.mpz(data.get("composite"))
    residue_lines = data.get("residue_lines")
    duration = data.get("duration")
    
    if not residue_lines or not isinstance(residue_lines, list):
        return jsonify({"error": "residue_lines must be a non-empty list"}), 400
        
    try:
        db.submit_stage_1_curves(composite, residue_lines, client_name, duration)
        threading.Thread(target=_run_pid_tick, daemon=True).start()
        return jsonify({"status": "success", "count": len(residue_lines)}), 200
    except Exception as e:
        logger.error(f"Error submitting GPU work: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/work/cpu', methods=['GET'])
def get_cpu_work():
    client_name = request.args.get("client_name")
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400
    
    limit = int(request.args.get("limit", 100))
    work_batch = db.request_stage2_CPU_work(client_name, limit=limit)

    return jsonify({
        "status": "success",
        "work_batch": work_batch,
        "b2_multiplier": _current_b2_multiplier,
    })

@app.route('/api/submit/cpu/batch', methods=['POST'])
def submit_cpu_work_batch():
    data = request.json
    client_name = data.get("client_name")
    completions = data.get("completions")

    if not completions or not isinstance(completions, list):
        return jsonify({"error": "completions must be a non-empty list"}), 400

    try:
        new_t_levels = db.submit_stage_2_curves_batch(completions, client_name)
        threading.Thread(target=_run_pid_tick, daemon=True).start()
        return jsonify({"status": "success", "count": len(completions), "new_t_levels": new_t_levels}), 200
    except Exception as e:
        logger.error(f"Error submitting CPU batch: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/submit/cpu', methods=['POST'])
def submit_cpu_work():
    data = request.json
    client_name = data.get("client_name")
    composite = gmpy2.mpz(data.get("composite"))
    sigma = data.get("sigma")
    b2_start = data.get("b2_start")
    b2_end = data.get("b2_end")
    duration = data.get("duration")
    
    try:
        db.submit_stage_2_curves(composite, sigma, client_name, b2_start, b2_end, duration)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error submitting CPU work: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/work/cpu/full', methods=['GET'])
def get_full_cpu_work():
    client_name = request.args.get("client_name")
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400

    prefs = WorkerPreferences(
        digit_limit=int(request.args.get("digit_limit", 300)),
        pretest=float(request.args.get("pretest", 0.3)),
        ordering=CompositeOrdering(request.args.get("ordering", CompositeOrdering.T_LEVEL.value)),
    )

    work = db.request_full_CPU_work(client_name, prefs=prefs)
    if work:
        composite, b1, suggested_curves, expression, t_level_val = work
        return jsonify({"composite": str(composite), "b1": b1, "suggested_curves": suggested_curves, "expression": expression, "t_level": t_level_val})
    return jsonify({"status": "no work available"}), 404

@app.route('/api/submit/cpu/full', methods=['POST'])
def submit_full_cpu_work():
    data = request.json
    client_name = data.get("client_name")
    composite = data.get("composite")
    curve_groups = data.get("curve_groups")  # [{count, b1, b2, ecm_param}]

    if not curve_groups:
        return jsonify({"error": "curve_groups required"}), 400

    try:
        new_t = db.submit_full_cpu_curves(composite, curve_groups, client_name)
        return jsonify({"status": "success", "new_t_level": new_t}), 200
    except Exception as e:
        logger.error(f"Error submitting full CPU curves: {e}")
        return jsonify({"error": str(e)}), 500

from oeispy.utils import factordb

@app.route('/api/submit/factor', methods=['POST'])
def submit_factor():
    data = request.json
    client_name = data.get("client_name")
    composite = int(data.get("composite"))
    factors = data.get("factors") # list of factors found
    
    if not factors or not isinstance(factors, list):
        return jsonify({"error": "factors must be a non-empty list"}), 400

    try:
        # 1. Report to FactorDB
        factordb.report({composite: factors})
        logger.info(f"Reported factors {factors} for composite {composite} from client {client_name}")
        
        # 2. Update local DB logic for new remaining composites
        # This will remove the old composite record and create new ones for the remaining cofactors
        remaining = db.get_remaining_composites(composite)
        
        return jsonify({
            "status": "success", 
            "message": "Factors reported successfully",
            "remaining_composites": [str(c) for c in remaining]
        }), 200
    except Exception as e:
        logger.error(f"Error submitting factor: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
