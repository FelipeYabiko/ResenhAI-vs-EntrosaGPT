// Serves the static export in `out/` like Netlify does (/matriz -> matriz.html), for local checks
// and the Playwright tests. No dependency. Usage: node scripts/servir.mjs [port]
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";

const PASTA = join(import.meta.dirname, "..", "out");
const PORTA = Number(process.argv[2] ?? 3000);
const TIPOS = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript",
  ".css": "text/css",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".ico": "image/x-icon",
  ".json": "application/json",
  ".txt": "text/plain; charset=utf-8",
};

function arquivoPara(caminho) {
  const limpo = normalize(decodeURIComponent(caminho.split("?")[0])).replace(/^(\.\.[/\\])+/, "");
  for (const candidato of [limpo, `${limpo}.html`, join(limpo, "index.html")]) {
    const completo = join(PASTA, candidato);
    if (completo.startsWith(PASTA) && existsSync(completo) && statSync(completo).isFile()) return completo;
  }
  return null;
}

createServer((pedido, resposta) => {
  const arquivo = arquivoPara(pedido.url ?? "/") ?? join(PASTA, "404.html");
  const status = arquivo.endsWith("404.html") && !pedido.url?.startsWith("/404") ? 404 : 200;
  resposta.writeHead(status, { "Content-Type": TIPOS[extname(arquivo)] ?? "application/octet-stream" });
  createReadStream(arquivo).pipe(resposta);
}).listen(PORTA, () => console.log(`Site estático em http://localhost:${PORTA}`));
