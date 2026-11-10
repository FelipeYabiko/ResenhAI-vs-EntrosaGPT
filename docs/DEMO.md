# Demo e vídeo

Rascunho para a Amanda e o time ajustarem. Regras do evento: vídeo de até 3 minutos, acessível sem login, mostrando o produto funcionando, em português ou inglês (inglês é preferido).

## Roteiro de 3 minutos (proposta)

| Tempo | O que aparece | O que dizemos |
| --- | --- | --- |
| 0:00 a 0:30 | Gancho: o vendedor dita um CNPJ e o resultado aparece em segundos, com a economia em reais por mês (dado de exemplo, dito como exemplo). Depois, o comerciante e o problema | Quem sofre com a demora para ter máquina e crédito, e por quê |
| 0:30 a 2:00 | Produto funcionando: consulta, resultado com fatores, envio da proposta, a matriz recebendo ao vivo, aprovação, contrato simulado | O fluxo completo, com o aviso de simulação visível |
| 2:00 a 2:40 | Por dentro: fontes públicas, regras explicáveis, eventos em tempo real, acessibilidade | Por que regras e não caixa-preta; como cuidamos de dados e privacidade |
| 2:40 a 3:00 | Impacto e próximos passos | Segundos até a proposta, menos campos digitados; próximos passos como mock |

O que mostrar de acessibilidade: voz, alto contraste e navegação com teclado ou leitor de tela, por 15 a 20 segundos.

## Dados da demo

- Só CNPJs de `fixtures/cnpjs_demo.json`. Escolha 3 com resultados diferentes (faixa boa, intermediária, recusada por situação cadastral).
- Faturamentos de exemplo marcados como exemplo.
- Aquecer o cache antes de gravar (a fonte de CNPJ limita 5 consultas por minuto).
- Conferir no ambiente publicado, não só no computador local.

## Antes de gravar

- [ ] Demo publicada, HTTPS, sem "primeiro acesso lento"
- [ ] Fluxo completo ensaiado 2 vezes
- [ ] Voz testada no navegador e no microfone da gravação, com digitação como plano B
- [ ] Nenhum dado real de pessoa, nenhuma chave ou aba com dado pessoal visível
- [ ] Aviso "Simulação" visível nas telas filmadas
- [ ] Todos os integrantes aparecem no vídeo (exigência do painel do evento)
- [ ] Legendas ou texto em tela para o que for dito em inglês
- [ ] O que não está pronto não aparece como se estivesse

## Ao descrever o produto, diga e não diga

- Diga: "simulação", "regras explicáveis", "dados públicos de empresas", "premissas do time".
- Não diga: "pré-aprovado de verdade", "modelo preciso", "inteligência artificial prevê o risco" (a pontuação é por regras), "dados em tempo real" (há cache e defasagem).
- Não cite número de impacto sem fonte. A economia em reais da demo é exemplo, não resultado medido.
- Não mostre taxas de marcas reais de maquininha, a menos que cada uma tenha fonte e data na tela.
