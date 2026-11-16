// node tests/page.js -> ok: N page checks (needs Playwright: npm i -D playwright && npx playwright install chromium)
const {chromium,devices}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();
 const ctx=await b.newContext({...devices['Pixel 7']});const p=await ctx.newPage();
 const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/ERR_FAILED/.test(m.text()))errs.push(m.text())});
 const html='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+fs.readFileSync(require('path').join(__dirname,'..','docs','index.html'),'utf8')+'</body></html>';
 await p.route('**/*',r=>r.request().url().startsWith('https://fonts')?r.abort():r.continue());
 await p.setContent(html);await p.waitForTimeout(400);
 let fails=0,checks=0;
 // first screen is calm: one big button, no code, nothing running, no answers yet
 checks++;if(!(await p.locator('#tourb').isVisible())||await p.locator('#code').isVisible()||await p.locator('#answers').isVisible()||await p.locator('.live').isVisible()||!(await p.locator('#ownb').isVisible())){fails++;console.log('FAIL calm first screen');}
 await p.click('#ownb');await p.waitForTimeout(400);
 // CH 16 Nov: answers only after Run. Opening the editor shows code, not answers
 checks++;if(await p.locator('#answers').isVisible()){fails++;console.log('FAIL write your own ran before Run was pressed');}
 checks++;if(!(await p.locator('#code').isVisible())||(await p.inputValue('#code'))!=='x = 5\nforever: x = x × x\nshow x\nshow x × x = x'||await p.locator('#ownb').isVisible()){fails++;console.log('FAIL write your own opens');}
 const n=await p.locator('.chip').count();
 const want={'Own square':['…918212890625','yes  (proved)'],'Tower of 3s':['…262464195387','yes  (proved)'],'Minus one':['…999999999999  (this is -1)','0'],'One third':['…666666666667  (this is 1/3)','1'],'196':["can't see the end"],'6 squared':['never settles'],'Twins':['…081787109376','1','0'],'The lamp':['never settles'],'Forever twice':['forever × forever'],'Powers of 2':['no  (proved)'],'Collatz 27':['yes  (proved)','never settles'],'Endless search':['no  (proved)'],'Past forever':['forever + 1','forever × 2','yes'],'Hunt':[],'Adds to −1':['…999999999999  (this is -1)','s: what gets added each step (f × n × n + 2 × f × n + f) settles to 0, and here a sum settles as soon as its pieces do. More than that: s + (− n − 1) × f is the same after every step, so the total is exactly -1'],'Exactly 3':['3','s: what gets added each step (f × n × n × n − 4 × f × n + f) settles to 0, and here a sum settles as soon as its pieces do. More than that: s + (− n + 3) × f is the same after every step, so the total is exactly 3'],'Ring of six':['never settles','x: the last digit of x goes round 0, 1, 2, 5, 6, 7 every 6 steps and never stops. Looking deeper, the last 1 to 40 digits all come round every 6 steps too. As far as I can see, x is going round a ring of 6 endless numbers'],'The liar':['never settles','x: the last digit of x goes round 6, 3 every 2 steps and never stops. Looking deeper, the last 1, 2, 3… digits take 2, 2, 2, 2, 2, 2, 8, 8, 40, 200, 1000, 5000 steps to come round'],'Hunt squares':[],'Hunt thirds':[],'All factorials':['0','…039052556442336528920420940313']};
 for(let i=0;i<n;i++){const c=p.locator('.chip').nth(i);const name=await c.textContent();await c.click();
  checks++;if(await p.locator('#answers').isVisible()){fails++;console.log('FAIL an example ran before Run was pressed',name);}
  await p.click('#run');await p.waitForFunction(()=>!document.querySelector('#out .empty')&&document.querySelectorAll('#out .row').length>0,null,{timeout:15000});
  const vals=await p.locator('#out .val').allTextContents();checks++;
  if(name.startsWith('Hunt')){checks++;const sq=await p.locator('#out .sq').count();if(sq!==(name==='Hunt'?400:100)){fails++;console.log('FAIL hunt squares',name,sq);}}
  if(JSON.stringify(vals)!==JSON.stringify(want[name])){fails++;console.log('FAIL',name,vals);}
  const ow=await p.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);checks++;if(ow){fails++;console.log('FAIL sideways scroll',name);}
 }
 // the hunt map: tap a square, open that one loop
 await p.locator('.chip',{hasText:/^Hunt$/}).click();await p.click('#run');await p.waitForSelector('#out .sq');
 checks++;const head=await p.locator('#out .head').textContent();if(!head.startsWith('hunt c from 0 to 399: tried 400 numbers, 5 kinds')){fails++;console.log('FAIL hunt head',head);}
 checks++;const leg=(await p.locator('#out .legend').textContent()).replace(/\s+/g,' ');if(!leg.includes('ring of 6 40')||!leg.includes('goes wild 160')){fails++;console.log('FAIL legend',leg);}
 await p.locator('#out .sq').nth(14).click();
 checks++;const det=await p.locator('#out .pickd').textContent();if(!det.includes('c = 14: ring of 2')){fails++;console.log('FAIL square detail',det);}
 await p.locator('#out .open',{hasText:'Open this loop'}).click();await p.waitForTimeout(600);
 checks++;if(await p.locator('#answers').isVisible()){fails++;console.log('FAIL Open this loop ran before Run was pressed');}
 await p.click('#run');await p.waitForTimeout(600);
 checks++;const code=await p.inputValue('#code');if(code!=='# stripes: the last digit of c sets the last digit of x at every step\nc = 14\nx = 0\nforever: x = x × x + c\nshow x\nwhy x'){fails++;console.log('FAIL open loop code',JSON.stringify(code));}
 checks++;const v=await p.locator('#out .val').allTextContents();if(JSON.stringify(v)!==JSON.stringify(['never settles','x: the last digit of x goes round 0, 4 every 2 steps and never stops. Looking deeper, the last 1 to 40 digits all come round every 2 steps too. As far as I can see, x is going round a ring of 2 endless numbers'])){fails++;console.log('FAIL opened loop output',v);}
 // zoom: chase the liar 57 -> 4557 -> back out
 await p.locator('.chip',{hasText:/^Hunt$/}).click();await p.click('#run');await p.waitForSelector('#out .sq');
 await p.locator('#out .sq').nth(57).click();await p.locator('#out .open',{hasText:'Zoom in'}).click();await p.waitForTimeout(1500);
 checks++;let hd=await p.locator('#out .head').textContent();if(!hd.startsWith('hunt c from 0 to 99 ends in 57: tried 100')){fails++;console.log('FAIL zoom 1',hd);}
 checks++;if(!(await p.inputValue('#code')).includes('hunt c from 0 to 99 ends in 57:')){fails++;console.log('FAIL zoom code');}
 await p.locator('#out .sq').nth(45).click();
 checks++;let dt=await p.locator('#out .pickd').textContent();if(!dt.includes('c = 4557: goes wild')){fails++;console.log('FAIL zoom square',dt);}
 await p.locator('#out .open',{hasText:'Zoom in'}).click();await p.waitForTimeout(1500);
 checks++;hd=await p.locator('#out .head').textContent();if(!hd.startsWith('hunt c from 0 to 99 ends in 4557')){fails++;console.log('FAIL zoom 2',hd);}
 await p.locator('#out .sq').nth(51).click();
 await p.locator('#out .open',{hasText:'Zoom out'}).click();await p.waitForTimeout(1500);
 checks++;hd=await p.locator('#out .head').textContent();if(!hd.startsWith('hunt c from 0 to 99 ends in 57:')){fails++;console.log('FAIL zoom out',hd);}
 // typing and keys
 await p.fill('#code','show 2 ');await p.click('.key >> nth=0');await p.type('#code',' 21');await p.click('#run');await p.waitForTimeout(300);
 checks++;if((await p.locator('#out .val').first().textContent())!=='42'){fails++;console.log('FAIL typed program',await p.locator('#out').textContent());}
 await p.fill('#code','show 1 / 2');await p.click('#run');await p.waitForTimeout(300);
 checks++;if(!(await p.locator('#out .row.bad').count())){fails++;console.log('FAIL error row');}
 await p.locator('.chip').nth(0).click();await p.click('#run');await p.waitForTimeout(500);await p.locator('.whyb').first().click();
 checks++;if(!(await p.locator('.why').first().isVisible())){fails++;console.log('FAIL why toggle');}
 // report link carries the program and the answer; live box freezes 390625's last five digits in gold
 await p.fill('#code','x = 6\nforever: x = x × x\nshow x');await p.click('#run');await p.waitForTimeout(400);
 { const u=new URL(await p.locator('#out a.report').getAttribute('href'));
   checks++;if(u.origin+u.pathname!=='https://github.com/connabyss/past-forever/issues/new'||u.searchParams.get('template')!=='break-it.yml'||u.searchParams.get('code')!=='x = 6\nforever: x = x × x\nshow x'||!u.searchParams.get('printed').startsWith('never settles')){fails++;console.log('FAIL report link',u.href);} }
 await p.locator('summary',{hasText:'How does it know'}).click();
 await p.locator('#steps div').nth(3).waitFor({timeout:15000});
 // the running x = 5 box keeps one size the whole loop, so the page never jumps
 { const hs=new Set();for(let i=0;i<60;i++){hs.add(await p.evaluate(()=>Math.round(document.querySelector('.live').getBoundingClientRect().height)));await p.waitForTimeout(200);}
   checks++;if(hs.size!==1){fails++;console.log('FAIL live box changes size',[...hs]);} }
 checks++;{const g=await p.locator('#steps div').nth(3).locator('b').textContent();if(g!=='90625'){fails++;console.log('FAIL live gold digits',g);}}
 // wonders tour: open, go to wonder 3, the reveal stays hidden until Show me runs the real code
 await p.click('#tourb');await p.click('#tnext');await p.click('#tnext');
 checks++;if((await p.locator('#tcount').textContent())!=='Wonder 3 of 7'||await p.locator('#treveal').isVisible()){fails++;console.log('FAIL tour step');}
 await p.click('#tshow');await p.waitForTimeout(400);
 checks++;if((await p.locator('#out .val').first().textContent())!=='…857142857143  (this is 1/7)'||!(await p.locator('#treveal').isVisible())){fails++;console.log('FAIL tour show',await p.locator('#out').textContent());}
 await p.click('#tback');checks++;if((await p.locator('#tcount').textContent())!=='Wonder 2 of 7'||await p.locator('#treveal').isVisible()){fails++;console.log('FAIL tour back');}
 // each wonder has its own link: #wonders/4 opens wonder 4 with the answer hidden; Share copies that link; the address follows the tour
 { const os=require('os'),pth=require('path');const f=pth.join(os.tmpdir(),'pf_page_test.html');fs.writeFileSync(f,html);
   const q=await ctx.newPage();q.on('pageerror',e=>errs.push(e.message));await q.route('**/*',r=>r.request().url().startsWith('https://fonts')?r.abort():r.continue());
   await ctx.grantPermissions(['clipboard-read','clipboard-write']).catch(()=>{});
   await q.goto('file://'+f+'#wonders/4');await q.waitForTimeout(500);
   checks++;if(!(await q.locator('#tour').isVisible())||(await q.locator('#tcount').textContent())!=='Wonder 4 of 7'||await q.locator('#treveal').isVisible()||await q.locator('#tshare').isVisible()){fails++;console.log('FAIL wonder link opens wonder 4');}
   await q.click('#tshow');await q.waitForTimeout(400);
   checks++;if(!(await q.locator('#tshare').isVisible())){fails++;console.log('FAIL share button after reveal');}
   await q.evaluate(()=>{window.__copied=null;navigator.share=undefined;navigator.clipboard.writeText=async t=>{window.__copied=t;};});
   await q.click('#tshare');await q.waitForTimeout(200);
   checks++;{const c=await q.evaluate(()=>window.__copied);if(c!=='file://'+f+'#wonders/4'||(await q.locator('#tshare').textContent())!=='Link copied ✓'){fails++;console.log('FAIL share copies link',c);}}
   await q.click('#tnext');
   checks++;if(!(await q.evaluate(()=>location.hash==='#wonders/5'))||await q.locator('#tshare').isVisible()){fails++;console.log('FAIL hash follows tour',await q.evaluate(()=>location.hash));}
   await q.click('#tclose');
   checks++;if(await q.evaluate(()=>location.hash!=='')){fails++;console.log('FAIL close clears hash');}
   await q.evaluate(()=>{location.hash='#wonders/2';});await q.waitForTimeout(300);
   checks++;if((await q.locator('#tcount').textContent())!=='Wonder 2 of 7'||!(await q.locator('#tour').isVisible())){fails++;console.log('FAIL hashchange opens wonder');}
   await q.goto('file://'+f+'#wonders/7');await q.waitForTimeout(400);await q.click('#tshow');await q.waitForTimeout(400);
   checks++;{const v=await q.locator('#out .val').allTextContents();const r=await q.locator('#treveal').textContent();if(JSON.stringify(v)!==JSON.stringify(['…262464195387','yes  (proved)'])||!r.includes('…262464195387')||(await q.locator('#tnext').textContent())!=='Done'){fails++;console.log('FAIL wonder 7 (Graham)',v,r);}}
   checks++;{const t=await q.locator('#tsrc').textContent();if(!(await q.locator('#tcode').isVisible())||t!=='x = 3\nforever: x = 3 ^ x\nshow x\nshow 3 ^ x = x'){fails++;console.log('FAIL wonder shows its code',t);}}
   await q.click('#tedit');await q.waitForTimeout(500);
   checks++;if(!(await q.locator('#code').isVisible())||(await q.inputValue('#code'))!=='x = 3\nforever: x = 3 ^ x\nshow x\nshow 3 ^ x = x'){fails++;console.log('FAIL change it opens the editor');}
   await q.click('#tback');checks++;if(await q.locator('#tcode').isVisible()){fails++;console.log('FAIL code hides on the next wonder');}
   await q.goto('file://'+f+'#wonders/99');await q.waitForTimeout(400);
   checks++;if((await q.locator('#tcount').textContent())!=='Wonder 1 of 7'){fails++;console.log('FAIL bad wonder number');}
   await q.close(); }
 checks++;if(errs.length){fails++;console.log('FAIL page errors',errs);}
 console.log(fails?('FAILED '+fails+' of '+checks):('ok: '+checks+' page checks'));await b.close();})();
