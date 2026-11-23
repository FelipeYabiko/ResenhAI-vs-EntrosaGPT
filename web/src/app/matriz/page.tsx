import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { PainelMatriz } from "@/components/PainelMatriz";
import mascoteLogo from "../../../public/img/mascote-logo.png";
import estilos from "../page.module.css";

export const metadata: Metadata = {
  title: "Painel da matriz | CredFácil",
  description: "Propostas simuladas chegando ao vivo para análise. Simulação, não é oferta de crédito.",
};

export default function PaginaMatriz() {
  return (
    <>
      <header className={estilos.cabecalho}>
        <div className={`container ${estilos.barra}`}>
          <Link href="/" className={estilos.marca}>
            <Image src={mascoteLogo} alt="" width={36} height={42} priority />
            CredFácil
          </Link>
          <nav aria-label="Principal" className={estilos.navegacao}>
            <Link href="/#analise">Área do agente</Link>
          </nav>
        </div>
      </header>

      <main id="conteudo" className="container">
        <PainelMatriz />
      </main>

      <footer className={`fundo-escuro ${estilos.avisos}`}>
        <div className="container">
          <p>
            <strong>Simulação. Não é oferta de crédito.</strong> Propostas, decisões e contratos desta tela são de
            demonstração.
          </p>
        </div>
      </footer>
    </>
  );
}
