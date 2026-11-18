# Scripts

Utilitários do projeto. Previsto: gerar CNPJ fictício com dígitos verificadores válidos (T-09) e aquecer o cache antes da demo (`docs/DEMO.md`).

Todo script novo documenta aqui o que faz, como rodar e que não usa dado pessoal.

## `exportar_openapi.py`

Gera `api/openapi.json` a partir dos schemas da API (`api/app/schemas.py`). Rode da raiz do repositório depois de mudar o contrato: `python scripts/exportar_openapi.py`. Não acessa a rede e não usa dado pessoal. O teste `api/tests/test_contrato.py` falha se o arquivo salvo estiver desatualizado.

## `verificar.py`

Roda lint (`ruff check`), formatação (`ruff format --check`) e testes (`pytest`) da API de uma vez e diz o que falhou. Rode da raiz: `python scripts/verificar.py`. Precisa das dependências de `api/requirements-dev.txt`. Não acessa a rede e não usa dado pessoal.

## `gerar_fixture_empresa.py`

Busca na fonte pública de CNPJ (open.cnpja.com) os dados de um ou mais CNPJs **de empresa** da lista de demonstração, tira tudo o que é pessoal (sócios, e-mails, telefones, endereço; nome de MEI) e salva em `fixtures/respostas_fontes/<cnpj>.json`. Rode da raiz: `python scripts/gerar_fixture_empresa.py 00000000000191`. Espera 13 s entre consultas, porque a fonte aceita 5 por minuto. A resposta crua nunca vai para disco nem para o terminal.
