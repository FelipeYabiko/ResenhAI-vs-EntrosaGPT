"""Download company data for demo CNPJs, sanitize it and save it in fixtures/respostas_fontes/.

Run from the repository root:  python scripts/gerar_fixture_empresa.py 00000000000191 [more CNPJs...]

- Only large companies (corporations, state companies, public bodies) are saved: for any other
  legal nature, or a MEI, the script refuses and saves nothing, because the CNPJ itself can point
  to a person. Fictitious demo CNPJs do not come from the source.
- The raw answer (partners, e-mails, phones, address) stays in memory and is dropped by `sanitizar`.
- Waits 13 s between queries: the source allows 5 per minute per IP.
"""

import sys
import time
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "api"))

from fontes.cnpj_publico import baixar, salvar_fixture, sanitizar

PAUSA_S = 13


def main(cnpjs: list[str]) -> int:
    if not cnpjs:
        print(__doc__)
        return 1
    for i, cnpj in enumerate(cnpjs):
        if i:
            time.sleep(PAUSA_S)
        try:
            dados = sanitizar(baixar(cnpj, tempo_limite_s=10), cnpj)
        except (urllib.error.HTTPError, ValueError) as erro:
            print(f"{cnpj}: não salvo ({erro}).")
            continue
        if dados.empresa.nome is None:
            print(f"{cnpj}: não salvo. Não é empresa grande (S.A., estatal ou órgão público).")
            continue
        arquivo = salvar_fixture(dados)
        print(f"{cnpj}: salvo em {arquivo} (dado de {dados.atualizado_em:%d/%m/%Y})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
