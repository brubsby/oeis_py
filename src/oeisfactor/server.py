import logging
import gmpy2
from flask import Flask, request, jsonify
from oeisfactor.db import OEISFactorDB

app = Flask(__name__)
db = OEISFactorDB()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    digit_limit = int(request.args.get("digit_limit", 300))
    curves = int(request.args.get("curves", 8192))
    
    work = db.request_stage1_GPU_work(client_name, digit_limit=digit_limit, curves=curves)
    if work:
        composite, b1, completion_time = work
        return jsonify({
            "composite": str(composite),
            "b1": b1,
            "completion_time": completion_time
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
        "work_batch": work_batch
    })

@app.route('/api/submit/cpu/batch', methods=['POST'])
def submit_cpu_work_batch():
    data = request.json
    client_name = data.get("client_name")
    completions = data.get("completions")

    if not completions or not isinstance(completions, list):
        return jsonify({"error": "completions must be a non-empty list"}), 400

    try:
        db.submit_stage_2_curves_batch(completions, client_name)
        return jsonify({"status": "success", "count": len(completions)}), 200
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
