# oeispy

A Python project for OEIS sequences, analysis, and factoring tools.

## Structure

*   `src/oeispy`: Main package containing sequence implementations and utilities.
    *   `core.py`: Core sequence class.
    *   `sequences/`: Implementations of individual OEIS sequences.
    *   `utils/`: Helper modules (factoring, primes, etc.).
*   `scripts/`: Executable scripts for various tasks (e.g., aliquot sequences).
*   `data/`: Data storage for scripts.

## Installation

This project uses `uv` for dependency management and is compatible with NixOS via `shell.nix`.

### Prerequisites

*   Python 3.8+
*   `uv` (Python package manager)
*   **Nix users**: Run `nix-shell` to load system dependencies (`primesieve`, `gmp`, `mpfr`).

### Setup

1.  Enter the environment (if using Nix):
    ```bash
    nix-shell
    ```

2.  Install the package in editable mode:
    ```bash
    uv pip install -e .
    ```

## Usage

You can run scripts using `uv run`. The scripts are located in the `scripts/` directory.

**Example: Running the Aliquot script**

```bash
uv run scripts/aliquot.py --help
```

**Example: Using the library in Python**

```python
from oeispy.sequences.A000040 import A000040
seq = A000040()
print(seq(1))  # Output: 2
```

## Development

*   **Adding Dependencies**: Update `pyproject.toml` and run `uv pip install -e .`.
*   **New Sequences**: Add new sequence files to `src/oeispy/sequences/` inheriting from `oeispy.core.Sequence`.
