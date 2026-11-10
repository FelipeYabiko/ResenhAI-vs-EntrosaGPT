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

## Como registrar

Nova decisão entra aqui no mesmo PR da mudança. Não apague decisões antigas: marque como substituídas e aponte para a nova.
