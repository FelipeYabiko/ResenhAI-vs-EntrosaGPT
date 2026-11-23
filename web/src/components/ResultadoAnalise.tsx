// Agent's result screen (issue #22, T-13): shows exactly what POST /v1/consultas returned.
// Structure and texts only; the Figma layout comes later. Nothing here computes a value:
// every number comes from the API (or from the labelled example), never from the browser.
import type { ConsultaResultado } from "@/lib/api";
import { mascararCnpj } from "@/lib/cnpj";
import { formatarData, formatarPercentual, formatarReais } from "@/lib/formato";
import { EnviarProposta } from "./EnviarProposta";
import estilos from "./ResultadoAnalise.module.css";

type Fonte = ConsultaResultado["fontes"][number];
type Economia = NonNullable<ConsultaResultado["economia"]>;

const NOMES_DAS_FONTES: Record<string, string> = {
  cnpj_publico: "Dados públicos do CNPJ",
  bcb_inadimplencia_pj: "Banco Central: inadimplência de empresas",
};

function descreverFonte(fonte: Fonte): string {
  const data = fonte.atualizado_em ? `dado de ${formatarData(fonte.atualizado_em)}` : "sem data";
  if (fonte.status === "indisponivel") return "indisponível no momento";
  if (fonte.status === "cache") return `fonte fora do ar, mostrando o último dado guardado (${data})`;
  return data;
}

function contribuicao(pontos: number): string {
  return `${pontos > 0 ? "+" : ""}${pontos} ${Math.abs(pontos) === 1 ? "ponto" : "pontos"}`;
}

