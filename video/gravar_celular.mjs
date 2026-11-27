// Uso (VPS): docker run --rm -v $PWD:/w -w /w mcr.microsoft.com/playwright:v1.65.1-noble node video/gravar_celular.mjs <url> fonte/celular/<nome> [quadros] [px] [início-px]
// (precisa de npm i playwright@1.65.1 na pasta)
// grava rolagem suave em tela de celular, quadro a quadro
import { chromium } from "playwright";
const [url, out, n = "170", desce = "1800", inicio = "0"] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 390, height: 780 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, bypassCSP: true });
await p.goto(url, { waitUntil: "networkidle", timeout: 60000 });
await p.addStyleTag({ content: "html{scroll-behavior:auto!important}::-webkit-scrollbar{display:none}" });
await p.waitForTimeout(3000);
const fs = await import("node:fs"); fs.mkdirSync(out, { recursive: true });
const ease = (t) => t * t * (3 - 2 * t); const N = +n, D = +desce;
for (let i = 0; i < N; i++) {
  const t = Math.min(1, Math.max(0, (i - 20) / (N - 40)));
  await p.evaluate((y) => new Promise((r) => { scrollTo(0, y); requestAnimationFrame(() => requestAnimationFrame(r)); }), Math.round(+inicio + D * ease(t)));
  await p.screenshot({ path: `${out}/q_${String(i + 1).padStart(4, "0")}.jpg`, type: "jpeg", quality: 92 });
}
await b.close(); console.log(out, N);
