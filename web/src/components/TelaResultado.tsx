"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useSyncExternalStore } from "react";
import { lerConsulta } from "@/lib/consulta-salva";
import { RESULTADO_EXEMPLO } from "@/lib/exemplo-resultado";
import { ResultadoAnalise } from "./ResultadoAnalise";

const semMudancas = () => () => {};
const noServidor = () => undefined;

export function TelaResultado() {
  const exemplo = useSearchParams().has("exemplo");
  // The saved result lives in the browser (lib/consulta-salva). On the server and in the first render
  // it is `undefined` ("carregando"), so the HTML from the server matches the first client render.
  const salvo = useSyncExternalStore(semMudancas, lerConsulta, noServidor);
  const resultado = exemplo ? RESULTADO_EXEMPLO : salvo;
  const bloco = useRef<HTMLDivElement>(null);

  // A new page: move the focus to its title, so keyboard and screen reader users start from the top.
  const pronto = resultado !== undefined;
  useEffect(() => {
    if (pronto) bloco.current?.querySelector("h1")?.focus();
  }, [pronto, exemplo]);

  if (resultado === undefined) return <p role="status">Carregando o resultado…</p>;

  if (resultado === null) {
    return (
      <div ref={bloco} style={{ display: "grid", gap: 16, paddingBlock: 32 }}>
        <h1 tabIndex={-1}>Nenhum resultado para mostrar</h1>
        <p>O resultado aparece aqui depois de uma consulta feita nesta aba.</p>
        <p>
          <Link href="/#analise">Fazer uma consulta</Link> ou{" "}
          <Link href="/resultado?exemplo">ver um exemplo ilustrativo</Link>.
        </p>
      </div>
    );
  }

  return (
    <div ref={bloco}>
      <ResultadoAnalise resultado={resultado} exemplo={exemplo} />
    </div>
  );
}
