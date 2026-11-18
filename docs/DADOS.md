# Dados: fontes, limites e privacidade

Testes feitos em 08/11/2026 por consulta direta às fontes. Refaça o teste antes de depender de qualquer fonte: serviços mudam.

## Regras de privacidade

Regulamento 6.9: a demo não pode expor dados pessoais reais de terceiros. Em finanças, usar ambiente de teste ou simulação.

- Dados de **empresa** (CNPJ, situação, CNAE, porte, capital social, data de abertura, município) podem ser usados.
- Dados de **pessoa** nunca: CPF, sócios, e-mail, telefone, endereço detalhado.
- Cadastro de MEI e de empresário individual costuma ter o nome da pessoa na razão social. Ocultar o nome.
- Na demo pública, só CNPJs da lista de demonstração (`fixtures/cnpjs_demo.json`): empresas grandes e CNPJs fictícios válidos. Veja `docs/ARQUITETURA.md`.
- Dados fictícios são marcados como fictícios nos fixtures e na tela.

## Fontes

| Fonte | Para quê | Situação |
| --- | --- | --- |
| API pública de CNPJ (cnpja, `open.cnpja.com`) | Situação cadastral, CNAE, porte, capital social, abertura, Simples e MEI | **Usar.** Testada: resposta traz esses campos |
| Séries do Banco Central (SGS) | Inadimplência e juros de referência | **Usar, com cuidado.** Ver abaixo |
| API CNPJ da Receita no Conecta gov.br | O que o documento original pede | **Não usar.** A página descreve acesso para órgãos públicos, com cadastro e token. Não achei acesso aberto nem preço |
| Banco Central, Estatísticas de Meios de Pagamentos: "Taxas de desconto (MDR) e volumetria" | Referência de mercado para dizer se a taxa atual está acima ou abaixo da média | **Usar como referência, se funcionar.** O recurso aparece no portal de dados abertos. Não consegui abrir a página nem o serviço (bloqueio da minha ferramenta). Nome do endpoint, campos e periodicidade ficam para testar (T-19). O RFC do time diz que é agregado e publicado cerca de 90 dias após o fim do trimestre |
| IBGE | Poder de compra e densidade comercial | **Fora do MVP.** Não confirmei qual série traz isso. Só entra se sobrar tempo |
| BrasilAPI (CNPJ) | Alternativa à cnpja. O RFC do Comparador a escolhe | **Não verificada.** Meu acesso automatizado foi bloqueado. Testar à mão (T-04) e escolher uma das duas. Provavelmente também traz sócios: sanitizar do mesmo jeito |
| Perfil de vendas do comerciante (faturamento, mix, ticket médio, prazo) | Simulador de custo, máquina e limite | Dados públicos de CNPJ não trazem isso. O agente informa. São estimativas do comerciante e aparecem como estimadas |
| Taxas reais de provedores de maquininha | Comparar por marca | **Fora do MVP.** Exigem coleta manual, envelhecem rápido e podem ser promocionais. Se um dia entrarem, cada taxa leva URL da fonte e data de coleta. A IA nunca preenche taxa de memória |

### API pública de CNPJ (cnpja)

- Endereço: `https://open.cnpja.com/office/{cnpj}` (só dígitos).
- Gratuita, sem cadastro. Limite: **5 consultas por minuto por IP**. Dados de estabelecimentos ativos podem ter até 45 dias de defasagem (segundo a própria página). A responsabilidade pelo uso dos dados é nossa, e o uso implica aceitar os termos da plataforma.
- Campos úteis na resposta: `company.name`, `company.equity` (capital social), `company.size`, `company.simples`, `company.simei`, `founded`, `status`, `mainActivity`, `address`.
- A resposta também traz `company.members` (sócios), `emails` e `phones`. **Descartar na entrada**, antes de guardar ou logar.
- Por causa do limite, a demo usa cache e fixtures. Mostre a consulta ao vivo no máximo uma vez, com um CNPJ já aquecido.
- Teste de 18/11/2026 (CNPJ 00000000000191): a resposta trouxe 45 sócios (nome, CPF mascarado, faixa de idade), 1 e-mail, 1 telefone e o endereço completo. Por isso a limpeza acontece logo na entrada, em `api/fontes/cnpj_publico.py` (`sanitizar`), que copia só estes campos:

| Campo no contrato | Campo da fonte | Observação |
| --- | --- | --- |
| `cnpj` | `taxId` | |
| `nome` | `company.name` | Só aparece para administração pública (natureza `1xxx`), empresa pública (2011), sociedade de economia mista (2038) e S.A. (2046, 2054), e nunca para MEI. Em todo o resto, inclusive LTDA (que pode ter um dono só), vem `null`, porque a razão social pode trazer o nome da pessoa. O script de fixtures também se recusa a salvar esses CNPJs |
| `situacao` | `status.text` | em maiúsculas, ex.: `ATIVA` |
| `cnae_principal` | `mainActivity.id` | formatado: 6422100 vira `6422-1/00` |
| `porte` | `company.size.acronym` | ex.: `ME`, `EPP`, `DEMAIS` |
| `abertura` | `founded` | |
| `capital_social` | `company.equity` | |
| `municipio_uf` | `address.city` + `address.state` | só cidade e UF, nunca o endereço |
| `fontes[].atualizado_em` | `updated` | data em que a fonte atualizou o cadastro |

