import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('GAME_URL','http://127.0.0.1:8000').rstrip('/');out=Path('/tmp/sondervig-beach-tests');out.mkdir(exist_ok=True)
with sync_playwright()as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']);ctx=b.new_context(viewport={'width':412,'height':915},has_touch=True,is_mobile=True);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text)if m.type=='error'else None)
 page.goto(BASE+'/osm-3d-preview.html?test=1');page.wait_for_function('!!window.__game',timeout=60000)
 assert page.evaluate('__game.mission.stage')=='talk'
 page.evaluate('__game.teleport(__game.family.position.x+1,__game.family.position.z)');page.locator('#action').click();assert page.evaluate('__game.mission.stage')=='walk'
 page.screenshot(path=str(out/'start.png'))
 # Input still moves relative to camera; real touch cancellation releases it.
 page.evaluate('__game.teleport(-205,95)');before=page.evaluate('__game.player.position.toArray()');bb=page.locator('#joystick').bounding_box();x=bb['x']+bb['width']/2;y=bb['y']+bb['height']/2;cdp=ctx.new_cdp_session(page)
 def touch(t,points):cdp.send('Input.dispatchTouchEvent',{'type':t,'touchPoints':[{'id':i,'x':x,'y':y}for i,x,y in points]})
 touch('touchStart',[(1,x,y-25)]);touch('touchStart',[(1,x,y-25),(2,220,410)]);touch('touchMove',[(1,x,y-25),(2,260,410)]);page.wait_for_function('p=>Math.hypot(__game.player.position.x-p[0],__game.player.position.z-p[2])>.18',arg=before,timeout=30000);touch('touchCancel',[]);assert page.evaluate('__game.state().pointers')==0
 page.evaluate('__game.teleport(__game.BEACH.x,__game.BEACH.z)');page.wait_for_function('__game.mission.stage==="collect"');page.locator('#seaView').click();page.screenshot(path=str(out/'beach.png'))
 for i in range(3):
  page.evaluate('i=>{const s=__game.collectibles[i];__game.teleport(s.x,s.z);}',i);page.locator('#action').click()
 assert page.evaluate('__game.mission.stage')=='return'
 page.reload();page.wait_for_function('!!window.__game',timeout=60000);assert page.evaluate('__game.mission.stage')=='return';assert page.evaluate('__game.mission.shells.length')==3
 page.evaluate('__game.teleport(__game.home.frame.center.x-8,__game.home.frame.center.z+3)');page.locator('#action').click();assert page.evaluate('__game.mission.stage')=='done';page.screenshot(path=str(out/'done.png'))
 page.locator('#help').click();page.once('dialog',lambda d:d.accept());page.locator('#restartQuest').click();page.wait_for_function('!!window.__game&&__game.mission.stage==="talk"',timeout=60000)
 assert not errors,errors
 (out/'report.json').write_text(json.dumps({'mission':'talk → walk → collect → return → done','reload':'passed','touch':'passed','errors':errors}));print('Mission, persisted reload, simultaneous touch and rendering passed.');b.close()
