"""Interaction + integrity tests for the portfolio. Run against a local static server."""
import asyncio, json, re, sys
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/'
results = []
def check(name, ok, detail=''):
    results.append((name, bool(ok), detail))

async def new_page(b, **kw):
    ctx = await b.new_context(**kw)
    pg = await ctx.new_page()
    pg._errs = []
    pg.on('console', lambda m: pg._errs.append(m.text) if m.type == 'error' and 'ERR_FAILED' not in m.text and '422' not in m.text else None)
    pg.on('pageerror', lambda e: pg._errs.append('PAGEERROR ' + str(e)))
    await pg.route(re.compile(r'https://fonts\.(googleapis|gstatic)\.com/.*'), lambda r: r.abort())
    return ctx, pg

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()

        # ---------- desktop ----------
        ctx, pg = await new_page(b, viewport={'width': 1440, 'height': 900})
        await ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin=URL.rstrip('/'))
        await pg.goto(URL, wait_until='load'); await pg.wait_for_timeout(800)

        # 1. no bare "#" links, all in-page anchors resolve
        hrefs = await pg.eval_on_selector_all('a[href]', 'as => as.map(a => a.getAttribute("href"))')
        check('no empty "#" links', all(h not in ('#', '', 'javascript:void(0)') for h in hrefs), str([h for h in hrefs if h in ('#', '')]))
        anchors = sorted({h for h in hrefs if h.startswith('#')})
        missing = [h for h in anchors if not await pg.evaluate('id => !!document.getElementById(id)', h[1:])]
        check('every in-page anchor has a target', not missing, f'{len(anchors)} anchors, missing={missing}')

        # 2. external links open safely
        ext = await pg.eval_on_selector_all('a[href^="http"]', 'as => as.map(a => [a.href, a.target, a.rel])')
        bad = [e for e in ext if e[1] != '_blank' or 'noopener' not in e[2]]
        check('external links use target=_blank rel=noopener', not bad, f'{len(ext)} external; bad={bad[:3]}')

        # 3. local assets all load (img src/srcset, pdf, css, js, icons)
        locals_ = await pg.evaluate('''() => {
          const s = new Set();
          document.querySelectorAll('img').forEach(i => { s.add(i.getAttribute('src')); (i.getAttribute('srcset')||'').split(',').forEach(x => x.trim() && s.add(x.trim().split(' ')[0])); });
          document.querySelectorAll('a[href^="assets/"], link[href^="assets/"], link[href$=".webmanifest"], script[src]').forEach(e => s.add(e.getAttribute('href') || e.getAttribute('src')));
          return [...s].filter(x => x && !x.startsWith('http'));
        }''')
        locals_ += ['robots.txt', 'sitemap.xml', '404.html', 'assets/images/og-image.png', 'assets/images/icon-512.png']
        bad_assets = []
        for a in locals_:
            r = await pg.request.get(URL + a)
            if r.status != 200: bad_assets.append((a, r.status))
        check('all local assets return 200', not bad_assets, f'{len(locals_)} checked; bad={bad_assets}')
        r = await pg.request.get(URL + 'assets/files/Ahmed_Iqbal_Resume.pdf')
        body = await r.body()
        check('résumé PDF serves as a real PDF', r.status == 200 and body[:4] == b'%PDF', f'status={r.status} bytes={len(body)}')
        dl = await pg.get_attribute('#resume a[download]', 'download')
        check('résumé download filename', dl == 'Ahmed_Iqbal_Resume.pdf', dl)
        async with pg.expect_download() as d:
            await pg.click('#resume a[download]')
        dwn = await d.value
        check('résumé download actually downloads', dwn.suggested_filename == 'Ahmed_Iqbal_Resume.pdf', dwn.suggested_filename)

        # 3b. v2 requirements: location, gold medal, project visuals, restrained motion
        body_txt = await pg.evaluate('document.body.innerText')
        html_src = await pg.content()
        pesh = [l.strip() for l in body_txt.splitlines() if 'Peshawar' in l]
        allowed = all(('CECOS' in l) or ('On-site' in l) for l in pesh)
        check('current location is Rawalpindi everywhere; Peshawar only in history',
              'Rawalpindi, Pakistan' in body_txt and allowed and '"addressLocality": "Rawalpindi"' in html_src and 'Peshawar' not in html_src.split('<body')[0],
              f'Peshawar lines kept: {pesh}')
        await pg.goto(URL, wait_until='load'); await pg.wait_for_timeout(2500)
        box = await pg.evaluate('(() => { const r = document.querySelector(".plaque").getBoundingClientRect(); return [r.top, r.bottom, innerHeight]; })()')
        gold_txt = await pg.inner_text('.plaque')
        check('Gold Medalist plaque fully visible in first screen (desktop)', box[0] >= 0 and box[1] <= box[2] and 'Gold Medalist' in gold_txt, str(box))
        vis = await pg.evaluate("""async () => {
          const out = [];
          for (const card of document.querySelectorAll('#work .spot, #work .tile')) {
            const imgs = [...card.querySelectorAll('.viz img')];
            for (const i of imgs) { i.loading = 'eager'; if (!i.complete) await new Promise(r => { i.onload = i.onerror = r; }); }
            out.push([card.querySelector('h3').textContent, imgs.length, imgs.every(i => i.naturalWidth > 0), imgs.every(i => i.alt && i.alt.length > 10)]);
          }
          return out; }""")
        bad = [v for v in vis if not (v[1] >= 1 and v[2] and v[3])]
        check('every featured project and site card has a loaded, alt-texted visual', not bad and len(vis) == 9, f'{len(vis)} cards; bad={bad}')
        await pg.wait_for_timeout(5000)
        running = await pg.evaluate('document.getAnimations().filter(a => a.playState === "running").map(a => a.animationName || a.constructor.name)')
        check('no CSS/WAAPI animation left running once settled (slider drift is a pausable scroll)', not running, str(running))

        # 3c. skills slider
        await pg.goto(URL, wait_until='load'); await pg.wait_for_timeout(600)
        info = await pg.evaluate("""() => {
          const orig = [...document.querySelectorAll('#stack-slider .snode:not([data-clone]) a')];
          const clones = [...document.querySelectorAll('#stack-slider .snode[data-clone]')];
          const bad = orig.filter(a => { const h = a.getAttribute('href'); return !(h.startsWith('http') ? (a.target === '_blank' && a.rel.includes('noopener')) : !!document.getElementById(h.slice(1))); }).map(a => a.dataset.skill);
          const cloneOk = clones.every(c => c.getAttribute('aria-hidden') === 'true' && [...c.querySelectorAll('a')].every(a => a.tabIndex === -1));
          const logos = [...new Set([...document.querySelectorAll('.snode:not([data-clone]) a')].map(a => 'assets/images/skills/' + a.dataset.skill + '.svg'))];
          return { n: orig.length, clones: clones.length, bad, cloneOk, logos, labels: orig.every(a => a.getAttribute('aria-label').length > 20) };
        }""")
        check('slider: every node has a real destination (case, section or safe external link)', info['n'] >= 30 and not info['bad'], f"{info['n']} nodes; bad={info['bad']}")
        check('slider: loop copies hidden from AT and tab order', info['clones'] == 2 * info['n'] and info['cloneOk'], str(info['clones']))
        check('slider: every node has a descriptive accessible name', info['labels'])
        bad_logo = []
        for u in info['logos']:
            r = await pg.request.get(URL + u)
            if r.status != 200 or b'<svg' not in (await r.body())[:200]: bad_logo.append(u)
        check('slider + inventory: all logo SVGs exist and are SVG', info['logos'] and not bad_logo, f"{len(info['logos'])} logos; bad={bad_logo}")
        await pg.evaluate('document.getElementById("stack-slider").scrollIntoView({block: "center"})'); await pg.mouse.move(5, 5)
        await pg.wait_for_timeout(500)
        x0 = await pg.evaluate('[...document.querySelectorAll(".srow-viewport")].map(v => v.scrollLeft)')
        await pg.wait_for_timeout(1500)
        x1 = await pg.evaluate('[...document.querySelectorAll(".srow-viewport")].map(v => v.scrollLeft)')
        check('slider: rows drift in opposite directions', x1[0] > x0[0] and x1[1] < x0[1], f'{x0} -> {x1}')
        check('slider: no pause / arrow controls (continuous marquee)', await pg.locator('#slider-toggle, #slider-prev, #slider-next').count() == 0)
        rend = await pg.evaluate("""() => {
          const files = new Set(), shown = [];
          for (const svg of document.querySelectorAll('#stack-slider .snode:not([data-clone]) .snode-logo')) {
            const id = svg.querySelector('use').getAttribute('href').slice(4);
            const sym = document.getElementById('sk-' + id); const box = svg.getBoundingClientRect();
            const ok = !!sym && sym.querySelector('path') && box.width >= 20 && getComputedStyle(svg).fill !== 'none';
            shown.push([id, !!ok]);
          }
          return shown; }""")
        import os
        files = sorted(f[:-4] for f in os.listdir(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'skills')) if f.endswith('.svg'))
        ids = sorted(r[0] for r in rend)
        check('slider: every logo renders (inline SVG, no CORS dependency)', all(r[1] for r in rend), str([r for r in rend if not r[1]]))
        check('slider: every file in assets/images/skills appears on the slider', ids == files, f'{len(ids)} on slider vs {len(files)} files; missing={sorted(set(files)-set(ids))}')
        # hover whichever copy of a logo is currently on screen, like a real visitor would
        pt = await pg.evaluate("""(() => { const vp = document.querySelectorAll('.srow-viewport')[0].getBoundingClientRect();
            const a = [...document.querySelectorAll('.srow')[0].querySelectorAll('.snode a')].find(a => { const r = a.getBoundingClientRect(); return r.left > vp.left + 150 && r.right < vp.right - 150; });
            const r = a.querySelector('.snode-dot').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, a.dataset.skill]; })()""")
        await pg.mouse.move(pt[0], pt[1]); await pg.wait_for_timeout(300)
        h0 = await pg.evaluate('document.querySelectorAll(".srow-viewport")[0].scrollLeft'); await pg.wait_for_timeout(800)
        h1 = await pg.evaluate('document.querySelectorAll(".srow-viewport")[0].scrollLeft')
        tipv = await pg.is_visible('#stip'); tipt = await pg.inner_text('#stip')
        check('slider: hover pauses the row and shows a tooltip with evidence', h0 == h1 and tipv and 'Click' in tipt, tipt.replace('\n', ' | ')[:120])
        await pg.mouse.move(5, 5); await pg.wait_for_timeout(300)
        r0 = await pg.evaluate('document.querySelectorAll(".srow-viewport")[0].scrollLeft'); await pg.wait_for_timeout(800)
        r1 = await pg.evaluate('document.querySelectorAll(".srow-viewport")[0].scrollLeft')
        check('slider: resumes moving when the pointer leaves', r1 != r0, f'{r0} -> {r1}')
        await pg.locator('.srow').nth(0).locator('.snode:not([data-clone]) a[data-skill="pytorch"]').click(); await pg.wait_for_timeout(600)
        check('slider: clicking PyTorch opens the AcademicGuard case study', await pg.evaluate('document.getElementById("case-dialog").open') and await pg.inner_text('#dialog-body h2') == 'AcademicGuard')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        n8n = await pg.evaluate('(() => { const a = document.querySelector(".snode:not([data-clone]) a[data-skill=n8n]"); return [a.href, a.target, a.rel]; })()')
        check('slider: tools without a project open official docs safely', n8n[0].startswith('https://docs.n8n.io') and n8n[1] == '_blank' and 'noopener' in n8n[2], str(n8n))
        await pg.focus('.snode:not([data-clone]) a[data-skill="docker"]'); await pg.wait_for_timeout(400)
        fv = await pg.evaluate("""(() => { const a = document.activeElement; const r = a.getBoundingClientRect(); const v = a.closest('.srow-viewport').getBoundingClientRect();
            return [a.dataset.skill, r.left >= v.left - 1 && r.right <= v.right + 1, !document.getElementById('stip').hidden]; })()""")
        check('slider: keyboard focus scrolls the node into view and shows its tooltip', fv[0] == 'docker' and fv[1] and fv[2], str(fv))
        chip = await pg.evaluate('(() => { const ids = [...document.querySelectorAll(".snode:not([data-clone]) a")].map(a => a.dataset.skill); return ids.filter(id => !document.querySelector(`.chip[data-skill="${id}"]`)); })()')
        check('every slider skill is also in the full inventory', not chip, str(chip))
        cl = await pg.evaluate('[...document.querySelectorAll(".org-logo")].map(i => i.complete && i.naturalWidth > 0)')
        check('company logos load in the experience timeline', len(cl) == 3 and all(cl), str(cl))

        # 4. nav links scroll to section and set aria-current
        for label, target in [('Experience', 'experience'), ('Projects', 'work'), ('Skills', 'skills'), ('Contact', 'contact')]:
            await pg.click(f'.nav-list a[href="#{target}"]'); await pg.wait_for_timeout(1300)
            top = await pg.evaluate(f'document.getElementById("{target}").getBoundingClientRect().top')
            cur = await pg.evaluate('(document.querySelector(".nav-list a[aria-current]")||{}).textContent')
            check(f'nav → {label} scrolls & highlights', -5 < top < 160 and cur == label, f'top={top:.0f} current={cur}')

        # 5. theme toggle + persistence
        await pg.click('#theme-btn')
        t1 = await pg.evaluate('document.documentElement.dataset.theme')
        await pg.wait_for_timeout(600)
        bg = await pg.evaluate('getComputedStyle(document.body).backgroundColor')
        await pg.reload(); await pg.wait_for_timeout(300)
        t2 = await pg.evaluate('document.documentElement.dataset.theme')
        check('theme toggle switches and persists', t1 == 'dark' and t2 == 'dark' and bg == 'rgb(12, 18, 20)', f'{t1} {t2} {bg}')
        await pg.click('#theme-btn')
        check('theme toggles back', await pg.evaluate('document.documentElement.dataset.theme') == 'light')

        # 6. filters
        await pg.evaluate('document.getElementById("work").scrollIntoView()')
        for f in ['agents', 'nlp', 'rag', 'web', 'ml', 'all']:
            await pg.click(f'.filter[data-filter="{f}"]'); await pg.wait_for_timeout(650)
            exp = await pg.evaluate(f'''[...document.querySelectorAll("#work .card, #work .archive-item")].filter(el => "{f}"==="all" || el.dataset.tags.split(" ").includes("{f}")).length''')
            vis = await pg.evaluate('[...document.querySelectorAll("#work .card, #work .archive-item")].filter(el => el.offsetParent !== null).length')
            badge = await pg.inner_text(f'.filter[data-filter="{f}"] .n')
            pressed = await pg.get_attribute(f'.filter[data-filter="{f}"]', 'aria-pressed')
            status = await pg.inner_text('#filter-status')
            check(f'filter "{f}" shows matching projects', exp == vis == int(badge) and pressed == 'true' and str(vis) in status, f'expected={exp} visible={vis} badge={badge} status="{status}"')

        # 7. case study panel
        await pg.click('a[data-case="academicguard"].btn'); await pg.wait_for_timeout(700)
        open_ = await pg.evaluate('document.getElementById("case-dialog").open')
        h = await pg.inner_text('#dialog-body h2')
        check('case study opens in panel with right content', open_ and h == 'AcademicGuard' and pg.url.endswith('#case-academicguard'), f'{open_} {h} {pg.url}')
        foc = await pg.evaluate('document.activeElement.id')
        check('focus moves into the panel', foc == 'dialog-h', foc)
        await pg.click('#case-next'); await pg.wait_for_timeout(300)
        h2 = await pg.inner_text('#dialog-body h2')
        await pg.click('#case-prev'); await pg.wait_for_timeout(300)
        h3 = await pg.inner_text('#dialog-body h2')
        check('next / previous case navigation', h2 == 'YouTube Knowledge Assistant' and h3 == 'AcademicGuard', f'{h2} / {h3}')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
        closed = not await pg.evaluate('document.getElementById("case-dialog").open')
        foc = await pg.evaluate('document.activeElement.getAttribute("data-case")')
        check('Escape closes panel, clears hash, restores focus', closed and '#case-' not in pg.url and foc == 'academicguard', f'closed={closed} url={pg.url} focus={foc}')
        await pg.click('a[data-case="youtube-rag"].btn'); await pg.wait_for_timeout(500)
        await pg.go_back(); await pg.wait_for_timeout(400)
        check('browser Back closes panel', not await pg.evaluate('document.getElementById("case-dialog").open'))
        # links inside step text open cases too
        await pg.click('.step a[href="#case-classmate"]'); await pg.wait_for_timeout(500)
        check('method-step link opens case', await pg.inner_text('#dialog-body h2') == 'ClassMate AI')
        await pg.click('#case-close'); await pg.wait_for_timeout(400)
        check('close button closes panel', not await pg.evaluate('document.getElementById("case-dialog").open'))
        # every case can render
        slugs = await pg.eval_on_selector_all('.cases-fallback .case', 'as => as.map(a => a.id.slice(5))')
        for s in slugs:
            await pg.goto(URL + '#case-' + s); await pg.reload(); await pg.wait_for_timeout(400)
            ok = await pg.evaluate('document.getElementById("case-dialog").open')
            imgs = await pg.evaluate('[...document.querySelectorAll("#dialog-body img")].every(i => i.complete && i.naturalWidth > 0)')
            check(f'deep link #case-{s} opens', ok and imgs, f'open={ok} imgs_ok={imgs}')
        await pg.goto(URL); await pg.wait_for_timeout(300)

        # 8. skills
        await pg.click('.chip[data-skill="finetune"]')
        t = await pg.inner_text('#ev-title'); n = await pg.evaluate('document.querySelectorAll("#ev-list li").length')
        check('skill chip shows evidence', t == 'Fine-tuning' and n == 1, f'{t} {n}')
        await pg.click('#ev-list a'); await pg.wait_for_timeout(500)
        check('evidence link opens the case', await pg.inner_text('#dialog-body h2') == 'AcademicGuard')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)

        # 9. copy email
        await pg.click('#copy-email'); await pg.wait_for_timeout(200)
        clip = await pg.evaluate('navigator.clipboard.readText()')
        toast = await pg.inner_text('#toast')
        check('copy email puts address on clipboard + feedback', clip == 'ahmedkhanswati82@gmail.com' and 'copied' in toast, f'{clip} / {toast}')
        mailto = await pg.get_attribute('.email-row a[href^="mailto:"]', 'href')
        check('email button is a mailto to the right address', mailto.startswith('mailto:ahmedkhanswati82@gmail.com'), mailto)

        # 10. form validation + submission states (Formspree mocked)
        await pg.click('#f-submit')
        errs = await pg.evaluate('[...document.querySelectorAll(".field .err")].map(e => e.textContent).filter(Boolean).length')
        inv = await pg.evaluate('document.querySelectorAll("[aria-invalid=true]").length')
        foc = await pg.evaluate('document.activeElement.id')
        check('empty submit shows 3 errors and focuses first', errs == 3 and inv == 3 and foc == 'f-name', f'{errs} {inv} {foc}')
        posted = {}
        async def ok_route(route):
            posted['body'] = route.request.post_data; posted['accept'] = route.request.headers.get('accept')
            await route.fulfill(status=200, content_type='application/json', body='{"ok":true}')
        await pg.route('https://formspree.io/**', ok_route)
        await pg.fill('#f-name', 'Test Recruiter'); await pg.fill('#f-email', 'recruiter@example.com'); await pg.fill('#f-msg', 'We are hiring an Applied AI Engineer for our LLM platform team.')
        await pg.click('#f-submit'); await pg.wait_for_timeout(500)
        st = await pg.inner_text('#form-status'); state = await pg.get_attribute('#form-status', 'data-state')
        check('valid submit posts to Formspree and shows success', state == 'ok' and 'Message sent' in st and 'Test Recruiter' in (posted.get('body') or '') and posted.get('accept') == 'application/json', st)
        check('form resets after success', await pg.input_value('#f-name') == '')
        await pg.unroute('https://formspree.io/**')
        await pg.route('https://formspree.io/**', lambda r: r.fulfill(status=422, content_type='application/json', body='{"errors":[{"message":"Form not found."}]}'))
        await pg.fill('#f-name', 'A B'); await pg.fill('#f-email', 'a@b.co'); await pg.fill('#f-msg', 'x' * 30)
        await pg.click('#f-submit'); await pg.wait_for_timeout(500)
        st = await pg.inner_text('#form-status')
        check('server error shows honest failure + email fallback', await pg.get_attribute('#form-status', 'data-state') == 'error' and 'wasn’t sent' in st and 'Form not found' in st and 'ahmedkhanswati82@gmail.com' in st, st)
        await pg.unroute('https://formspree.io/**')
        await pg.route('https://formspree.io/**', lambda r: r.abort())
        await pg.click('#f-submit'); await pg.wait_for_timeout(500)
        st = await pg.inner_text('#form-status')
        check('network failure shows failure, never fake success', await pg.get_attribute('#form-status', 'data-state') == 'error', st)

        # 11. keyboard: skip link + focus visible
        await pg.goto(URL); await pg.keyboard.press('Tab')
        check('first Tab reaches skip link', await pg.evaluate('document.activeElement.className') == 'skip-link')
        await pg.keyboard.press('Enter'); await pg.wait_for_timeout(300)
        check('skip link jumps to main', pg.url.endswith('#main'))

        # 12. performance-ish numbers
        await pg.goto(URL, wait_until='load'); await pg.wait_for_timeout(2500)
        perf = await pg.evaluate('''() => new Promise(res => {
          let lcp = 0, cls = 0;
          new PerformanceObserver(l => l.getEntries().forEach(e => lcp = e.startTime)).observe({type: 'largest-contentful-paint', buffered: true});
          new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) cls += e.value; })).observe({type: 'layout-shift', buffered: true});
          setTimeout(() => {
            const nav = performance.getEntriesByType('navigation')[0];
            const res = performance.getEntriesByType('resource');
            const bytes = res.reduce((s, r) => s + (r.transferSize || r.encodedBodySize || 0), 0) + (nav.transferSize || 0);
            res(  {lcp: Math.round(lcp), cls: +cls.toFixed(4), dcl: Math.round(nav.domContentLoadedEventEnd), requests: res.length + 1, kb: Math.round(bytes / 1024)});
          }, 500);
        })'''.replace('res(  {', 'resolve({').replace('new Promise(res =>', 'new Promise(resolve =>'))
        check('initial load (local, no throttling)', perf['cls'] < 0.1, json.dumps(perf))
        check('no console errors (desktop)', not pg._errs, str(pg._errs[:5]))
        await ctx.close()

        # ---------- mobile ----------
        ctx, pg = await new_page(b, viewport={'width': 375, 'height': 740}, is_mobile=True, has_touch=True)
        await pg.goto(URL, wait_until='load'); await pg.wait_for_timeout(600)
        sw = await pg.evaluate('[document.documentElement.scrollWidth, innerWidth]')
        check('mobile: no horizontal overflow', sw[0] <= sw[1], str(sw))
        box = await pg.evaluate('(() => { const r = document.querySelector(".plaque").getBoundingClientRect(); return [r.top, r.bottom, innerHeight]; })()')
        check('mobile: Gold Medalist plaque visible in first screen', box[0] >= 0 and box[1] <= box[2], str(box))
        vis_nav = await pg.is_visible('.nav-list a[href="#skills"]')
        await pg.tap('#menu-btn'); await pg.wait_for_timeout(450)
        exp = await pg.get_attribute('#menu-btn', 'aria-expanded'); vis = await pg.is_visible('.nav-list a[href="#skills"]')
        check('mobile menu opens', not vis_nav and exp == 'true' and vis, f'hidden_before={not vis_nav} expanded={exp} visible={vis}')
        await pg.tap('.nav-list a[href="#skills"]'); await pg.wait_for_timeout(1200)
        check('mobile menu link navigates and closes menu', await pg.get_attribute('#menu-btn', 'aria-expanded') == 'false' and -5 < await pg.evaluate('document.getElementById("skills").getBoundingClientRect().top') < 160)
        await pg.tap('#menu-btn'); await pg.wait_for_timeout(300); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        check('mobile menu closes on Escape', await pg.get_attribute('#menu-btn', 'aria-expanded') == 'false')
        for w in (320, 360, 414, 768, 1024):
            await pg.set_viewport_size({'width': w, 'height': 800}); await pg.wait_for_timeout(250)
            sw = await pg.evaluate('[document.documentElement.scrollWidth, innerWidth]')
            check(f'no horizontal overflow at {w}px', sw[0] <= sw[1], str(sw))
        tiny = await pg.evaluate('''() => [...document.querySelectorAll('a, button, input, textarea')].filter(e => { const r = e.getBoundingClientRect(); return e.offsetParent && r.width > 0 && (r.height < 24 || r.width < 24) && !e.closest('p, li, dd, .hp') }).map(e => e.outerHTML.slice(0, 60))''')
        check('tap targets ≥ 24px (outside running text)', not tiny, str(tiny[:4]))
        await pg.set_viewport_size({'width': 375, 'height': 740})
        await pg.evaluate('document.getElementById("work").scrollIntoView()'); await pg.wait_for_timeout(300)
        await pg.tap('a[data-case="classmate"].btn'); await pg.wait_for_timeout(600)
        dw = await pg.evaluate('document.getElementById("case-dialog").getBoundingClientRect().width')
        check('mobile: case panel is full width', abs(dw - 375) < 2, str(dw))
        check('no console errors (mobile)', not pg._errs, str(pg._errs[:5]))
        await ctx.close()

        # ---------- reduced motion ----------
        ctx, pg = await new_page(b, viewport={'width': 1280, 'height': 800}, reduced_motion='reduce')
        await pg.goto(URL, wait_until='load'); await pg.wait_for_timeout(400)
        pre = await pg.evaluate('document.querySelectorAll(".pre").length')
        caret = await pg.evaluate('document.querySelectorAll(".caret").length')
        toks = await pg.evaluate('document.querySelectorAll(".tok").length')
        check('reduced motion: nothing hidden, no streaming/caret', pre == 0 and caret == 0 and toks == 0, f'pre={pre} caret={caret} tok={toks}')
        await pg.evaluate('document.getElementById("stack-slider").scrollIntoView()'); await pg.wait_for_timeout(400)
        r0 = await pg.evaluate('[...document.querySelectorAll(".srow-viewport")].map(v => v.scrollLeft)'); await pg.wait_for_timeout(1500)
        r1 = await pg.evaluate('[...document.querySelectorAll(".srow-viewport")].map(v => v.scrollLeft)')
        check('reduced motion (OS setting): slider does not drift', r0 == r1, f'{r0} {r1}')
        await ctx.close()

        # ---------- JavaScript disabled ----------
        ctx, pg = await new_page(b, viewport={'width': 1280, 'height': 800}, java_script_enabled=False)
        await pg.goto(URL, wait_until='load')
        cases_vis = await pg.is_visible('#case-agent-web')
        await pg.click('a[data-case="academicguard"].btn'); await pg.wait_for_timeout(2500)
        top = await pg.evaluate('document.getElementById("case-academicguard").getBoundingClientRect().top')
        hero_vis = await pg.is_visible('#hero-title')
        check('no-JS: case studies readable in page; card links jump to them', cases_vis and hero_vis and -5 < top < 200, f'cases={cases_vis} top={top}')
        await ctx.close()

        # ---------- 404 ----------
        ctx, pg = await new_page(b)
        r = await pg.goto(URL + '404.html')
        check('404 page renders with link home', r.status == 200 and await pg.is_visible('a[href="./"]'))
        await ctx.close()
        await b.close()

    w = max(len(n) for n, _, _ in results)
    for n, ok, d in results:
        print(('PASS ' if ok else 'FAIL ') + n.ljust(w) + ('  | ' + d if d else ''))
    print(f'\n{sum(ok for _, ok, _ in results)}/{len(results)} passed')

asyncio.run(main())
