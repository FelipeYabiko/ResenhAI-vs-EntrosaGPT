"""Generate fictitious CNPJs with valid check digits that do NOT exist in the public CNPJ source.

Run from the repository root:
    python scripts/gerar_cnpj_ficticio.py 3          # find 3 new fictitious CNPJs
    python scripts/gerar_cnpj_ficticio.py --conferir # re-check the fictitious ones in the demo list

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
from fontes.demo import cnpjs_da_demo

RAIZ_INICIAL = 98765432  # arbitrary 8-digit root; headquarters branch is always 0001
PAUSA_S = 13
CNPJ_DE_CONTROLE = "00000000000191"  # known to exist: if the source does not find it, something is wrong


def fonte_responde_certo() -> bool:
    if existe_na_fonte(CNPJ_DE_CONTROLE):
        return True
    print(
        f"A fonte não encontrou o CNPJ de controle {CNPJ_DE_CONTROLE}. Parando: um 'não existe' agora não é confiável."
    )
    return False


def conferir_lista() -> int:
    ficticios = [c for c, item in cnpjs_da_demo().items() if item.origem == "ficticio"]
    problemas = 0
    for cnpj in ficticios:
        time.sleep(PAUSA_S)
        if existe_na_fonte(cnpj):
            problemas += 1
            print(f"{cnpj}: PASSOU A EXISTIR na fonte. Tire da lista e gere outro (docs/DADOS.md).")
        else:
            print(f"{cnpj}: continua inexistente em {date.today():%d/%m/%Y}")
    return 1 if problemas else 0


def com_digitos(base12: str) -> str:
    numeros = [int(c) for c in base12]
    primeiro = _digito(numeros, PESOS_PRIMEIRO)
    return base12 + str(primeiro) + str(_digito([*numeros, primeiro], PESOS_SEGUNDO))


def main(quantidade: int) -> int:
    achados, raiz = [], RAIZ_INICIAL
    while len(achados) < quantidade:
        cnpj = com_digitos(f"{raiz:08d}0001")
        time.sleep(PAUSA_S)
        if existe_na_fonte(cnpj):
            print(f"{cnpj}: existe na fonte, descartado")
        else:
            achados.append(cnpj)
            print(f"{cnpj}: não existe na fonte em {date.today():%d/%m/%Y}, pode ser usado como fictício")
        raiz += 1
    return 0


if __name__ == "__main__":
    if not fonte_responde_certo():
        sys.exit(2)
    if sys.argv[1:] == ["--conferir"]:
        sys.exit(conferir_lista())
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
