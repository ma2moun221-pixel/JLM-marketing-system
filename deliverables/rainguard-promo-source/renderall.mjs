import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
const [,, url, outDir, from, to, fps='30'] = process.argv;
const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1080,height:1920}});
await p.goto(url); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
for (let f=+from; f<+to; f++) {
  await p.evaluate(t=>window.renderFrame(t), f/ +fps);
  await p.screenshot({path:`${outDir}/f_${String(f).padStart(4,'0')}.png`});
}
await b.close();
