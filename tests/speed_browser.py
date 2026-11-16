import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('GAME_URL','http://127.0.0.1:8000').rstrip('/');out=Path('/tmp/sondervig-speed-tests');out.mkdir(exist_ok=True)
report=[]
with sync_playwright()as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 for name,width,height,mobile in [('phone',412,915,True),('desktop',1280,800,False),('landscape',844,390,True)]:
  ctx=b.new_context(viewport={'width':width,'height':height},has_touch=mobile,is_mobile=mobile,device_scale_factor=1);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text)if m.type=='error'else None)
  page.goto(BASE+'/osm-3d-preview.html?test=1');page.wait_for_function('!!window.__game',timeout=60000)
  for key,speed in [('normal',3.2),('medium',6.4),('fast',9.6)]:
   page.locator('[data-speed="'+key+'"]').click();page.wait_for_function('s=>Math.abs(__game.state().walkingSpeed-s)<.03',arg=speed,timeout=30000);assert page.locator('[data-speed="'+key+'"]').get_attribute('aria-pressed')=='true'
   bb=page.locator('[data-speed="'+key+'"]').bounding_box();assert bb['x']>=0 and bb['y']>=0 and bb['x']+bb['width']<=width and bb['y']+bb['height']<=height,bb
  page.reload();page.wait_for_function('!!window.__game',timeout=60000);assert page.evaluate('__game.state().selectedSpeed')=='fast'
  page.keyboard.press('1');assert page.evaluate('__game.state().selectedSpeed')=='normal';page.keyboard.press('3');assert page.evaluate('__game.state().selectedSpeed')=='fast'
  page.evaluate('__game.teleport(__game.BEACH.x+50,__game.BEACH.z-80)');before=page.evaluate('__game.player.position.toArray()');page.keyboard.down('s');page.wait_for_function('p=>Math.hypot(__game.player.position.x-p[0],__game.player.position.z-p[2])>1',arg=before,timeout=30000);page.keyboard.up('s')
  stats=page.evaluate('''async()=>{const w=await import('./src/world.js');const h=__game.scene.children.find(o=>o.userData.reference);let valid=true;for(const c of h.userData.obstacles){const p={x:c.points.reduce((s,p)=>s+p.x,0)/4,z:c.points.reduce((s,p)=>s+p.z,0)/4};valid&&=w.blocked(p,.32,__game.grid);}return {openings:h.userData.openings.length,furnitureCollision:valid};}''');assert stats['openings']==5 and stats['furnitureCollision'],stats
  page.evaluate('__game.teleport(-8,6)');page.screenshot(path=str(out/(name+'.png')))
  assert not errors,errors;report.append({'viewport':name,'levels':'3.2/6.4/9.6','persisted':True,**stats});ctx.close()
 b.close()
(out/'report.json').write_text(json.dumps(report,indent=2));print('Three speed levels, keyboard, persistence, movement and home details passed on 3 viewports.')