- Para gerar os dados de um CNPJ da demo: `python scripts/gerar_fixture_empresa.py <cnpj>`. O arquivo vai para `fixtures/respostas_fontes/<cnpj>.json`, já sem dado pessoal. Um teste confere que esses arquivos só têm os campos permitidos.

### Banco Central (SGS)

- Padrão: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json`. Para os últimos pontos: `/dados/ultimos/{n}?formato=json`.
- O portal de dados abertos (`dadosabertos.bcb.gov.br`) lista cada série com nome, periodicidade e unidade. **Leia a página da série antes de usar.**
- Teste de 08/11/2026 com `ultimos/3`:

| Série | Último dado retornado | Observação |
| --- | --- | --- |
| 26203 (portal: inadimplência de PJ, pequeno porte) | 01/04/2023 | Trimestral. **Sem dado recente na API.** Não usar como atual |
| 26770 (portal: inadimplência MEI, São Paulo) | 01/04/2023 | Trimestral. **Sem dado recente na API.** Não usar como atual |
| 21083 | 01/09/2026 (3,28) | Mensal. Nome e escopo **a confirmar** na página da série |
| 20714 | 01/09/2026 (32,36) | Mensal. Nome e unidade **a confirmar** na página da série |

- Tarefa: confirmar no portal o que são 21083 e 20714 (e achar outras séries mensais atuais) antes de citar na tela ou no vídeo. Não chame de "inadimplência" algo que não foi confirmado.
- Série trimestral por estado seria útil para a regra regional, mas as que testei param em 2023. Se não houver série atual por estado, usar uma série nacional.

## Cache e falhas

| Fonte | TTL do cache | Se falhar |
| --- | --- | --- |
| CNPJ | 24 h | Usar o último dado em cache e mostrar "dado de DD/MM". Sem cache, `502` com mensagem clara |
| Banco Central | 24 h | Igual |

Timeout de 1,2 s por chamada. Nunca devolver dado inventado no lugar de falha.

## Dados fictícios

- `fixtures/cnpjs_demo.json`: lista de CNPJs da demonstração, cada um com a origem (`real_empresa_grande` ou `ficticio`) e a data em que foi conferido. Montada em 18/11/2026:
  - **Empresas grandes** (Banco do Brasil, Caixa, Petrobras, Correios): todas estatais, confirmadas na fonte pública com `scripts/gerar_fixture_empresa.py`, que só salva empresa de natureza grande.
  - **Fictícios** (mercadinho, salão e loja de material de construção, os 3 perfis da landing): dígitos válidos, gerados com `scripts/gerar_cnpj_ficticio.py`, que só aceita número que a fonte responde como **inexistente** (HTTP 404). Os dados deles são inventados e o nome termina em "(FICTÍCIO)".
- **Fictício nunca vai à fonte:** na consulta (#16), CNPJ de origem `ficticio` usa só os dados do fixture. Assim, mesmo que o número passe a existir um dia, nenhum dado real é buscado nem misturado com o inventado. Antes de gravar o vídeo e antes da avaliação, rode `python scripts/gerar_cnpj_ficticio.py --conferir`.
- **Atenção:** CNPJ com dígito válido não é fictício só por parecer genérico. O `11.222.333/0001-81`, muito usado como exemplo, é de uma associação real (conferido em 18/11/2026). Por isso todo fictício passa pela checagem na fonte. Para testes, use `98.765.435/0001-21` (inexistente na fonte em 18/11/2026, fora da lista da demo).
- CNPJ fictício precisa ter **dígitos verificadores válidos**, senão a validação (RF-01) o recusa.
- Os códigos CNAE dos fictícios (4712-1/00 minimercado, 9602-5/01 cabeleireiro, 4744-0/99 material de construção) foram escritos de memória: conferir na tabela CNAE do IBGE antes de aparecerem no vídeo.
- Faturamentos de exemplo para a demo ficam em `fixtures/` e são sempre marcados como exemplo.
- O contrato simulado e as propostas de exemplo usam só nomes inventados.
- O catálogo de máquinas e de taxas da demo é fictício e marcado como ilustrativo. Não use marcas reais.
- O caso de teste de referência do simulador (R$ 15 mil por mês, economia de R$ 169,80) está em `docs/ARQUITETURA.md`.

## Atribuição

O README deve listar as fontes e dizer que os dados de empresa vêm de fontes públicas, que limites e taxas são simulações e que a pontuação é por premissas do time, sem validação estatística.
