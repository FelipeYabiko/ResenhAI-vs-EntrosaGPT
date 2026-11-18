"""Generate fictitious CNPJs with valid check digits that do NOT exist in the public CNPJ source.

Run from the repository root:  python scripts/gerar_cnpj_ficticio.py 3

A random valid CNPJ can belong to a real company, or to a MEI (a person). So every candidate is
checked against open.cnpja.com and kept only if the source answers "not found" (HTTP 404).
"Not found today" is what we can check: write the check date next to each CNPJ in the demo list.
Waits 13 s between queries (the source allows 5 per minute).
"""

import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "api"))

from app.cnpj import PESOS_PRIMEIRO, PESOS_SEGUNDO, _digito
from fontes.cnpj_publico import existe_na_fonte

RAIZ_INICIAL = 98765432  # arbitrary 8-digit root; headquarters branch is always 0001
PAUSA_S = 13


def com_digitos(base12: str) -> str:
    numeros = [int(c) for c in base12]
    primeiro = _digito(numeros, PESOS_PRIMEIRO)
    return base12 + str(primeiro) + str(_digito([*numeros, primeiro], PESOS_SEGUNDO))


def main(quantidade: int) -> int:
    achados, raiz = [], RAIZ_INICIAL
    while len(achados) < quantidade:
        cnpj = com_digitos(f"{raiz:08d}0001")
        if achados or raiz != RAIZ_INICIAL:
            time.sleep(PAUSA_S)
        if existe_na_fonte(cnpj):
            print(f"{cnpj}: existe na fonte, descartado")
        else:
            achados.append(cnpj)
            print(f"{cnpj}: não existe na fonte em {date.today():%d/%m/%Y}, pode ser usado como fictício")
        raiz += 1
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
