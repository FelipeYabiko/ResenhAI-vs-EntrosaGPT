import Image from "next/image";
import { FormularioAnalise } from "@/components/FormularioAnalise";
import { InterruptorMovimento } from "@/components/InterruptorMovimento";
import { EXEMPLOS } from "@/lib/exemplos";
import { formatarReais } from "@/lib/formato";
import cartoes from "../../public/img/cartoes.png";
import maquininhasGrande from "../../public/img/maquininhas-laranja-grande.png";
import maquininhas from "../../public/img/maquininhas-laranja.png";
import mascoteAcenando from "../../public/img/mascote-acenando.png";
import mascoteEncaminhando from "../../public/img/mascote-encaminhando.png";
import mascoteLogo from "../../public/img/mascote-logo.png";
import estilos from "./page.module.css";

const PASSOS = [
  {
    titulo: "Consulte",
    texto: "Informe o CNPJ e uma estimativa de faturamento do negócio.",
    imagem: cartoes,
  },
  {
    titulo: "Entenda",
    texto: "Veja informações de crédito e compare custos simulados das maquininhas.",
    imagem: maquininhas,
  },
  {
    titulo: "Encaminhe",
    texto: "Leve a proposta para a equipe avaliar. A decisão vem depois da análise.",
    imagem: mascoteEncaminhando,
  },
];

const PRINCIPIOS = [
  { titulo: "Regras explicadas", texto: "Você entende o que está sendo comparado, sem letras miúdas." },
  {
    titulo: "Simulação, sempre",
    texto: "Valores estimados ficam identificados. Nada aqui é uma oferta real.",
  },
  { titulo: "Feito para ir com você", texto: "No celular do vendedor, do balcão à próxima visita." },
];

