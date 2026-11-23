import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Suspense } from "react";
import { TelaResultado } from "@/components/TelaResultado";
import mascoteLogo from "../../../public/img/mascote-logo.png";
import estilos from "../page.module.css";

export const metadata: Metadata = {
  title: "Resultado da análise | CredFácil",
  description: "Resultado simulado da análise de crédito e de custo de maquininha. Simulação, não é oferta de crédito.",
};

export default function PaginaResultado() {
  return (
    <>
      <header className={estilos.cabecalho}>
        <div className={`container ${estilos.barra}`}>
          <Link href="/" className={estilos.marca}>
            <Image src={mascoteLogo} alt="" width={36} height={42} priority />
            CredFácil
          </Link>
          <nav aria-label="Principal" className={estilos.navegacao}>
            <Link href="/#analise" className="botao botao-marinho">
              Nova consulta
            </Link>
          </nav>
        </div>
      </header>

      <main id="conteudo" className="container">
        {/* TelaResultado reads the address (?exemplo), which only exists in the browser. */}
        <Suspense fallback={<p role="status">Carregando o resultado…</p>}>
          <TelaResultado />
        </Suspense>
      </main>

      <footer className={`fundo-escuro ${estilos.avisos}`}>
        <div className="container">
          <p>
            <strong>Simulação. Não é oferta de crédito.</strong> Valores estimados e simulados; a aprovação depende da
            análise da equipe.
          </p>
        </div>
      </footer>
    </>
  );
}
