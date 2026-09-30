"""Real Chromium interaction audit; app must be running at localhost:8080."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'verification';OUT.mkdir(parents=True,exist_ok=True)


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8080')
    base=parser.parse_args().url.rstrip('/')
    errors=[]; external=[];checks=[]
    with sync_playwright() as p:
        executable=os.environ.get('WORKSHOP_CHROMIUM')
        fallback=Path('/home/tsuna/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell')
        if not executable and fallback.exists():executable=str(fallback)
        browser=p.chromium.launch(executable_path=executable,headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1150})
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request: external.append(request.url) if not request.url.startswith(base+'/') else None)
        page.goto(base+'/',wait_until='networkidle')
        page.wait_for_function("document.getElementById('contour-plot').data?.length === 2")
        page.click('#lang-en')
        assert page.locator('#seed').input_value()=='424242'
        for function in ['sphere','rosenbrock']:
            page.select_option('#function',function)
            for algorithm in ['goa','ga','rls']:
                page.select_option('#algorithm',algorithm)
                page.locator('#n-agents').evaluate("el => { el.value = '30'; el.dispatchEvent(new Event('input', {bubbles:true})); }");page.locator('#max-iter').evaluate("el => { el.value = '50'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
                with page.expect_response('**/api/run_animation') as response_event:page.click('#animation-btn')
                payload=response_event.value.json()
                page.wait_for_function("document.getElementById('animation-section').dataset.loading === 'false' && document.getElementById('total-iterations').textContent === '50' && document.getElementById('animation-plot').data?.some(t=>t.name==='Best-so-far (archive through this iteration)')")
                assert payload['n_frames']==51 and len(payload['history'])==51
                expected_optimum=[0,0] if function=='sphere' else [1,1]
                page.locator('#iteration-slider').evaluate("el => { el.value = '25'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
                page.wait_for_function("document.getElementById('current-iteration').textContent === '25'")
                actual=page.evaluate("""() => {
                    const plot=document.getElementById('animation-plot');
                    const optimum=plot.data.find(t=>t.name==='Known optimum');
                    const best=plot.data.find(t=>t.name==='Best-so-far (archive through this iteration)');
                    const agents=plot.data.find(t=>t.name==='🔴 Current Agents');
                    return {optimum:[optimum.x[0],optimum.y[0]], best:[best.x[0],best.y[0]],
                            agents:agents.x.map((x,i)=>[x,agents.y[i]]), fitness:document.getElementById('current-fitness').textContent,
                            frame:document.getElementById('current-iteration').textContent};
                }""")
                assert actual['optimum']==expected_optimum
                assert actual['best']==payload['best_positions_history'][25]
                assert actual['agents']==payload['frames'][25]
                assert abs(float(actual['fitness'])-payload['history'][25]) <= max(1e-30,abs(payload['history'][25])*6e-5)
                page.click('#play-btn');page.wait_for_timeout(650)
                assert int(page.locator('#current-iteration').inner_text())>25
                page.click('#pause-btn');paused=page.locator('#current-iteration').inner_text()
                page.wait_for_timeout(650);assert page.locator('#current-iteration').inner_text()==paused
                page.locator('#iteration-slider').evaluate("el => { el.value = '50'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
                page.wait_for_function("document.getElementById('current-iteration').textContent === '50'")
                last=float(page.locator('#current-fitness').inner_text())
                assert abs(last-payload['history'][-1])<=max(1e-30,abs(payload['history'][-1])*6e-5)
                page.click('button:has-text("Reset")');assert page.locator('#current-iteration').inner_text()=='0'
                page.click('button:has-text("Step")');assert page.locator('#current-iteration').inner_text()=='1'
                # Full-scale GOA final screenshot, also tests the specified presentation setup.
                if algorithm=='goa':
                    page.locator('#max-iter').evaluate("el => { el.value = '100'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
                    with page.expect_response('**/api/run_animation') as full_event:page.click('#animation-btn')
                    full=full_event.value.json()
                    page.wait_for_function("document.getElementById('animation-section').dataset.loading === 'false' && document.getElementById('total-iterations').textContent === '100'")
                    page.locator('#iteration-slider').evaluate("el => { el.value = '100'; el.dispatchEvent(new Event('input', {bubbles:true})); }")
                    page.wait_for_function("document.getElementById('current-iteration').textContent === '100'")
                    assert full['n_frames']==101 and full['evaluation_count']==3030
                    page.locator('#animation-section').screenshot(path=str(OUT/f'browser_{function}.png'))
                checks.append(dict(function=function,algorithm=algorithm,frames=51,iteration_25_marker_and_value=True,
                                   play=True,pause=True,seek_last=True,reset=True,step=True))
                # Plain Run endpoint reached through UI, not only direct API tests.
                with page.expect_response('**/api/run') as run_event:page.click('#run-btn')
                normal=run_event.value.json();page.wait_for_function("document.getElementById('convergence-plot').data?.length === 1")
                assert 'Seed:' in page.locator('#result-content').inner_text()
            page.click('#compare-btn')
            page.wait_for_function("document.querySelectorAll('#comparison-body tr').length === 3")
            page.wait_for_function("document.getElementById('convergence-plot').data?.length === 3")
            assert 'Winner' not in page.locator('#comparison-body').inner_text()
            # Clear old rows before testing the next function.
            page.evaluate("document.getElementById('comparison-body').innerHTML = ''")
        page.click('#lang-th');page.click('#animation-btn')
        page.wait_for_function("document.getElementById('animation-section').dataset.loading === 'false' && document.getElementById('animation-plot').data?.some(t=>t.name?.includes('Known optimum'))")
        page.locator('#animation-section').screenshot(path=str(OUT/'browser_thai.png'))
        assert not errors,errors
        assert not external,external
        evidence=dict(status='passed',browser='Chromium / Playwright',real_browser=True, url=base,
                      playwright_version=__import__('importlib.metadata').metadata.version('playwright'),
                      combinations=checks,offline_external_requests=external,page_errors=errors,
                      compare_all_both_functions=True,thai_english_switch=True,
                      full_30_agent_100_iteration_goa_both_functions=True)
        (OUT/'browser.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
        print(json.dumps(evidence,indent=2))
        browser.close()


if __name__=='__main__':main()