export default function Inicio() {
  return (
    <>
      <header className={estilos.cabecalho}>
        <div className={`container ${estilos.barra}`}>
          <a href="#conteudo" className={estilos.marca}>
            <Image src={mascoteLogo} alt="" width={36} height={42} priority />
            CredFácil
          </a>
          <nav aria-label="Principal" className={estilos.navegacao}>
            <a href="#como-funciona">Como funciona</a>
            <a href="#comparar">Comparar</a>
            <a href="#analise" className="botao botao-marinho">
              Fazer análise
            </a>
          </nav>
        </div>
      </header>

      <main id="conteudo">
        <section className={`container ${estilos.hero}`} aria-labelledby="titulo-principal">
          <div className={estilos.heroTexto}>
            <p className="sobretitulo">Crédito + maquininhas, sem complicação</p>
            <h1 id="titulo-principal">Mais clareza para decidir. Mais oportunidades para crescer.</h1>
            <p className={estilos.heroResumo}>
              Consulte pelo CNPJ, entenda as possibilidades de crédito e compare taxas de maquininhas. Tudo em uma
              conversa simples.
            </p>
            <a href="#analise" className="botao botao-laranja">
              Fazer uma análise
            </a>
            <p className={estilos.semPromessa}>Sem promessa de crédito. Com informação.</p>
          </div>
          <div className={estilos.heroImagem}>
            <Image src={mascoteAcenando} alt="" priority sizes="(min-width: 860px) 420px, 70vw" />
          </div>
        </section>

        <section id="analise" className={`container ${estilos.analise}`} aria-labelledby="titulo-analise">
          <h2 id="titulo-analise">
            Seu próximo passo começa <span className={estilos.destaque}>aqui</span>.
          </h2>
          <FormularioAnalise />
        </section>
        <div className={`container ${estilos.movimento}`}>
          <InterruptorMovimento />
        </div>

        <section id="como-funciona" className={`container ${estilos.secao}`} aria-labelledby="titulo-passos">
          <p className="sobretitulo">Do CNPJ à próxima conversa</p>
          <h2 id="titulo-passos">É simples. E você entende cada passo.</h2>
          <ol className={estilos.passos}>
            {PASSOS.map((passo, i) => (
              <li key={passo.titulo} className={estilos.passo}>
                <div className={estilos.passoTopo}>
                  <span className={estilos.numero} aria-hidden="true">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <Image src={passo.imagem} alt="" className={estilos.passoImagem} sizes="88px" />
                </div>
                <h3>{passo.titulo}</h3>
                <p>{passo.texto}</p>
              </li>
            ))}
          </ol>
        </section>

        <section id="comparar" className={`fundo-escuro ${estilos.comparar}`} aria-labelledby="titulo-comparar">
          <div className="container">
            <p className="sobretitulo">Compare antes de escolher</p>
            <h2 id="titulo-comparar">Menos taxas. Mais fôlego.</h2>
            {EXEMPLOS.map((exemplo) => {
              const economia = exemplo.custoAtualMensal - exemplo.custoRecomendadoMensal;
              return (
                <div key={exemplo.id} className={estilos.exemplo}>
                  <h3 className={estilos.perfil}>Exemplo: {exemplo.perfil}</h3>
                  <ul className={estilos.cartoes}>
                    <li className={`${estilos.cartao} ${estilos.cartaoCreme}`}>
                      <h4>Taxa de balcão</h4>
                      <p className={estilos.legenda}>Plano padrão • exemplo fictício</p>
                      <p className={estilos.valor}>
                        {formatarReais(exemplo.custoAtualMensal, { centavos: false })}
                        <span>/mês</span>
                      </p>
                      <span className="selo">Simulação</span>
                    </li>
                    <li className={`${estilos.cartao} ${estilos.cartaoCeleste}`}>
                      <h4>Opção recomendada</h4>
                      <p className={estilos.legenda}>Plano comparado • exemplo fictício</p>
                      <p className={estilos.valor}>
                        {formatarReais(exemplo.custoRecomendadoMensal, { centavos: false })}
                        <span>/mês</span>
                      </p>
                      <span className="selo">Simulação</span>
                    </li>
                    <li className={`${estilos.cartao} ${estilos.cartaoLaranja}`}>
                      <h4>Resultado</h4>
                      <p className={estilos.legenda}>Você pode economizar</p>
                      <p className={estilos.valor}>
                        {formatarReais(economia, { centavos: false })}
                        <span>/mês neste exemplo</span>
                      </p>
                      <span className="selo">Simulação</span>
                    </li>
                  </ul>
                  <p className={estilos.notaTaxas}>
                    Taxas ilustrativas: {exemplo.taxaAtual} → {exemplo.taxaRecomendada}.
                  </p>
                </div>
              );
            })}
            <p className={estilos.notaPequena}>
              Exemplos fictícios, não são taxas de uma operadora. Mesma base de vendas em cada comparação; sem
              aluguel de máquina nem antecipação.
            </p>
          </div>
        </section>

        <section className={`container ${estilos.secao}`} aria-labelledby="titulo-regras">
          <h2 id="titulo-regras">Informação boa não esconde as regras.</h2>
          <ul className={estilos.principios}>
            {PRINCIPIOS.map((p) => (
              <li key={p.titulo} className={estilos.principio}>
                <h3>{p.titulo}</h3>
                <p>{p.texto}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className={estilos.chamada} aria-labelledby="titulo-chamada">
          <div className={`container ${estilos.chamadaGrade}`}>
            <div className={estilos.chamadaTexto}>
              <p className="sobretitulo">Vamos conversar sobre o seu negócio?</p>
              <h2 id="titulo-chamada">Seu negócio merece um próximo passo claro.</h2>
              <p>Encaminhe as informações para uma avaliação humana. Sem promessa, sem pressão.</p>
              <a href="#analise" className="botao botao-marinho">
                Encaminhar para análise
              </a>
            </div>
            <Image
              src={maquininhasGrande}
              alt=""
              className={estilos.chamadaImagem}
              sizes="(min-width: 860px) 420px, 90vw"
            />
          </div>
        </section>
      </main>

      <footer className={estilos.rodape}>
        <div className={`container ${estilos.rodapeGrade}`}>
          <div>
            <p className={estilos.marca}>
              <Image src={mascoteLogo} alt="" width={36} height={42} />
              CredFácil
            </p>
            <p className={estilos.lema}>Informação que aproxima.</p>
            <p>Crédito e maquininhas em uma conversa simples, para quem está no campo ou no balcão.</p>
          </div>
          <nav aria-label="Rodapé">
            <h2 className={estilos.rodapeTitulo}>Explore</h2>
            <ul className={estilos.rodapeLinks}>
              <li>
                <a href="#como-funciona">Como funciona</a>
              </li>
              <li>
                <a href="#comparar">Comparar maquininhas</a>
              </li>
              <li>
                <a href="#analise">Fazer uma análise</a>
              </li>
            </ul>
          </nav>
        </div>
        <div className={`fundo-escuro ${estilos.avisos}`}>
          <div className="container">
            <p>
              <strong>Simulação. Não é oferta de crédito.</strong> Valores estimados e simulados; a aprovação depende
              da análise da equipe.
            </p>
            <p>Protótipo demonstrativo: os exemplos não representam taxas reais de nenhuma operadora.</p>
            <p>Hack Brasil 2026 • Informação que aproxima.</p>
          </div>
        </div>
      </footer>
    </>
  );
}
