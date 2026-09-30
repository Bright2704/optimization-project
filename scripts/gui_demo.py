"""Visible Google Chrome demo with Thai captions, assertions and a replay video.

The Chrome window remains open for the user after the recorded tour.
No personal Chrome profile is accessed: a temporary profile is used.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8091')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'docs/verification/gui')
    parser.add_argument('--debug-port', type=int, default=9333)
    args = parser.parse_args()
    base = args.url.rstrip('/')
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    chrome = shutil.which('google-chrome-stable') or shutil.which('google-chrome')
    if not chrome:
        raise RuntimeError('Google Chrome is required for this demonstration')
    profile = tempfile.mkdtemp(prefix='goa-gui-chrome-')
    log = (out/'chrome.log').open('w')
    process = subprocess.Popen([chrome, f'--user-data-dir={profile}',
        f'--remote-debugging-port={args.debug_port}', '--remote-debugging-address=127.0.0.1',
        '--no-first-run', '--no-default-browser-check', '--disable-dev-shm-usage',
        '--window-size=1480,1000', '--new-window', base], stdout=log, stderr=log,
        start_new_session=True)
    endpoint = f'http://127.0.0.1:{args.debug_port}'
    for attempt in range(80):
        if process.poll() is not None:
            raise RuntimeError(f'Chrome exited: {(out/"chrome.log").read_text()}')
        try:
            with urllib.request.urlopen(endpoint+'/json/version',timeout=1) as response:
                chrome_info=json.load(response)
            break
        except OSError:
            time.sleep(.25)
    else:
        raise RuntimeError('Chrome debugging endpoint did not become ready')
    print(f'Visible Google Chrome is open (PID {process.pid}); beginning GUI tour',flush=True)
    errors=[]; checks=[]; scenes=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.connect_over_cdp(endpoint)
        normal=browser.contexts[0]
        context=browser.new_context(viewport={'width':1440,'height':920},
                    record_video_dir=str(out),record_video_size={'width':1440,'height':920},locale='th-TH')
        page=context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.bring_to_front()
        page.goto(base,wait_until='networkidle')
        page.wait_for_function("document.getElementById('contour-plot').data?.length === 2")
        # Caption and zoom apply only to this demonstration tab.
        page.evaluate("""() => {
            document.body.style.zoom='0.75';
            const caption=document.createElement('div');caption.id='gui-demo-caption';
            caption.style.cssText='position:fixed;bottom:8px;left:10px;right:10px;z-index:999999;background:#152b46;color:white;padding:14px 20px;border-radius:12px;font:26px "IBM Plex Sans Thai",sans-serif;line-height:1.35;pointer-events:none;box-shadow:0 2px 12px #0004';
            document.body.appendChild(caption);
        }""")

        def scene(stem,caption,seconds=3):
            page.locator('#gui-demo-caption').evaluate('(el,text)=>el.textContent=text',caption)
            page.wait_for_timeout(350)
            page.screenshot(path=str(out/f'{stem}.png'))
            scenes.append(dict(scene=stem,caption=caption,screenshot=f'{stem}.png'))
            print(caption,flush=True)
            page.wait_for_timeout(seconds*1000)

        def animation_ready():
            page.wait_for_function("document.getElementById('animation-section').dataset.loading === 'false' && document.getElementById('total-iterations').textContent === '100'")
            page.evaluate("document.getElementById('animation-section').scrollIntoView({block:'start',behavior:'instant'})")
            page.wait_for_timeout(400)

        def assert_frame(data,frame):
            actual=page.evaluate("""() => {
                const plot=document.getElementById('animation-plot');
                const optimum=plot.data.find(t=>t.name?.includes('Known optimum'));
                const best=plot.data.find(t=>t.name==='Best-so-far (archive through this iteration)');
                const agents=plot.data.find(t=>t.name?.includes('Agents ปัจจุบัน')||t.name?.includes('Current Agents'));
                return {frame:Number(document.getElementById('current-iteration').textContent),
                        best:[best.x[0],best.y[0]],optimum:[optimum.x[0],optimum.y[0]],
                        agents:agents.x.map((x,i)=>[x,agents.y[i]]),
                        fitness:Number(document.getElementById('current-fitness').textContent)};
            }""")
            assert actual['frame']==frame
            assert actual['best']==data['best_positions_history'][frame]
            assert actual['optimum']==data['known_optimum']['position']
            assert actual['agents']==data['frames'][frame]
            assert abs(actual['fitness']-data['history'][frame])<=max(1e-30,abs(data['history'][frame])*6e-5)
            return actual

        scene('01_setup','1/8 เลือก GOA + Sphere · 30 agents · 100 iterations · Seed 424242',4)
        with page.expect_response('**/api/run') as response:
            page.click('#run-btn')
        result=response.value.json()
        page.wait_for_function("document.getElementById('convergence-plot').data?.length === 1")
        page.locator('.charts').scroll_into_view_if_needed()
        scene('02_run_result',f"2/8 กด Run: ได้ Best fitness = {result['fitness']:.4e} · ใช้ {result['evaluation_count']:,} evaluations",4)
        assert len(result['history'])==101 and result['evaluation_count']==3030
        with page.expect_response('**/api/run_animation') as response:
            page.click('#animation-btn')
        data=response.value.json();animation_ready();assert_frame(data,0)
        scene('03_sphere_initial','3/8 Animation เริ่มที่ iteration 0: แดง = agents · เขียว = known optimum · ส้ม = best-so-far',4)
        page.select_option('#animation-speed','4')
        page.click('#play-btn')
        page.wait_for_function("Number(document.getElementById('current-iteration').textContent) >= 25")
        page.click('#pause-btn')
        paused=int(page.locator('#current-iteration').inner_text());before=assert_frame(data,paused)
        page.wait_for_timeout(900)
        assert int(page.locator('#current-iteration').inner_text())==paused
        scene('04_play_pause',f'4/8 กด Play แล้ว Pause: หยุดจริงที่ iteration {paused} · fitness และตำแหน่งตรงกับ frame',4)
        # Use keyboard on the real range control to seek, rather than invoking the application function.
        slider=page.locator('#iteration-slider');slider.focus();slider.press('Home')
        for _ in range(50):slider.press('ArrowRight')
        assert_frame(data,50)
        scene('05_seek_midpoint',f"5/8 เลื่อน slider ไป iteration 50: Best fitness = {data['history'][50]:.4e}",4)
        slider.press('End');sphere_final=assert_frame(data,100)
        scene('06_sphere_final','6/8 เลื่อนไป iteration 100: จุดรวมกันได้ แต่ดูค่า fitness ด้วย ไม่ถือว่าถึง optimum โดยอัตโนมัติ',4)
        checks.append(dict(function='sphere',algorithm='goa',agents=30,iterations=100,frames=len(data['frames']),
                           evaluations=data['evaluation_count'],play_pause_verified=True,
                           slider_keyboard_seek_50_100=True,final_fitness=data['fitness'],final_position=data['position']))
        page.select_option('#function','rosenbrock')
        with page.expect_response('**/api/run_animation') as response:
            page.click('#animation-btn')
        data=response.value.json();animation_ready();assert_frame(data,0)
        scene('07_rosenbrock_initial','7/8 เปลี่ยนเป็น Rosenbrock: optimum = (1,1) · สี contour ใช้ log10(1+f) เพื่อเห็นหุบเขา',4)
        page.select_option('#animation-speed','4');page.click('#play-btn')
        page.wait_for_function("document.getElementById('current-iteration').textContent === '100'",timeout=25000)
        page.wait_for_function("document.getElementById('play-btn').disabled === false")
        final=assert_frame(data,100)
        scene('08_rosenbrock_final',f"Rosenbrock จบรอบ 100: fitness = {data['fitness']:.4e} ยังมากกว่า 0 · best-so-far ≠ known optimum",4)
        checks.append(dict(function='rosenbrock',algorithm='goa',agents=30,iterations=100,frames=len(data['frames']),
                           evaluations=data['evaluation_count'],complete_playback=True,
                           final_fitness=data['fitness'],final_position=data['position']))
        page.select_option('#function','sphere')
        with page.expect_response('**/api/run'):
            page.click('#compare-btn')
        page.wait_for_function("document.querySelectorAll('#comparison-body tr').length === 3 && document.getElementById('convergence-plot').data?.length === 3")
        page.locator('#comparison-section').scroll_into_view_if_needed()
        comparison=page.locator('#comparison-body').inner_text()
        scene('09_compare','8/8 Compare All: เปรียบเทียบ GOA / GA / RLS ในตัวอย่างรันเดียว · สถิติ 30 runs อยู่ใน results/workshop',5)
        assert not errors,errors
        video=page.video
        page.close();context.close()
        source=video.path(); replay=out/'gui_demo.webm'
        if source!=replay:shutil.move(str(source),replay)
        # Leave the normal Chrome window ready for hands-on use.
        landing=normal.pages[0] if normal.pages else normal.new_page()
        landing.goto(base,wait_until='networkidle');landing.bring_to_front()
        landing.select_option('#function','rosenbrock');landing.click('#animation-btn')
        landing.wait_for_function("document.getElementById('animation-section').dataset.loading === 'false'")
        landing.evaluate("document.getElementById('animation-section').scrollIntoView({block:'start'})")
        version=browser.new_browser_cdp_session().send('Browser.getVersion')
        evidence=dict(status='passed',created_utc=datetime.now(timezone.utc).isoformat(),
                      browser='Google Chrome',headed=True,chrome_version=version,chrome_process_id=process.pid,
                      temporary_profile=profile,url=base,checks=checks,compare_all_ui=True,
                      comparison_text=comparison,page_errors=errors,scenes=scenes,
                      replay_webm='gui_demo.webm',window_left_open=True)
        (out/'gui_demo.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
        print('GUI checks passed; Chrome remains open for you.',flush=True)
    if shutil.which('ffmpeg'):
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(replay),'-c:v','libx264','-preset','fast',
                        '-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'gui_demo.mp4')],check=True)
        print(f'Replay: {out/"gui_demo.mp4"}',flush=True)


if __name__=='__main__':main()
