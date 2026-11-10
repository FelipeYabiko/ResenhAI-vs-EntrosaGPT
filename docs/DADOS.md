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

- `fixtures/cnpjs_demo.json`: lista de CNPJs da demonstração, cada um com a origem (`real_empresa_grande` ou `ficticio`).
- CNPJ fictício precisa ter **dígitos verificadores válidos**, senão a validação (RF-01) o recusa. Gere com `scripts/` e registre aqui como foram gerados.
- Faturamentos de exemplo para a demo ficam em `fixtures/` e são sempre marcados como exemplo.
- O contrato simulado e as propostas de exemplo usam só nomes inventados.
- O catálogo de máquinas e de taxas da demo é fictício e marcado como ilustrativo. Não use marcas reais.
- O caso de teste de referência do simulador (R$ 15 mil por mês, economia de R$ 169,80) está em `docs/ARQUITETURA.md`.

## Atribuição

O README deve listar as fontes e dizer que os dados de empresa vêm de fontes públicas, que limites e taxas são simulações e que a pontuação é por premissas do time, sem validação estatística.
