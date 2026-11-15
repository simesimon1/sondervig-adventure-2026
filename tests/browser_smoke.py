"""Opt-in browser checks. Start the static server first; see README.
Uses a real Chromium renderer, with touch/viewport emulation, not physical devices.
"""
import json
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = os.environ.get('GAME_URL', 'http://127.0.0.1:8000').rstrip('/')
OUT = Path(os.environ.get('GAME_TEST_OUTPUT', '/tmp/sondervig-browser-checks'))
OUT.mkdir(parents=True, exist_ok=True)
REPORT = []


def state(page):
    return page.evaluate('__game.state()')


def distance(a, b):
    return math.hypot(a[0] - b[0], a[2] - b[2])


def load(browser, name, width, height, mobile=False):
    context = browser.new_context(viewport={'width': width, 'height': height}, has_touch=mobile, is_mobile=mobile, device_scale_factor=2 if mobile else 1)
    page = context.new_page()
    errors, failures = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failures.append(request.url))
    page.goto(BASE + '/osm-3d-preview.html?test=1')
    page.wait_for_function('!!window.__game', timeout=60000)
    page.wait_for_timeout(300)
    assert '122 Wege · 227 Gebäude' in page.locator('#status').inner_text()
    assert not errors, errors
    assert not failures, failures
    assert state(page)['shadows'] != mobile
    return context, page, errors, failures