export function ResultadoAnalise({ resultado, exemplo }: { resultado: ConsultaResultado; exemplo: boolean }) {
  const { empresa, fontes, pontuacao, recomendacao, economia, benchmark_mercado: benchmark, aviso } = resultado;

  return (
    <article className={estilos.resultado} aria-labelledby="titulo-resultado">
      <h1 id="titulo-resultado" tabIndex={-1}>
        {exemplo ? "Exemplo de resultado" : "Resultado da análise"}
      </h1>

      {exemplo && (
        <p className={estilos.exemplo}>
          <strong>Exemplo ilustrativo.</strong> Estes números não vêm de uma consulta: mostram como a tela fica
          enquanto a análise completa está em construção. A empresa é fictícia.
        </p>
      )}

      <p className={estilos.aviso}>
        <strong>{aviso}</strong> Limite, taxas e economia são estimativas para conversa com o comerciante.
      </p>

      <section aria-labelledby="titulo-economia" className={estilos.bloco}>
        <h2 id="titulo-economia">Economia estimada</h2>
        <BlocoEconomia economia={economia} />
      </section>

      <section aria-labelledby="titulo-risco" className={estilos.bloco}>
        <h2 id="titulo-risco">Faixa de risco</h2>
        <p className={estilos.destaque}>
          Faixa {pontuacao.faixa} <span className={estilos.detalhe}>({pontuacao.pontos} de 100 pontos)</span>
        </p>
        <p className={estilos.detalhe}>Escala de A a E, calculada por regras explicadas abaixo.</p>
        {pontuacao.fatores.length > 0 ? (
          <>
            <h3>O que pesou no resultado</h3>
            <ul>
              {pontuacao.fatores.map((fator) => (
                <li key={fator.regra}>
                  {fator.explicacao}: <strong>{contribuicao(fator.contribuicao)}</strong>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p>Nenhum fator foi informado pela análise.</p>
        )}
      </section>

      <section aria-labelledby="titulo-recomendacao" className={estilos.bloco}>
        <h2 id="titulo-recomendacao">
          Recomendação <span className="selo">Simulação</span>
        </h2>
        <dl className={estilos.lista}>
          <div>
            <dt>Máquina indicada</dt>
            <dd>
              {recomendacao.maquina.modelo}
              {recomendacao.maquina.motivo && <span className={estilos.detalhe}>. {recomendacao.maquina.motivo}</span>}
            </dd>
          </div>
          <div>
            <dt>Limite de crédito simulado</dt>
            <dd>{formatarReais(recomendacao.limite_credito_simulado)}</dd>
          </div>
          <div>
            <dt>Taxa de antecipação simulada</dt>
            <dd>{formatarPercentual(recomendacao.taxas_antecipacao_simuladas.mensal_percentual)} ao mês</dd>
          </div>
        </dl>
      </section>

      <section aria-labelledby="titulo-mercado" className={estilos.bloco}>
        <h2 id="titulo-mercado">Referência de mercado</h2>
        {benchmark.disponivel ? (
          <p>
            {benchmark.referencia}
            {benchmark.data_referencia && `, dado de ${formatarData(benchmark.data_referencia)}`}. É uma média
            agregada, não a taxa de uma operadora.
          </p>
        ) : (
          <p>Referência do Banco Central indisponível nesta consulta.</p>
        )}
      </section>

      <section aria-labelledby="titulo-empresa" className={estilos.bloco}>
        <h2 id="titulo-empresa">Empresa</h2>
        <dl className={estilos.lista}>
          <div>
            <dt>CNPJ</dt>
            <dd>{mascararCnpj(empresa.cnpj)}</dd>
          </div>
          <div>
            <dt>Nome</dt>
            <dd>{empresa.nome ?? "Não exibido (MEI ou empresário individual, por privacidade)"}</dd>
          </div>
          <div>
            <dt>Situação cadastral</dt>
            <dd>{empresa.situacao}</dd>
          </div>
          <div>
            <dt>Atividade principal (CNAE)</dt>
            <dd>{empresa.cnae_principal}</dd>
          </div>
          <div>
            <dt>Porte</dt>
            <dd>{empresa.porte}</dd>
          </div>
          <div>
            <dt>Aberta em</dt>
            <dd>{formatarData(empresa.abertura)}</dd>
          </div>
          <div>
            <dt>Capital social</dt>
            <dd>{formatarReais(empresa.capital_social)}</dd>
          </div>
          <div>
            <dt>Município</dt>
            <dd>{empresa.municipio_uf}</dd>
          </div>
        </dl>
      </section>

      <section aria-labelledby="titulo-fontes" className={estilos.bloco}>
        <h2 id="titulo-fontes">Fontes</h2>
        {fontes.length > 0 ? (
          <ul>
            {fontes.map((fonte) => (
              <li key={fonte.nome}>
                {NOMES_DAS_FONTES[fonte.nome] ?? fonte.nome}: {descreverFonte(fonte)}
              </li>
            ))}
          </ul>
        ) : (
          <p>A análise não informou fontes.</p>
        )}
        <p className={estilos.detalhe}>Análise feita em {(resultado.tempo_ms / 1000).toLocaleString("pt-BR")} s.</p>
      </section>

      <section aria-labelledby="titulo-proposta" className={estilos.bloco}>
        <h2 id="titulo-proposta">Enviar proposta à matriz</h2>
        {exemplo ? (
          <p>No exemplo ilustrativo não é possível enviar proposta. Faça uma consulta para enviar.</p>
        ) : (
          <EnviarProposta consultaId={resultado.consulta_id} />
        )}
      </section>
    </article>
  );
}

function BlocoEconomia({ economia }: { economia: Economia | null }) {
  if (!economia) {
    return (
      <p>
        Sem o mix de pagamento e as taxas que o comerciante paga hoje, não dá para comparar custos. Nenhuma economia foi
        estimada.
      </p>
    );
  }

  const custos = (
    <dl className={estilos.lista}>
      <div>
        <dt>Custo mensal hoje (estimativa do comerciante)</dt>
        <dd>{formatarReais(economia.custo_mensal_atual)}</dd>
      </div>
      <div>
        <dt>Custo mensal com a oferta</dt>
        <dd>{formatarReais(economia.custo_mensal_oferta)}</dd>
      </div>
    </dl>
  );

  if (economia.economia_mensal <= 0) {
    return (
      <>
        <p className={estilos.destaque}>Com esses dados, a oferta não reduz o custo mensal.</p>
        {custos}
      </>
    );
  }

  const meses = economia.meses_para_compensar_saida;
  return (
    <>
      <p className={estilos.destaque}>
        {formatarReais(economia.economia_mensal)} por mês{" "}
        <span className={estilos.detalhe}>({formatarReais(economia.economia_anual)} por ano)</span>
      </p>
      {custos}
      {meses === null && <p>Com esses dados, a economia não compensa o custo de saída informado.</p>}
      {meses !== null && meses > 0 && (
        <p>
          A economia compensa o custo de saída em {meses} {meses === 1 ? "mês" : "meses"}.
        </p>
      )}
      <p className={estilos.detalhe}>Estimativa feita com os dados informados pelo comerciante.</p>
    </>
  );
}
