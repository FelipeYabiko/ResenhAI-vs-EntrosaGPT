# Contexto do projeto

Contexto estável do projeto. O que muda ao longo do tempo (decisões, perguntas em aberto, próximos passos) fica em `docs/STATUS.md`.

Última revisão: 06/11/2026.

## Resumo

Time de 4 pessoas no Hack Brasil 2026, hackathon nacional online (4 a 30 de novembro) com final presencial em São Paulo. O projeto é o **CredFácil**, na trilha Pagamentos & finanças (ver `docs/PRODUTO.md` e `docs/STATUS.md`).

## Regras do evento que afetam decisões técnicas

Fonte: [regulamento](https://hackbrasil.com/regulamento) (versão de 02/11/2026) e e-mail da organização. As regras podem mudar. Em caso de conflito, vale o regulamento. Dúvidas: oi@hackbrasil.com.

### Prazos

| Data | O que acontece |
| --- | --- |
| 30/11 às 23h59 | Fim das submissões. Vale a última versão enviada dentro do prazo |
| 02/12 | Finalistas anunciados |
| 04/12 às 23h59 | Finalistas confirmam presença |
| 12/12 | Final presencial no Google Brasil, em São Paulo. Todos os integrantes presentes. Viagem e hospedagem por conta de cada um |
| 15/12 | Os repositórios precisam continuar públicos até esta data |

### Entrega e avaliação

- **Entrega:** repositório público no GitHub, demo funcionando (precisa ficar no ar durante a avaliação) e vídeo de até 3 minutos, acessível sem login, em português ou inglês (de preferência inglês).
- **Avaliação:** quatro critérios com o mesmo peso. Execução técnica (o produto funciona e está completo?), implementação técnica (arquitetura, qualidade do código, escolha e uso das tecnologias), impacto e comunicação (vídeo na fase online, apresentação na final).
- **Desempate:** maior nota em execução técnica, depois em impacto.
- **Final:** os 5 melhores projetos elegíveis de cada trilha.

### Código e repositório

- Repositório novo, criado depois do fim da sessão de abertura (04/11 às 21h), com todos os commits a partir daí. Repositório antigo ou com histórico importado desclassifica. O e-mail da organização cita 19h; criar depois das 21h cobre as duas versões.
- Pode continuar uma ideia anterior, mas código anterior ao evento não pode ser copiado. Exceção: código aberto que já era público (bibliotecas, frameworks, starter kits).
- Licença open source é recomendada, não exigida. Licença ou restrição que impeça os jurados de ler, executar e testar o código desclassifica o projeto.
- Tecnologias livres. Nenhuma ferramenta de patrocinador é exigida nem dá nota extra. IA (agentes, copilotos, modelos de linguagem) é permitida e recomendada.
- A demo não pode expor dados pessoais reais de terceiros. Finanças: ambientes de teste ou simulação.

### Trilhas

Cada projeto concorre em uma só trilha. O problema e o público do projeto precisam estar dentro dela. Citar o tema não basta. O enquadramento é condição para concorrer, não nota.

| Trilha | O que cabe (resumo) | Fora do escopo (resumo) |
| --- | --- | --- |
| Pagamentos & finanças | Infraestrutura de pagamentos, agentes financeiros, gestão financeira pessoal e de pequenas empresas, acesso a crédito | Apostas e jogos de azar, rendimento garantido, pirâmide, manipulação de mercado, emissão de tokens para captar dinheiro |
| Logística & automação | Integrações entre sistemas, automação de fluxos de trabalho, roteirização, estoque e cadeia de suprimentos | Spam, contas falsas, burla de captcha ou de limites de plataformas, coleta que viole termos do site ou exponha dados pessoais |
| Saúde & bem-estar | Triagem, busca de serviços de saúde, saúde mental, atividade física, sono e nutrição | Diagnóstico ou prescrição automáticos no lugar de profissional, venda de medicamento sem prescrição, dados reais de pacientes |
| Acesso à educação | Ferramentas de ensino e aprendizado, assistentes de estudo, tradução e adaptação de conteúdo, apoio a professores e escolas | Assistentes de uso geral sem foco em aprendizado, ferramentas para colar em prova ou burlar detector de plágio |
| Cultura & economia criativa | Ferramentas para artistas e criadores, música, audiovisual, comunidades criativas, formas de remunerar quem cria | Publicidade e marketing em geral, bots de engajamento, obras de terceiros sem autorização |
| Cibersegurança | Detecção de fraude e phishing, privacidade, gestão de identidade e acesso, monitoramento | Malware, exploits, ferramentas para invadir ou espionar |
| Meio ambiente & economia verde | Créditos de carbono, reciclagem, energia renovável, monitoramento ambiental, eficiência energética e hídrica | Projeto em que o tema ambiental é só rótulo |

Existe também uma lista de temas proibidos no FAQ do site, que ainda não foi lida na íntegra (ver `docs/STATUS.md`).

## Time

Quatro pessoas: Felipe, Guilherme, Kayke e Amanda. Comunicação pelo grupo "Hack BR" no Discord.

| Pessoa | Perfil | Papel proposto (a confirmar) |
| --- | --- | --- |
| Felipe | Automação, dados e integrações em Python, liderança de time | Tech lead, arquitetura, back-end e integrações |
| Guilherme | Desenvolvimento full-stack | Full-stack, reforça front ou back conforme a ideia |
| Kayke | Dados e ML, experiência com crédito | Dados e ML |
| Amanda | Front-end, UX/UI e design | UX/UI, front-end, pitch e vídeo |

Parte do time tem disponibilidade limitada em dias úteis. O ritmo proposto é assíncrono durante a semana e síncrono no fim de semana.

## Créditos oferecidos pelo evento

Depois que o rascunho inicial for aprovado, cada integrante recebe códigos próprios na aba "Benefícios" do painel: cupom de US$ 20 no plano Devin Pro (Cognition) e 5 mil créditos do Firecrawl.

Rascunho inicial, enviado pelo painel do time:

1. Cada pessoa aceita os termos e informa cidade e UF em "Meus dados".
2. Escolher a trilha.
3. Repositório público novo, com README descrevendo o que será construído.
4. Vídeo de cerca de 3 minutos com todas as pessoas do time aparecendo (público ou não listado).
5. Página pública do projeto em HTTPS (pode ser um protótipo inicial).
6. "Verificar e enviar". O rascunho não substitui a submissão final.

Como usar:

- **Devin:** tarefas delimitadas, com critério de aceite, sempre via PR com revisão humana. O plano Pro tem cota diária e semanal de uso, e passar dela é pago à parte.
- **Firecrawl:** 1 crédito por página raspada ou rastreada, 2 créditos por 10 resultados de busca, +4 créditos por página com extração em JSON. Uso previsto: baixar documentação (Banco Central, API de CNPJ, WCAG) em markdown para dar contexto aos agentes. Não use para coletar dados de empresas ou de pessoas, e não vale forçar o uso dentro do produto.

## Domínio (resumo)

Detalhes e fontes em `docs/RESEARCH.md` (feita antes da escolha da ideia; ver a nota no topo do arquivo).

- Inadimplência em nível recorde: 84,2 milhões de pessoas e 9,3 milhões de empresas negativadas (Serasa), quase todas micro e pequenas.
- O Pix Automático abriu a cobrança recorrente para qualquer empresa, mas a adoção ainda é inicial.
- 82% dos pequenos negócios que vendem on-line usam o WhatsApp, e o crédito para eles está restrito.
- Cerca de metade dos pequenos negócios já usa IA, quase sempre em marketing.
- O custo logístico brasileiro é de 15,5% do PIB (2025), quase o dobro do dos EUA.
