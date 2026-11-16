// node tests/still.js [page.html]  ->  ok: nothing moves while you watch
// Opens the playground at six widths from a small phone to a desktop, opens the running x = 5 box, and watches for longer
// than one full loop of it. Every button, line of text and the page height must stay exactly where they are.
// REAL_FONTS=1 loads the web fonts too (needs the network). A web address works in place of the file.
// (Needs Playwright, like tests/page.js.)  Run on the old page from before 16 Nov it fails: the box grew 27px.
const {chromium,devices}=require('playwright');const fs=require('fs'),path=require('path'),os=require('os');
const file=process.argv[2]||path.join(__dirname,'..','docs','index.html');
(async()=>{const b=await chromium.launch();let fails=0;
 const phone=(w)=>[w+'px phone',{viewport:{width:w,height:700},hasTouch:true,isMobile:true,deviceScaleFactor:2}];
 const sizes=[phone(320),phone(360),phone(375),['Pixel 7',{...devices['Pixel 7']}],['tablet',{viewport:{width:768,height:1000}}],['desktop',{viewport:{width:1280,height:800}}]];
 const realFonts=process.env.REAL_FONTS==='1';
 await Promise.all(sizes.map(async([name,opts])=>{
  const ctx=await b.newContext(opts);const p=await ctx.newPage();
  if(!realFonts)await p.route('**/*',r=>r.request().url().startsWith('https://fonts')?r.abort():r.continue());
  await p.goto(/^https?:/.test(file)?file:'file://'+path.resolve(file));await p.waitForTimeout(500);
  await p.evaluate(()=>{const d=[...document.querySelectorAll('details')].find(x=>/forever is done/.test(x.textContent));if(d)d.open=true;});
  const where=()=>p.evaluate(()=>document.documentElement.scrollHeight+' '+[...document.querySelectorAll('button,summary,p,li,.lim')].filter(e=>e.offsetParent&&!e.closest('#steps')).map(e=>Math.round(e.getBoundingClientRect().top+scrollY)).join(','));
  const seen=new Set();const t0=Date.now();
  while(Date.now()-t0<12000){seen.add(await where());await p.waitForTimeout(100);}
  if(seen.size!==1){fails++;const hs=[...seen].map(s=>s.split(' ')[0]);console.log('FAIL '+name+': the page moved while nobody touched it (page heights '+[...new Set(hs)].join(', ')+')');}
  await ctx.close();}));
 await b.close();console.log(fails?'FAILED: '+fails+' of '+sizes.length+' screen sizes':'ok: nothing moves while you watch ('+sizes.length+' screen sizes, 12 s each'+(realFonts?', real fonts':'')+')');process.exit(fails?1:0);})();
