"""Write the API v1 OpenAPI to api/openapi.json.

Run from the repository root: python scripts/exportar_openapi.py
Uses no network and no personal data.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "api"))

from app.main import app


def gerar() -> str:
    return json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    destino = RAIZ / "api" / "openapi.json"
    destino.write_text(gerar(), encoding="utf-8")
    print(f"OpenAPI salvo em {destino.relative_to(RAIZ)}")
