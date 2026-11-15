"""GLB integration, viewer and failure recovery; Chromium with touch emulation."""
import os,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('GAME_URL','http://127.0.0.1:8000').rstrip('/')
OUT=Path(os.environ.get('GAME_TEST_OUTPUT','/tmp/sondervig-characters-checks'));OUT.mkdir(parents=True,exist_ok=True)
report=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    for label,width,height,mobile in [('desktop',1280,800,False),('mobile',412,915,True)]:
        context=browser.new_context(viewport={'width':width,'height':height},has_touch=mobile,is_mobile=mobile,device_scale_factor=1)
        page=context.new_page();errors=[];failures=[];console=[]
        page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:failures.append(r.url));page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
        page.goto(BASE+'/osm-3d-preview.html?test=1');page.wait_for_function('!!window.__game',timeout=60000)
        actors=page.evaluate('[__game.player,__game.family,__game.ida].map(a=>({name:a.name,model:a.userData.model,clips:a.userData.clipNames}))')
        assert [a['name']for a in actors]==['Simon','Swantje','Ida']
        assert all(a['model']=='glb' and sorted(a['clips'])==['Idle','Walk']for a in actors),actors
        assert page.evaluate('__game.grid.near(__game.ida.position.x,__game.ida.position.z).some(c=>c.id==="ida")')
        page.screenshot(path=str(OUT/f'{label}-world.png'))
        page.locator('#help').click();page.locator('a[href="./character-studio.html"]').click();page.wait_for_function('!!window.__studio',timeout=60000) if '?test=1' in page.url else None
        # The normal viewer intentionally has no debug object; reload explicitly.
        page.goto(BASE+'/character-studio.html?test=1');page.wait_for_function('!!window.__studio',timeout=60000)
        for id,expected in [('simon',1.88),('swantje',1.87),('ida',1.05)]:
            page.locator(f'[data-character="{id}"]').click();page.wait_for_function('id=>__studio.avatar.userData.character===id',arg=id,timeout=60000)
            info=page.evaluate('''async () => {
                const T=await import('./vendor/three.module.js'),a=__studio.avatar;a.userData.update(.01,0);a.updateMatrixWorld(true);
                const bounds=new T.Box3().setFromObject(a,true);let meshes=0,joints=0; a.traverse(o=>{if(o.isSkinnedMesh){meshes++;joints=o.skeleton.bones.length;}});
                const foot=[];for(let i=0;i<10;i++){a.userData.update(.08,1);a.updateMatrixWorld(true);const b=new T.Box3().setFromObject(a,true);foot.push(b.min.y);}
                return {height:bounds.max.y-bounds.min.y,meshes,joints,foot};
            }''')
            assert abs(info['height']-expected)<.04,(id,info)
            assert info['meshes']>0 and info['joints']==18,(id,info)
            assert min(info['foot'])>-.012,(id,info)
            page.locator('#face').click();page.screenshot(path=str(OUT/f'{label}-{id}-face.png'));page.locator('#full').click()
            report.append({'viewport':label,'character':id,**info})
        before=page.evaluate('__studio.state().distance');page.locator('#face').click();assert page.evaluate('__studio.state().distance')<before
        page.locator('#walk').click();assert page.locator('#walk').get_attribute('aria-pressed')=='true'
        page.locator('#turn').click();assert page.locator('#turn').get_attribute('aria-pressed')=='true'
        if mobile:
            cdp=context.new_cdp_session(page);before=page.evaluate('__studio.state().yaw')
            cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'id':1,'x':220,'y':410}]})
            cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'id':1,'x':280,'y':420}]})
            cdp.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]});assert abs(page.evaluate('__studio.state().yaw')-before)>.1
        assert not errors and not failures and not console,(label,errors,failures,console)
        context.close()
    # A broken character asset must not take working movement/OSM down with it.
    context=browser.new_context(viewport={'width':1000,'height':700});page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('**/assets/characters/simon.glb',lambda route:route.abort())
    page.goto(BASE+'/osm-3d-preview.html?test=1');page.wait_for_function('!!window.__game',timeout=60000)
    assert page.evaluate('__game.player.userData.model')=='fallback'
    assert 'Ersatzfigur aktiv' in page.locator('#status').inner_text()
    page.evaluate('__game.teleport(-205,95)');before=page.evaluate('__game.player.position.toArray()');page.keyboard.down('s')
    page.wait_for_function('p=>Math.hypot(__game.player.position.x-p[0],__game.player.position.z-p[2])>.2',arg=before,timeout=30000);page.keyboard.up('s')
    assert not errors,errors
    report.append({'fallback':'Simulated missing Simon GLB: OSM scene and movement remain functional'})
    context.close();browser.close()
(OUT/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'character_view_checks':len(report)-1,'fallback':'passed','output':str(OUT)}))
