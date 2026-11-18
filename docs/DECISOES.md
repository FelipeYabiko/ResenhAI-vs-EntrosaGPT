# Registro de decisões

Cada decisão tem número, data, situação e motivo. Situação: **Decidida** (o time confirmou), **Proposta** (sugestão aguardando confirmação) ou **Em aberto**.

| ID | Decisão | Situação | Data | Motivo e alternativas |
| --- | --- | --- | --- | --- |
| D-001 | Trilha: Pagamentos & finanças | Decidida (informada pelo Felipe) | 08/11 | A ideia cabe em "acesso a crédito" e "como empresas recebem". Alternativa considerada: Logística & automação |
| D-002 | Ideia: CredFácil | Decidida (aprovada pelo time, segundo o Felipe) | 08/11 | Dá papel a cada pessoa, fluxo curto, bom para vídeo, acessibilidade como diferencial. Alternativas: cobrança inteligente, copiloto de caixa do MEI |
| D-003 | Pontuação por regras explicáveis, sem ML e sem LLM | Proposta | 08/11 | Sem dados reais de inadimplência não dá para treinar nem validar. Regras são testáveis e explicáveis. Honestidade: premissas do time |
| D-004 | Hospedagem de web, API e banco: **Vercel** | Decidida em parte (informada pelo Felipe) | 09/11 | Requisitos: HTTPS, deploy automático, não "dormir", no ar até 15/12. Falta confirmar na Vercel: FastAPI (funções Python), SSE e banco Postgres (não verificados). Plano B se algo falhar: front na Vercel ou Netlify, API no Render, banco no Neon (ver T-36) |
| D-014 | Deploy na Vercel Hobby com um dono (Felipe): os demais abrem PR e o dono faz o merge | Proposta | 09/11 | O plano Hobby só permite deploy pelo dono da conta e bloqueia commit de outro autor ("commit author does not have contributing access"). Alternativa: Pro (US$ 20 por pessoa/mês). O merge pelo botão pode manter o autor original: testar (T-36) |
| D-005 | Modo demo com lista de CNPJs permitidos e sanitização | Proposta | 08/11 | Evita expor dado pessoal (MEI). Custo: jurados não consultam qualquer CNPJ |
| D-006 | Tempo real com Server-Sent Events, webhook opcional | Proposta | 08/11 | Mais simples que WebSocket para este caso |
| D-007 | Idioma: código e commits em inglês, documentos e interface em português, vídeo em inglês | Proposta | 08/11 | Vídeo em inglês é preferido pela organização |
| D-008 | Fontes: API pública de CNPJ (cnpja ou BrasilAPI, a testar) e referências do Banco Central (séries e MDR). IBGE fora do MVP | Proposta | 08/11 | A API oficial da Receita é para órgãos públicos. Ver `docs/DADOS.md` |
| D-009 | Monorepo com `/web` e `/api`. Sem `/ml` | Proposta | 08/11 | Não há modelo treinado. O scoring mora em `/api/scoring` |
| D-010 | Licença do projeto | Em aberto | 08/11 | Recomendada pelo regulamento (6.6), não exigida. Não pode restringir leitura, execução e teste pelos jurados |
| D-011 | Absorver no CredFácil o simulador de custo, a métrica de economia em reais e a referência do Banco Central do RFC "Comparador de Maquininhas" | Proposta | 08/11 | Dá um número de impacto mensurável e uma recomendação de máquina auditável. Alternativa: trocar o projeto pelo Comparador (usuário é o comerciante), que perde voz, painel da matriz e crédito, e compete direto com comparadores que já existem |
| D-012 | Quem é o agente: credenciadora específica ou marketplace multi-provedor | Em aberto | 08/11 | Padrão proposto: credenciadora, com catálogo de demonstração fictício comparado à situação atual do comerciante. Um ranking neutro entre concorrentes contradiz o interesse de quem vende uma máquina. Marketplace exige taxas reais com fonte e data |
| D-013 | Fora do MVP: links de afiliado, comparação por marca real, coleta automática de taxas | Proposta | 08/11 | Programas de afiliado ainda não foram confirmados; taxas reais envelhecem e exigem fonte. Podem aparecer no pitch como próximos passos |
| D-015 | Botão "Login" e assistente de chat do protótipo ficam. "Login" vira "Entrar na demonstração", com escolha entre Agente e Matriz (sem cadastro nem senha). O chat é ajuda com respostas prontas, sem LLM e sem calcular nada | Decidida (Felipe deixou a critério do agente, 17/11) | 17/11 | Mantém o design da Amanda sem sair do MVP, que não tem login real e tem dois perfis de demonstração. Texto gerado por LLM continua sendo extra opcional no fim (`docs/PRODUTO.md`) |
| D-016 | Catálogo da demo com marcas fictícias | Decidida (Felipe, 17/11) | 17/11 | O time pensou em nomes parecidos com marcas reais (ex.: "InfinitoPay"). Recomendação do agente: nomes que não lembrem nenhuma marca real, porque nome parecido com taxa inventada pode ser lido como dado real da marca e pode gerar problema de marca registrada. Nome final em aberto |
| D-017 | Valores dos cards da landing (perfis mercadinho, salão e loja) vêm do simulador do Kayke. Até o simulador existir, ficam os valores do protótipo da Amanda, marcados como ilustrativos | Decidida (Felipe, 17/11) | 17/11 | Evita número escrito à mão que contradiz o cálculo da tela de resultado |
| D-018 | Telas que faltam no Figma (painel da matriz, botão de ditado, tela de resultado) são feitas pelo time seguindo a estética do protótipo (cores, fontes, ilustrações) | Decidida (Felipe, 17/11) | 17/11 | Não trava o código esperando novo design |
| D-019 | Contrato v1: a consulta só exige CNPJ e faturamento (os dois campos do formulário da landing). Mix, ticket, prazo e taxas atuais são opcionais. Sem mix ou sem taxas atuais, `economia` vem `null` e a tela convida a completar o perfil | Proposta (aguarda aprovação de Felipe, Guilherme e Kayke no PR do contrato, #12) | 17/11 | O protótipo do Figma só pede CNPJ e faturamento. Assumir um mix padrão seria inventar dado do comerciante. Alternativa: usar o perfil de exemplo escolhido nas abas da landing (mercadinho, salão, loja) como mix, marcado como ilustrativo |

## Como registrar

Nova decisão entra aqui no mesmo PR da mudança. Não apague decisões antigas: marque como substituídas e aponte para a nova.
