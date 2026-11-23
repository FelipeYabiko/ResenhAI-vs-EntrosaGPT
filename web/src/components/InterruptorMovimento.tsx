"use client";

import { useSyncExternalStore } from "react";
import estilos from "./InterruptorMovimento.module.css";

const CHAVE = "credfacil-movimento";
const EVENTO = "credfacil-movimento";
const consultaSistema = "(prefers-reduced-motion: reduce)";

function reduzido(): boolean {
  const escolha = document.documentElement.dataset.movimento;
  if (escolha) return escolha === "reduzido";
  return window.matchMedia(consultaSistema).matches;
}

function assinar(avisar: () => void) {
  const midia = window.matchMedia(consultaSistema);
  midia.addEventListener("change", avisar);
  window.addEventListener(EVENTO, avisar);
  return () => {
    midia.removeEventListener("change", avisar);
    window.removeEventListener(EVENTO, avisar);
  };
}

/** "Reduzir movimento" switch from the prototype. Starts from the OS setting; the choice is remembered. */
export function InterruptorMovimento() {
  const ligado = useSyncExternalStore(assinar, reduzido, () => false);

  function alternar(marcado: boolean) {
    const valor = marcado ? "reduzido" : "normal";
    document.documentElement.dataset.movimento = valor;
    try {
      localStorage.setItem(CHAVE, valor);
    } catch {
      // Private mode or blocked storage: the choice still applies to this visit.
    }
    window.dispatchEvent(new Event(EVENTO));
  }

  return (
    <label className={estilos.interruptor}>
      <input
        type="checkbox"
        checked={ligado}
        onChange={(e) => alternar(e.target.checked)}
      />
      Reduzir movimento
    </label>
  );
}
