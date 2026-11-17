import type { Metadata, Viewport } from "next";
import "@fontsource/outfit/400.css";
import "@fontsource/outfit/600.css";
import "@fontsource/outfit/800.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "CredFácil: crédito e maquininhas, sem complicação",
  description:
    "Consulte pelo CNPJ, entenda as possibilidades de crédito e compare custos simulados de maquininhas. Simulação, não é oferta de crédito.",
};

export const viewport: Viewport = {
  themeColor: "#f7f3e6",
};

// Applies the saved "reduzir movimento" choice before the first paint, so nothing moves by accident.
const lerPreferenciaDeMovimento = `try{var m=localStorage.getItem("credfacil-movimento");if(m==="reduzido"||m==="normal")document.documentElement.dataset.movimento=m}catch(e){}`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: lerPreferenciaDeMovimento }} />
      </head>
      <body>
        <a className="pular-link" href="#conteudo">
          Pular para o conteúdo
        </a>
        {children}
      </body>
    </html>
  );
}
