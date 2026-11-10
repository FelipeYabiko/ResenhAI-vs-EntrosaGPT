# Produto: CredFácil

Documento de produto do MVP. Mudou o escopo? Atualize aqui e em `docs/STATUS.md` no mesmo PR.

Origem: documento "CredFácil: Arquitetura de Inteligência de Crédito Aberto e Operações de Campo Acessíveis" (plataforma POS-Intel), aprovado pelo time. Este arquivo detalha o que vamos construir a partir dele e marca onde nos afastamos dele.

O simulador de custo vem de outro documento do time, o RFC "MVP Comparador de Maquininhas (Pós-Cred)". Absorvemos o cálculo, a métrica de economia em reais e o benchmark do Banco Central. Ficam de fora os links de afiliado, a comparação por marca real e a validação em larga escala (ver `docs/DECISOES.md`, D-011 a D-013).

## Em uma frase

O vendedor de campo digita ou dita o CNPJ de um comerciante e, em segundos, recebe a máquina de cartão indicada, um limite de crédito **simulado** e as taxas de antecipação de recebíveis. A matriz recebe a proposta na hora, em um painel.

## Trilha

Pagamentos & finanças (acesso a crédito e como empresas recebem). Regulamento 5.4: o problema e o público precisam estar dentro da trilha. Por isso o **beneficiário é o pequeno comerciante** (demora para ter máquina e crédito, taxa mal ajustada). O vendedor é o canal.

## Quem usa

| Papel | O que faz | Observação |
| --- | --- | --- |
| Agente de campo | Consulta o CNPJ, vê a recomendação e envia a proposta | Usuário principal do app |
| Analista da matriz | Recebe propostas, resolve pendências, aprova ou recusa | Usuário do painel |
| Comerciante | Recebe a oferta | Não usa o app. É o beneficiário e deve aparecer na narrativa do vídeo |

Em aberto (D-012): o agente trabalha para uma credenciadora específica ou para um marketplace que compara vários provedores? A proposta padrão é a primeira: o app compara a situação atual do comerciante com o catálogo de demonstração da credenciadora. A segunda exige taxas reais por provedor, com fonte e data, e está fora do MVP.

Hipótese a validar: que o processo atual de uma credenciadora seja lento e fragmentado, como o documento afirma. Não temos linha de base. Não cite número de "antes" sem fonte.

## Fluxo principal do MVP

1. **Ingestão.** O agente digita ou dita o CNPJ e informa o perfil de vendas do comerciante: faturamento mensal, mix de pagamento (débito, crédito à vista, parcelado, Pix), ticket médio e prazo de recebimento desejado. Se o comerciante já tem maquininha, informa também as taxas que paga hoje e o custo da máquina atual. São estimativas do comerciante e aparecem como estimadas.
2. **Processamento.** O backend consulta as fontes públicas (ver `docs/DADOS.md`), com cache, e monta o perfil.
3. **Avaliação.** O motor de regras devolve a faixa de risco com os fatores que a explicam. O simulador de custo devolve o modelo de máquina recomendado, o custo mensal atual contra o custo com a oferta e a **economia em reais por mês e por ano**. Saem também o limite de crédito simulado e as taxas de antecipação simuladas. Quando houver dado, o sistema mostra se a taxa atual está acima ou abaixo da referência de mercado do Banco Central.
4. **Despacho.** O agente envia a proposta. A matriz recebe um evento estruturado no painel, ao vivo, e pode aprovar, recusar ou pedir pendência. Ao aprovar, o sistema gera um contrato simulado em PDF.

Toda tela e toda resposta da API que mostrem limite, taxa ou aprovação carregam o aviso **"Simulação. Não é oferta de crédito."**

## Telas

| Tela | Conteúdo |
| --- | --- |
| Consulta (agente) | Campo de CNPJ, botão de ditado por voz, perfil de vendas (faturamento, mix, ticket médio, prazo de recebimento), situação atual opcional (taxas, custo da máquina, custo de saída), botão consultar |
| Resultado (agente) | **Economia em reais por mês e por ano em destaque**, faixa de risco e fatores, máquina recomendada, limite simulado, taxas, referência de mercado, fontes com data de atualização, aviso de simulação, botão enviar proposta |
| Painel da matriz | Lista de propostas em tempo real, filtro por status, detalhe da proposta, ações aprovar, recusar, pedir pendência |
| Contrato simulado | PDF gerado ao aprovar, com marca d'água "SIMULAÇÃO" |

## Requisitos funcionais e critérios de aceite

