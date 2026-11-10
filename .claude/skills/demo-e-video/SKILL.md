---
name: demo-e-video
description: Use para preparar dados de demonstração, roteiro, ensaio ou gravação do vídeo de até 3 minutos do CredFácil. Garante que o vídeo mostra o produto funcionando, sem dado real e sem promessas falsas.
---

# Demo e vídeo

Leia `docs/DEMO.md` e `docs/PRODUTO.md`.

## Regras do evento

- Vídeo de até 3 minutos, acessível sem login, **mostrando o produto funcionando**. Inglês é preferido, português é aceito.
- Todos os integrantes aparecem no vídeo (exigência do painel do evento).
- A demo roda no ambiente publicado, em HTTPS, e fica no ar até 15/12.
- Nenhum dado pessoal real de terceiros na tela.

## Passos

1. Escolha 3 CNPJs de `fixtures/cnpjs_demo.json` com resultados diferentes (faixa boa, intermediária, recusada).
2. Aqueça o cache antes de gravar. A fonte de CNPJ limita 5 consultas por minuto por IP.
3. Ensaie o fluxo completo duas vezes no ambiente publicado.
4. Teste a voz no microfone da gravação. Tenha a digitação como plano B.
5. Confira cada passo do roteiro: o que não está pronto não aparece como se estivesse.
6. Verifique que o aviso "Simulação" aparece nas telas filmadas e que não há aba, chave ou dado pessoal visível.

## Linguagem

- Pode dizer: "simulação", "regras explicáveis", "dados públicos de empresas", "premissas do time".
- Não diga: "pré-aprovado de verdade", "modelo preciso", "IA prevê o risco", "tempo real" para dados de fonte pública (há cache e defasagem), nem número de impacto sem fonte.

## Saída

Entregue a sequência de dados de exemplo, a lista de verificação marcada e os pontos do roteiro que ainda dependem de funcionalidade não pronta.
