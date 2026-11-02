// node tools/shot.js <out.png> [--w 1440] [--h 900] [--js "code run in page before the shot"] [--wait 800] [--dark]
// Opens build/index.html, reports console errors and horizontal overflow.
const {chromium}=require('playwright');const path=require('path');
const a=process.argv.slice(2),out=a[0],o=k=>{const i=a.indexOf('--'+k);return i>=0?a[i+1]:null};
(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:+(o('w')||1440),height:+(o('h')||900)},deviceScaleFactor:+(o('dpr')||1),hasTouch:a.includes('--touch'),colorScheme:a.includes('--dark')?'dark':'light'});
const errs=[];p.on('pageerror',e=>errs.push('pageerror: '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push('console: '+m.text())});
await p.goto('file://'+path.resolve(__dirname,'../build/index.html'));await p.waitForTimeout(+(o('wait')||1200));
if(o('js')){await p.evaluate(o('js'));await p.waitForTimeout(+(o('wait')||1200));}
await p.screenshot({path:out});
const of=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
console.log(JSON.stringify({out,overflowX:of,errors:errs}));await b.close();})();
