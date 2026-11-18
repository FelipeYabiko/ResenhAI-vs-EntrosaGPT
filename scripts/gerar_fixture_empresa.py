"""Download company data for demo CNPJs, sanitize it and save it in fixtures/respostas_fontes/.

Run from the repository root:  python scripts/gerar_fixture_empresa.py 00000000000191 [more CNPJs...]

- Only company CNPJs from the demo list (docs/DADOS.md). Never a person's data.
- The raw answer (partners, e-mails, phones, address) stays in memory and is dropped by `sanitizar`.
- Waits 13 s between queries: the source allows 5 per minute per IP.
"""

import sys
import time
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
        dados = sanitizar(baixar(cnpj, tempo_limite_s=10))
        arquivo = salvar_fixture(dados)
        print(
            f"{cnpj}: salvo em {arquivo.relative_to(Path.cwd())} (dado de {dados.atualizado_em:%d/%m/%Y})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
