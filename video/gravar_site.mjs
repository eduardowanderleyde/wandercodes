// Grava a rolagem do site em quadros PNG via Chrome DevTools Protocol (sem dependências).
// Uso: node gravar_site.mjs <url> <pasta-saida> <largura> <altura>
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
const [url, out, W = "1920", H = "1080"] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", "--remote-debugging-port=9333", `--user-data-dir=${out}/../chrome-perfil`,
  "--hide-scrollbars", `--window-size=${W},${H}`, "about:blank"], { stdio: "ignore" });
const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50 && !alvo; i++) {
  await dorme(200);
  try { alvo = (await (await fetch("http://127.0.0.1:9333/json")).json()).find((t) => t.type === "page"); } catch {}
}
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d.result); pend.delete(d.id); } };
const cdp = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const avaliar = async (expr) => (await cdp("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result.value;

const movel = +W < 800;
await cdp("Emulation.setDeviceMetricsOverride", { width: +W, height: +H, deviceScaleFactor: movel ? 2 : 1, mobile: movel });
await cdp("Page.enable");
await cdp("Page.navigate", { url });
await dorme(4000);
await avaliar(`document.documentElement.style.scrollBehavior='auto'; document.fonts.ready.then(()=>1)`);
// espera os quadros da abertura carregarem
await avaliar(`new Promise(r=>{let n=0;const t=setInterval(()=>{const ok=[...document.images].length; if(++n>40){clearInterval(t);r(1)} },100)})`);
await dorme(4000);
const total = await avaliar(`document.documentElement.scrollHeight - innerHeight`);
const cine = await avaliar(`(document.querySelector('.cine')||{offsetHeight:0}).offsetHeight ? document.querySelector('.cine').offsetHeight - innerHeight : 0`);
// roteiro em quadros (30 fps): parado, abertura devagar, resto, parado no fim
const ease = (t) => t * t * (3 - 2 * t);
const plano = [];
const seg = (de, ate, n) => { for (let k = 0; k < n; k++) plano.push(de + (ate - de) * ease(k / (n - 1))); };
seg(0, 0, 75);
seg(0, total, Number(process.env.QUADROS || 900));
seg(total, total, 75);
let n = 0;
for (const y of plano) {
  await avaliar(`scrollTo(0, ${Math.round(y)}); new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))`);
  const { data } = await cdp("Page.captureScreenshot", { format: "jpeg", quality: 92 });
  writeFileSync(`${out}/q_${String(++n).padStart(4, "0")}.jpg`, Buffer.from(data, "base64"));
}
console.log(`${n} quadros, página ${total}px`);
ws.close(); chrome.kill();