| ID | Requisito | Critério de aceite |
| --- | --- | --- |
| RF-01 | Validar CNPJ digitado | CNPJ inválido (formato ou dígito) mostra erro claro e não chama fonte externa |
| RF-02 | Ditar o CNPJ por voz | O texto reconhecido aparece na tela para conferência antes de consultar; digitar continua possível |
| RF-03 | Consultar fontes públicas | Resposta traz situação cadastral, CNAE, porte, tempo de atividade e capital social, com a data de cada fonte |
| RF-04 | Calcular a faixa de risco | Mesmo CNPJ e mesmo faturamento sempre dão o mesmo resultado. Cada fator mostra sua contribuição |
| RF-05 | Recomendar máquina, limite e taxas | Valores vêm da regra e do catálogo de demonstração documentados, marcados como simulação |
| RF-06 | Enviar proposta | A proposta aparece no painel da matriz em até 2 s sem recarregar a página |
| RF-07 | Tratar pendências | A matriz pede pendência com texto estruturado e o agente a vê na proposta |
| RF-08 | Aprovar ou recusar | O status muda para os dois lados e um evento fica registrado |
| RF-09 | Contrato simulado | PDF baixável, com dados da proposta e marca d'água de simulação |
| RF-10 | Fonte fora do ar | O sistema usa o último dado em cache marcado como "dado de DD/MM" ou mostra erro claro. Nunca dado inventado |
| RF-11 | Simular a economia | Mostra custo atual, custo com a oferta e economia por mês e por ano, em reais, marcados como estimativa. Caso de referência: R$ 15 mil por mês, 40% débito, 40% crédito à vista, 20% Pix (sem taxa), taxas atuais 1,99% e 4,98% contra 0,99% e 3,15%, sem custo de máquina. Esperado: R$ 418,20, R$ 248,40 e economia de R$ 169,80 por mês |
| RF-12 | Considerar o custo de saída | Se informado (multa, máquina já comprada), entra no cálculo e o resultado diz em quantos meses a economia o compensa |
| RF-13 | Referência de mercado | Mostra se a taxa atual está acima ou abaixo da referência do Banco Central, com a data. É agregada e defasada e nunca aparece como taxa de provedor. Se o recurso não funcionar, a função é cortada |

## Requisitos não funcionais

- **Tempo:** CNPJ até resultado em menos de 2 s, medido com cache quente. A meta vale para a demo, não para chamadas frias às fontes.
- **Acessibilidade:** WCAG 2.1 nível AA. Ver `docs/ACESSIBILIDADE.md`.
- **Disponibilidade:** demo no ar em HTTPS durante toda a avaliação e até 15/12, sem login obrigatório para os jurados.
- **Privacidade:** nenhum dado pessoal real de terceiros. Ver `docs/DADOS.md`.
- **Idioma:** interface em português do Brasil. Vídeo em inglês (proposta).

## Fora do escopo do MVP

- Crédito, contrato ou transação real. Tudo é simulação.
- Links de afiliado, receita de comissão e comparação por marca real de maquininha (taxas reais de provedores exigem fonte e data, ver `docs/DADOS.md`). O modelo de receita pode aparecer no pitch como próximo passo.
- Coleta automática de taxas e Open Finance.
- CPF, dados de sócios e qualquer dado pessoal.
- Modelo de machine learning treinado. A pontuação é por regras.
- IBGE (poder de compra e densidade comercial), se atrasar. É opcional.
- Assinatura real do contrato, integração com banco ou adquirente de verdade.
- Cadastro e login reais de usuários. Há dois perfis de demonstração.
- App nativo.
- Texto explicativo gerado por LLM (possível extra no fim; nunca para calcular).

## Impacto e como medimos

Medimos o que o próprio produto mede, sem inventar linha de base:

- economia média, em reais por mês, nos casos simulados. São dados de exemplo e nunca devem ser apresentados como resultado real;
- segundos entre digitar o CNPJ e ter a proposta enviada;
- campos que o agente precisa digitar (meta: dois);
- pendências por proposta, quando a matriz pede documento.

Opcional, se sobrar tempo: 5 a 10 conversas anônimas com comerciantes para medir intenção de troca, usando só o número agregado, sem extrato nem dado pessoal e sem aparecer no vídeo (T-28).

A dúvida de como o impacto é avaliado na trilha deve ser enviada à organização (oi@hackbrasil.com). Ver `docs/STATUS.md`.

## Glossário

- **POS:** terminal de pagamento, a "maquininha".
- **Antecipação de recebíveis:** receber hoje valores de vendas que cairiam no futuro, com desconto (taxa).
- **CNAE:** Classificação Nacional de Atividades Econômicas, o código da atividade da empresa.
- **MEI:** microempreendedor individual.
- **MDR:** taxa de desconto do comerciante em cada venda no cartão, cobrada pela credenciadora.
- **Matriz:** a central da credenciadora, onde ficam analistas de risco e emissão de contratos.
- **Credenciadora:** empresa que habilita comerciantes a aceitar cartão e oferece as maquininhas.
