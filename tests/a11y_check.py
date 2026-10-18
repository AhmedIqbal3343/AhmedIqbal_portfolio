import asyncio, json
from playwright.async_api import async_playwright
JS = r'''() => {
  const out = {};
  const ids = [...document.querySelectorAll('[id]')].map(e => e.id); out.dupIds = ids.filter((x,i) => ids.indexOf(x) !== i);
  out.imgNoAlt = [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length;
  const hs = [...document.querySelectorAll('main h1, main h2, main h3, main h4')].filter(h => h.offsetParent);
  let prev = 1, jumps = []; hs.forEach(h => { const l = +h.tagName[1]; if (l > prev + 1) jumps.push(h.tagName + ':' + h.textContent.slice(0,30)); prev = l; });
  out.h1count = document.querySelectorAll('h1').length; out.headingJumps = jumps;
  out.unnamed = [...document.querySelectorAll('a, button')].filter(e => e.offsetParent && !(e.getAttribute('aria-label') || e.textContent.trim())).map(e => e.outerHTML.slice(0,80));
  out.unlabelled = [...document.querySelectorAll('input:not([type=hidden]), textarea')].filter(i => !document.querySelector(`label[for="${i.id}"]`)).map(i => i.id);
  // contrast of visible text against its effective background
  function rgb(s){ const m = s.match(/[\d.]+/g); return m ? m.map(Number) : null; }
  function lum([r,g,b]){ [r,g,b] = [r,g,b].map(v => { v/=255; return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); }); return .2126*r + .7152*g + .0722*b; }
  function bgOf(el){ while (el) { const c = getComputedStyle(el).backgroundColor; const v = rgb(c); if (v && (v.length < 4 || v[3] > .5)) return v.slice(0,3); el = el.parentElement; } return [255,255,255]; }
  const bad = []; const seen = new Set();
  document.querySelectorAll('body *').forEach(el => {
    if (!el.offsetParent || el.closest('svg, canvas, .hp, .paper')) return;
    const direct = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!direct) return;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity < .5) return;
    if (getComputedStyle(el).backgroundImage.includes('gradient') && el.tagName === 'MARK') return;
    const fg = rgb(cs.color).slice(0,3), bg = bgOf(el);
    const L1 = lum(fg), L2 = lum(bg); const ratio = (Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
    const size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 600;
    const need = (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5;
    const key = el.tagName + cs.color + bg;
    if (ratio < need && !seen.has(key)) { seen.add(key); bad.push(`${ratio.toFixed(2)} <${need} ${el.tagName}.${el.className} "${el.textContent.trim().slice(0,30)}"`); }
  });
  out.lowContrast = bad;
  return out;
}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for scheme in ('light','dark'):
            pg = await b.new_page(viewport={'width':1280,'height':800}, color_scheme=scheme, reduced_motion='reduce')
            await pg.route('**/fonts.g*/**', lambda r: r.abort())
            await pg.goto((__import__('sys').argv[1] if len(__import__('sys').argv) > 1 else 'http://localhost:8765/')); await pg.wait_for_timeout(500)
            print(scheme, json.dumps(await pg.evaluate(JS), indent=1, ensure_ascii=False))
            await pg.close()
        await b.close()
asyncio.run(main())