with sync_playwright() as p:
    binary = os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium')
    browser = p.chromium.launch(executable_path=binary, headless=True, args=['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    context, page, errors, failures = load(browser, 'desktop', 1440, 900)
    page.screenshot(path=str(OUT / 'desktop-house.png'))
    # Keyboard movement in a clear, level local area; also check heading relation.
    page.evaluate('__game.teleport(-205, 95)')
    before = state(page)
    page.keyboard.down('s')
    page.wait_for_function('p => Math.hypot(__game.player.position.x-p[0],__game.player.position.z-p[2])>.3', arg=before['player'], timeout=20000)
    page.keyboard.up('s')
    after = state(page)
    assert distance(before['player'], after['player']) > .25
    assert after['player'][0] < before['player'][0]  # yaw=-1, backward faces west
    # No stuck keys after loss of focus.
    page.keyboard.down('d'); page.evaluate("window.dispatchEvent(new Event('blur'))")
    frozen = state(page)['player']; page.wait_for_timeout(180)
    assert distance(frozen, state(page)['player']) < .001
    page.keyboard.up('d')
    # Mouse orbit and wheel use the running scene, then reset follow camera.
    before = state(page)
    page.mouse.move(700, 350); page.mouse.down(); page.mouse.move(790, 380, steps=8); page.mouse.up()
    assert abs(state(page)['yaw'] - before['yaw']) > .3
    before_zoom = state(page)['dist']; page.mouse.wheel(0, 240); page.wait_for_timeout(100)
    assert state(page)['dist'] > before_zoom
    page.locator('#reset').click(); assert abs(state(page)['dist'] - 16) < .001
    # House collision through normal input, oriented toward its actual footprint.
    page.evaluate('''() => { const f=__game.home.frame; __game.teleport(f.center.x+f.u.x*(f.width/2+1),f.center.z+f.u.z*(f.width/2+1)); }''')
    # Turn the camera so W points directly through the house wall.
    target_yaw = page.evaluate('Math.atan2(__game.home.frame.u.x,__game.home.frame.u.z)')
    delta_x = (state(page)['yaw'] - target_yaw) / .007
    page.mouse.move(650, 350); page.mouse.down(); page.mouse.move(650 + delta_x, 350, steps=8); page.mouse.up()
    page.keyboard.down('w')
    page.wait_for_function('''() => {const f=__game.home.frame,p=__game.player.position;
      return Math.abs((p.x-f.center.x)*f.u.x+(p.z-f.center.z)*f.u.z)-f.width/2<.43;}''',timeout=20000)
    page.wait_for_timeout(500); page.keyboard.up('w')
    collision = page.evaluate('''async () => { const w=await import('./src/world.js'); const p={x:__game.player.position.x,z:__game.player.position.z}; return {inside:w.inside(p,__game.home.points),distance:w.polygonDistance(p,__game.home.points),ground:__game.player.position.y-__game.world.terrain.height(p.x,p.z)}; }''')
    assert not collision['inside'] and .3199 <= collision['distance'] <= .45, collision
    assert abs(collision['ground']) < .0001
    # All rendered road triangle centroids must be outside building footprints;
    # their vertices must match the shared terrain sampler + surface offset.
    geo = page.evaluate('''async () => {
      const w=await import('./src/world.js'); let overlap=0,error=0,count=0;
      for(const buffer of Object.values(__game.world.roadGeometry)){
        const ps=buffer.position;
        for(let i=0;i<ps.length;i+=9){
          const p={x:(ps[i]+ps[i+3]+ps[i+6])/3,z:(ps[i+2]+ps[i+5]+ps[i+8])/3};
          for(const b of __game.world.buildingGrid.near(p.x,p.z)) if(w.inside(p,b.points) && w.polygonDistance(p,b.points)===0) overlap++;
          for(let j=0;j<9;j+=3) error=Math.max(error,Math.abs(ps[i+j+1]-__game.world.terrain.height(ps[i+j],ps[i+j+2])-.045));
          count++;
        }
      } return {overlap,error,count};
    }''')
    assert geo['overlap'] == 0, geo
    assert geo['error'] < .00001 and geo['count'] > 1000, geo
    # Interaction range and one-shot collection.
    page.evaluate('''() => {const s=__game.collectibles[0];__game.teleport(s.x,s.z);}''')
    page.keyboard.press('e'); assert state(page)['collected'] == 1
    page.keyboard.press('e'); assert state(page)['collected'] == 1
    # Parked vehicle has a real collider, and the figure stays outside it.
    car_check = page.evaluate('''async () => { const w=await import('./src/world.js'); const c=__game.car.position; const end=w.moveActor({x:c.x-8,z:c.z},16,0,.32,__game.grid,__game.world.terrain); return {blocked:w.blocked(end,.32,__game.grid),stopped:end.x<c.x}; }''')
    assert car_check == {'blocked': False, 'stopped': True}, car_check
    # Free terrain is actually walkable; grounding follows its triangulated height.
    dune = page.evaluate('''async () => {const w=await import('./src/world.js');const t=__game.world.terrain;let best={x:0,z:0,y:0};for(let x=-210;x<-80;x+=4)for(let z=-140;z<140;z+=4){const y=t.height(x,z);if(y>best.y&&!w.blocked({x,z},.5,__game.grid))best={x,z,y};}__game.teleport(best.x,best.z);return best;}''')
    assert dune['y'] > 3
    page.keyboard.down('s'); page.wait_for_timeout(250); page.keyboard.up('s')
    assert page.evaluate('Math.abs(__game.player.position.y-__game.world.terrain.height(__game.player.position.x,__game.player.position.z))') < .0001
    page.screenshot(path=str(OUT / 'desktop-dunes.png'))
    page.locator('#survey').click(); page.wait_for_timeout(250); page.screenshot(path=str(OUT / 'desktop-overview.png'))
    page.locator('#help').click(); assert page.locator('#guide').evaluate('(e)=>e.open')
    page.locator('#closeGuide').click()
    assert not errors and not failures, (errors, failures)
    REPORT.append({'viewport':'desktop 1440×900','checks':'keyboard, mouse, wheel, blur, house/car collision, grounding, collect, terrain, clipped roads, help','geometry':geo,'render':state(page)})
    context.close()

    # CDP sends genuine touch sequences, including pointer capture and cancellation.
    for name, width, height in [('phone-390',390,844),('phone-412',412,915),('tablet-820',820,1180),('phone-landscape',844,390)]:
        context, page, errors, failures = load(browser, name, width, height, True)
        page.screenshot(path=str(OUT / f'{name}.png'))
        page.evaluate('__game.teleport(-205,95)')
        cdp = context.new_cdp_session(page)
        def touch(kind, points):
            cdp.send('Input.dispatchTouchEvent', {'type':kind,'touchPoints':[{'id':i,'x':x,'y':y,'radiusX':2,'radiusY':2,'force':1} for i,x,y in points]})
        box=page.locator('#joystick').bounding_box(); sx=box['x']+box['width']/2; sy=box['y']+box['height']/2
        # Keep camera finger away from all HUD controls.
        cx=width*.55; cy=height*.5
        before=state(page)
        touch('touchStart',[(1,sx,sy-25)])
        touch('touchStart',[(1,sx,sy-25),(2,cx,cy)])
        touch('touchMove',[(1,sx,sy-25),(2,cx+45,cy+5)])
        page.wait_for_function('p => Math.hypot(__game.player.position.x-p[0],__game.player.position.z-p[2])>.18', arg=before['player'], timeout=20000)
        during=state(page)
        assert distance(before['player'],during['player'])>.15, (name,before,during)
        assert abs(during['yaw']-before['yaw'])>.15, (name,before,during)
        assert during['pointers']==1 and during['joystick']['id'] is not None
        touch('touchCancel',[]); page.wait_for_timeout(80)
        assert state(page)['pointers']==0 and state(page)['joystick']['id'] is None
        frozen=state(page)['player']; page.wait_for_timeout(160)
        assert distance(frozen,state(page)['player'])<.001
        # Pinch + centroid pan with two touches on the canvas.
        before=state(page); x1=width*.40; x2=width*.65; yy=height*.48
        touch('touchStart',[(3,x1,yy),(4,x2,yy)])
        touch('touchMove',[(3,x1-20,yy+25),(4,x2+20,yy+25)])
        touch('touchEnd',[]); page.wait_for_timeout(80)
        after=state(page)
        assert after['dist']<before['dist']-.1, (name,before,after)
        assert math.hypot(after['target'][0]-before['target'][0],after['target'][2]-before['target'][2])>.1
        assert after['pointers']==0
        # Controls fit within the viewport; screenshots support visual review.
        for selector in ['#joystick','#action','#help','#quality','#reset']:
            bb=page.locator(selector).bounding_box(); assert bb['x']>=0 and bb['y']>=0 and bb['x']+bb['width']<=width+1 and bb['y']+bb['height']<=height+1,(name,selector,bb)
        page.locator('#quality').click(); assert not state(page)['shadows']
        page.locator('#quality').click(); assert state(page)['shadows']
        page.locator('#help').click(); assert page.locator('#guide').evaluate('(e)=>e.open'); page.locator('#closeGuide').click()
        assert not errors and not failures,(name,errors,failures)
        REPORT.append({'viewport':name,'checks':'simultaneous joystick/orbit, pinch/pan, touch cancellation, quality, help, controls fit','render':after})
        context.close()
    # Existing entry points remain reachable and the old game still starts.
    page=browser.new_page(); legacy_errors=[];page.on('pageerror',lambda e:legacy_errors.append(str(e)))
    page.goto(BASE+'/');page.wait_for_timeout(300);assert page.locator('a[href="./osm-3d-preview.html"]').count()==1
    page.locator('#start').click();assert page.locator('#intro').count()==0
    page.goto(BASE+'/osm-preview.html');page.wait_for_function("document.querySelector('#status').textContent.includes('122')",timeout=30000)
    assert '227' in page.locator('#status').inner_text();assert not legacy_errors,legacy_errors
    browser.close()
(OUT/'report.json').write_text(json.dumps(REPORT,indent=2,ensure_ascii=False))
print(json.dumps({'passed':len(REPORT),'artifacts':str(OUT),'road_geometry':REPORT[0]['geometry']},ensure_ascii=False))
