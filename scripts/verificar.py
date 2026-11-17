"""Run every API check in one go: lint, format and tests.

Run from the repository root, with the API dev requirements installed:
    python scripts/verificar.py
Works on Windows, macOS and Linux. Uses no network and no personal data.
"""

import subprocess
import sys
from pathlib import Path

API = Path(__file__).resolve().parent.parent / "api"

ETAPAS = [
    ("Lint", [sys.executable, "-m", "ruff", "check", "."]),
    ("Formatação", [sys.executable, "-m", "ruff", "format", "--check", "."]),
    ("Testes", [sys.executable, "-m", "pytest", "-q"]),
]


def main() -> int:
    falhas = []
    for nome, comando in ETAPAS:
        print(f"\n== {nome} ==", flush=True)
        if subprocess.run(comando, cwd=API, check=False).returncode != 0:
            falhas.append(nome)
    if falhas:
        print(f"\nFalhou: {', '.join(falhas)}")
        return 1
    print("\nTudo certo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
