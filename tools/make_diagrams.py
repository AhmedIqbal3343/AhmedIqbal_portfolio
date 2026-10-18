"""Generate the project system diagrams and site-structure maps as static SVG.

Every node in these diagrams corresponds to a stage documented in the résumé or
verified on the live site. Edit SPECS / SITES and re-run:

    python3 tools/make_diagrams.py

Writes assets/images/diagrams/<name>.svg (desktop, 16:10) and <name>-m.svg (phone).
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / 'assets' / 'images' / 'diagrams'
OUT.mkdir(parents=True, exist_ok=True)

# Fixed dark palette: these always sit on the dark "work" band or as figures.
C = dict(bg='#0b1114', grid='#16242a', node='#141f25', stroke='#2e3d43', text='#e9eeec', sub='#9fb0b3',
         label='#8ea1a5', arrow='#6f8489', accent='#f5d04a', core='#1b2a31', ok='#6fd3a8')
SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"


def defs():
    return f'''<defs>
  <pattern id="g" width="25" height="25" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{C['grid']}"/></pattern>
  <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{C['arrow']}"/></marker>
  <marker id="y" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{C['accent']}"/></marker>
</defs>'''


def node(x, y, w, h, lines, sub=None, core=False, fs=19):
    stroke = C['accent'] if core else C['stroke']
    fill = C['core'] if core else C['node']
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="{2 if core else 1.5}"/>']
    n = len(lines) + (1 if sub else 0)
    lh = fs * 1.22
    top = y + h / 2 - (n * lh) / 2 + fs * .82
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x + w / 2}" y="{top + i * lh:.1f}" text-anchor="middle" font-family="{SANS}" font-size="{fs}" font-weight="600" fill="{C["text"]}">{escape(ln)}</text>')
    if sub:
        out.append(f'<text x="{x + w / 2}" y="{top + len(lines) * lh + 2:.1f}" text-anchor="middle" font-family="{MONO}" font-size="{fs * .72:.1f}" fill="{C["sub"]}">{escape(sub)}</text>')
    return '\n'.join(out)


def label(x, y, text, anchor='start', color=None, fs=14):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{MONO}" font-size="{fs}" letter-spacing="1.2" fill="{color or C["label"]}">{escape(text)}</text>'


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">\n'
            f'<title>{escape(title)}</title>\n{defs()}\n<rect width="{w}" height="{h}" fill="{C["bg"]}"/>\n<rect width="{w}" height="{h}" fill="url(#g)"/>\n{body}\n</svg>\n')


def edge_label(x, y, text, color):
    tw = len(text) * 8.2 + 14
    return (f'<rect x="{x - tw / 2:.1f}" y="{y - 13}" width="{tw:.1f}" height="22" rx="11" fill="{C["bg"]}" stroke="{color}" stroke-width="1"/>'
            f'<text x="{x}" y="{y + 3}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{color}">{escape(text)}</text>')


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0], u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])


def lane_chip(x, y, text, fs=14):
    tw = len(text) * fs * .63 + 4
    return f'<rect x="{x - 6}" y="{y - fs - 1}" width="{tw + 12:.0f}" height="{fs + 9}" fill="{C["bg"]}"/>' + label(x, y, text, fs=fs)


def horizontal(spec):
    W, M, GAP = 1000, 40, 30
    NH = 112
    lanes_y = []
    y = 92
    for lane in spec['lanes']:
        lanes_y.append(y)
        y += NH + 118
    H = lanes_y[-1] + NH + 74
    body = [label(M, 48, spec['kicker'].upper(), color=C['accent'], fs=15),
            f'<text x="{M}" y="74" font-family="{SANS}" font-size="15" fill="{C["sub"]}">{escape(spec["title"])}</text>']
    boxes = []
    chips = []
    for li, lane in enumerate(spec['lanes']):
        n = len(lane['nodes'])
        w = (W - 2 * M - (n - 1) * GAP) / n
        ly = lanes_y[li] + 26
        chips.append(lane_chip(M, ly - 8, lane['name'].upper()))
        row = []
        for i, nd in enumerate(lane['nodes']):
            x = M + i * (w + GAP)
            body.append(node(round(x, 1), ly, round(w, 1), NH, nd['t'], nd.get('s'), nd.get('core', False)))
            row.append((x, ly, w, NH))
            if i:
                px = row[i - 1][0] + w
                body.append(f'<line x1="{px + 3:.1f}" y1="{ly + NH / 2}" x2="{x - 4:.1f}" y2="{ly + NH / 2}" stroke="{C["arrow"]}" stroke-width="2" marker-end="url(#a)"/>')
        boxes.append(row)
    labels = []
    for e in spec.get('edges', []):
        (a_l, a_i), (b_l, b_i) = e['from'], e['to']
        ax, ay, aw, ah = boxes[a_l][a_i]
        bx, by, bw, bh = boxes[b_l][b_i]
        col = C['accent'] if e.get('feedback') else C['arrow']
        mk = 'y' if e.get('feedback') else 'a'
        dash = ' stroke-dasharray="7 6"' if e.get('feedback') else ''
        x1 = ax + aw / 2 + (e.get('dx1', 0))
        x2 = bx + bw / 2 + (e.get('dx2', 0))
        if b_l > a_l:
            y1, y2 = ay + ah + 3, by - 5
        else:
            y1, y2 = ay - 3, by + bh + 5
        my = (y1 + y2) / 2
        body.append(f'<path d="M{x1:.1f} {y1:.1f} C{x1:.1f} {my:.1f} {x2:.1f} {my:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{col}" stroke-width="2"{dash} marker-end="url(#{mk})"/>')
        if e.get('label'):
            lx, ly2 = bez((x1, y1), (x1, my), (x2, my), (x2, y2), e.get('t', .5))
            labels.append(edge_label(lx, ly2 + 4, e['label'], col))
    body += chips + labels
    body.append(label(M, H - 26, spec['note']))
    return svg(W, H, '\n'.join(body), spec['title'])


def vertical(spec):
    """Phone layout: one column per lane, nodes stacked."""
    lanes = spec['lanes']
    W, M, GAP = 640, 20, 50
    cols = len(lanes)
    cw = (W - 2 * M - (cols - 1) * GAP) / cols
    NH, VG = 96, 30
    top = 108
    maxn = max(len(l['nodes']) for l in lanes)
    H = top + maxn * (NH + VG) + 70
    body = [label(M, 44, spec['kicker'].upper(), color=C['accent'], fs=16),
            f'<text x="{M}" y="72" font-family="{SANS}" font-size="17" fill="{C["sub"]}">{escape(spec["title"])}</text>']
    boxes = []
    vchips = []
    for li, lane in enumerate(lanes):
        x = M + li * (cw + GAP)
        vchips.append(lane_chip(x, top - 10, lane['name'].upper(), fs=14))
        col = []
        for i, nd in enumerate(lane['nodes']):
            y = top + i * (NH + VG)
            lines = nd.get('m', nd['t'])
            body.append(node(round(x, 1), y, round(cw, 1), NH, lines, nd.get('s'), nd.get('core', False), fs=20))
            col.append((x, y, cw, NH))
            if i:
                body.append(f'<line x1="{x + cw / 2:.1f}" y1="{y - VG + 2}" x2="{x + cw / 2:.1f}" y2="{y - 4}" stroke="{C["arrow"]}" stroke-width="2" marker-end="url(#a)"/>')
        boxes.append(col)
    for e in spec.get('edges', []):
        (a_l, a_i), (b_l, b_i) = e['from'], e['to']
        ax, ay, aw, ah = boxes[a_l][a_i]
        bx, by, bw, bh = boxes[b_l][b_i]
        col = C['accent'] if e.get('feedback') else C['arrow']
        mk = 'y' if e.get('feedback') else 'a'
        dash = ' stroke-dasharray="7 6"' if e.get('feedback') else ''
        if b_l > a_l:
            x1, x2 = ax + aw + 2, bx - 5
        else:
            x1, x2 = ax - 2, bx + bw + 5
        y1, y2 = ay + ah / 2 + 14, by + bh / 2 - 14
        mx = (x1 + x2) / 2
        body.append(f'<path d="M{x1:.1f} {y1:.1f} C{mx:.1f} {y1:.1f} {mx:.1f} {y2:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{col}" stroke-width="2"{dash} marker-end="url(#{mk})"/>')
    body += vchips
    body.append(label(M, H - 26, spec.get('note_m', spec['note']), fs=13))
    return svg(W, H, '\n'.join(body), spec['title'])


SPECS = {
    'agent-web': dict(
        kicker='System diagram · simplified', title='Agent workflow that builds client websites (DX Creativ)',
        note='Stages from the résumé. Internal prompts and tools not shown.',
        note_m='Stages from the résumé. Internals not shown.',
        lanes=[
            dict(name='Build', nodes=[
                dict(t=['Client brief']),
                dict(t=['LLM agent'], s='prompts · tools', core=True),
                dict(t=['Generated', 'site pages']),
                dict(t=['Output-quality', 'evaluation']),
                dict(t=['Deploy to', 'WordPress'], s='2 sites live'),
            ]),
            dict(name='Improve', nodes=[
                dict(t=['Real client use']),
                dict(t=['Failure modes', 'surface']),
                dict(t=['Fix prompts &', 'pipeline code'], core=True),
            ]),
        ],
        edges=[dict(**{'from': (0, 4), 'to': (1, 0)}, label='in use', t=.22),
               dict(**{'from': (1, 2), 'to': (0, 1)}, feedback=True, label='feedback', t=.78)],
    ),
    'ads-agent': dict(
        kicker='Conceptual diagram · verified stages only', title='Google Ads agent and its improvement loop (DX Creativ)',
        note='Account-level actions the agent takes are not shown.',
        note_m='Account-level actions not shown.',
        lanes=[
            dict(name='Agent run', nodes=[
                dict(t=['Campaign &', 'search-term data']),
                dict(t=['Retrieval &', 'configuration']),
                dict(t=['LLM agent'], s='prompts', core=True),
                dict(t=['Agent output']),
            ]),
            dict(name='My improvement loop', nodes=[
                dict(t=['Analyse campaign', '& search datasets'], m=['Analyse', 'campaign data']),
                dict(t=['Diagnose', 'weak output']),
                dict(t=['Update prompts,', 'retrieval, config'], core=True),
            ]),
        ],
        edges=[dict(**{'from': (0, 0), 'to': (1, 0)}),
               dict(**{'from': (0, 3), 'to': (1, 1)}, label='review', t=.25),
               dict(**{'from': (1, 2), 'to': (0, 2)}, feedback=True, label='ship fixes', t=.75)],
    ),
    'academicguard': dict(
        kicker='Pipeline diagram · in development', title='AcademicGuard: fine-tuning and inference',
        note='No scores shown: the project is still in development.',
        note_m='No scores shown: still in development.',
        lanes=[
            dict(name='Training', nodes=[
                dict(t=['Labelled AI vs', 'human text'], m=['Labelled', 'AI / human text']),
                dict(t=['Clean, normalise,', 'tokenise'], m=['Clean &', 'tokenise']),
                dict(t=['Fine-tune', 'pretrained', 'Transformer'], m=['Fine-tune', 'Transformer'], s='HF · PyTorch', core=True),
                dict(t=['Held-out', 'evaluation'], s='P · R · confusion'),
            ]),
            dict(name='Inference', nodes=[
                dict(t=['PDF / DOCX', 'paper']),
                dict(t=['Section-aware', 'extraction']),
                dict(t=['Fine-tuned', 'classifier'], core=True),
                dict(t=['LLM summary']),
                dict(t=['Per-section', 'report']),
            ]),
        ],
        edges=[dict(**{'from': (0, 2), 'to': (1, 2)}, label='checkpoint')],
    ),
    'doc-rag': dict(
        kicker='System diagram · client work', title='Document-grounded RAG (Arfa Kareem Technologies)',
        note='Answers are constrained to retrieved passages.',
        lanes=[
            dict(name='Ingestion', nodes=[
                dict(t=['PDFs &', 'documents']),
                dict(t=['Parse &', 'clean']),
                dict(t=['Chunk']),
                dict(t=['Embed']),
                dict(t=['Vector', 'index'], core=True),
            ]),
            dict(name='Query', nodes=[
                dict(t=['Question']),
                dict(t=['Embed', 'query']),
                dict(t=['Top-k', 'retrieval'], core=True),
                dict(t=['LLM, limited', 'to passages'], m=['LLM, limited', 'to passages']),
                dict(t=['Answer with', 'sources']),
            ]),
        ],
        edges=[dict(**{'from': (0, 4), 'to': (1, 2)}, label='search', dx1=0)],
    ),
    'youtube-rag': dict(
        kicker='Pipeline diagram', title='YouTube Knowledge Assistant',
        note='Generation limited to retrieved transcript passages.',
        note_m='Grounded in retrieved passages only.',
        lanes=[
            dict(name='Ingest', nodes=[
                dict(t=['Lecture video']), dict(t=['Transcript']), dict(t=['Segment &', 'clean']), dict(t=['Embed']), dict(t=['ChromaDB'], core=True)]),
            dict(name='Ask', nodes=[
                dict(t=['Question']), dict(t=['Retrieve', 'passages'], core=True), dict(t=['Grounded', 'answer'], s='FastAPI')]),
        ],
        edges=[dict(**{'from': (0, 4), 'to': (1, 1)}, label='search')],
    ),
}

# ---------------------------------------------------------------- site maps
SITES = {
    'quickjumpstart': dict(url='quickjumpstart.ae', stack='WordPress · Elementor', sections=[
        ('nav', 'Header · contact · navigation'), ('hero', 'Hero: jump start in Dubai · Call · WhatsApp'),
        ('form', 'Request-a-jump-start form'), ('grid', 'Car-brand grid → brand pages'), ('text', 'Weak-battery warning signs'),
        ('cards', 'Services'), ('steps', '5-step process'), ('text', 'Coverage areas'), ('cards', 'Team'), ('text', 'FAQ'), ('nav', 'Footer')]),
    'glanpawspets': dict(url='glanpawspets.com', stack='WordPress · Elementor', sections=[
        ('nav', 'Header · services menu'), ('hero', 'Hero: van at your door · Book · Call'), ('grid', 'Photo gallery'),
        ('cards', 'Why Glan Paws'), ('steps', 'How it works (3 steps)'), ('cards', 'Mobile services'), ('grid', 'Pets we groom'),
        ('form', 'Packages & prices → WhatsApp'), ('text', 'Areas covered'), ('text', 'FAQ'), ('nav', 'Footer')]),
    'batteryonline': dict(url='batteryonline.ae', stack='Shopify', sections=[
        ('nav', 'Header · navigation · cart'), ('hero', 'Hero · Send a van'), ('form', 'Car finder: make / model / year'),
        ('cards', 'Best sellers'), ('grid', 'Product carousel'), ('steps', '4-step process'), ('cards', 'Why Dubai drivers'),
        ('grid', 'Battery brands'), ('text', 'Coverage areas'), ('text', 'FAQ'), ('nav', 'Footer')]),
}

H_OF = dict(nav=34, hero=118, form=64, grid=64, text=40, cards=64, steps=56)


def block(kind, x, y, w, h):
    s = C['stroke']
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{C["node"]}" stroke="{s}" stroke-width="1.2"/>']
    if kind == 'hero':
        out.append(f'<rect x="{x + 18}" y="{y + 20}" width="{w * .42:.0f}" height="16" rx="4" fill="{C["text"]}" opacity=".85"/>')
        out.append(f'<rect x="{x + 18}" y="{y + 44}" width="{w * .3:.0f}" height="10" rx="3" fill="{C["sub"]}" opacity=".6"/>')
        out.append(f'<rect x="{x + 18}" y="{y + 70}" width="86" height="26" rx="13" fill="{C["accent"]}"/>')
        out.append(f'<rect x="{x + 112}" y="{y + 70}" width="86" height="26" rx="13" fill="none" stroke="{C["sub"]}"/>')
        out.append(f'<rect x="{x + w * .58:.0f}" y="{y + 14}" width="{w * .38:.0f}" height="{h - 28}" rx="6" fill="{C["grid"]}"/>')
    elif kind == 'grid':
        n = 8
        cw = (w * .62 - (n - 1) * 8) / n
        for i in range(n):
            out.append(f'<rect x="{x + w * .36 + i * (cw + 8):.1f}" y="{y + 14}" width="{cw:.1f}" height="{h - 28}" rx="4" fill="{C["grid"]}"/>')
    elif kind == 'cards':
        for i in range(3):
            out.append(f'<rect x="{x + w * .36 + i * (w * .21):.1f}" y="{y + 12}" width="{w * .19:.1f}" height="{h - 24}" rx="5" fill="{C["grid"]}"/>')
    elif kind == 'form':
        for i in range(3):
            out.append(f'<rect x="{x + w * .36 + i * (w * .17):.1f}" y="{y + 20}" width="{w * .15:.1f}" height="{h - 40}" rx="4" fill="none" stroke="{C["sub"]}" stroke-opacity=".6"/>')
        out.append(f'<rect x="{x + w * .87:.1f}" y="{y + 18}" width="{w * .1:.1f}" height="{h - 36}" rx="12" fill="{C["accent"]}"/>')
    elif kind == 'steps':
        for i in range(5):
            cx = x + w * .4 + i * (w * .12)
            out.append(f'<circle cx="{cx:.1f}" cy="{y + h / 2}" r="10" fill="{C["grid"]}" stroke="{C["sub"]}" stroke-opacity=".6"/>')
    return out


def sitemap(name, d, W, mobile=False):
    M = 30 if mobile else 40
    top = 70
    fs = 17 if mobile else 15
    body = [f'<rect x="{M}" y="22" width="{W - 2 * M}" height="34" rx="9" fill="{C["node"]}" stroke="{C["stroke"]}"/>',
            *[f'<circle cx="{M + 20 + i * 16}" cy="39" r="4.5" fill="{C["stroke"]}"/>' for i in range(3)],
            f'<text x="{M + 80}" y="44" font-family="{MONO}" font-size="{fs}" fill="{C["sub"]}">{d["url"]}</text>',
            f'<text x="{W - M - 14}" y="44" text-anchor="end" font-family="{MONO}" font-size="{fs - 2}" fill="{C["label"]}">{escape(d["stack"])}</text>']
    y = top
    secs = d['sections'][:8] if mobile else d['sections']
    for kind, text in secs:
        h = H_OF[kind] * (1.15 if mobile else 1)
        if mobile and kind == 'hero':
            h = 130
        body += block(kind, M, y, W - 2 * M, h) if not mobile else block('text' if kind not in ('hero',) else kind, M, y, W - 2 * M, h)
        ty = y + (28 if kind == 'hero' and not mobile else h / 2 + 5) if not (kind == 'hero') else y + h - 14
        tx = M + 16
        body.append(f'<text x="{tx}" y="{ty:.0f}" font-family="{MONO}" font-size="{fs}" fill="{C["text"] if kind == "hero" else C["sub"]}">{escape(text)}</text>')
        y += h + 8
    H = y + 46
    body.append(label(M, H - 18, 'PAGE STRUCTURE MAPPED FROM THE LIVE SITE · NOT A SCREENSHOT', fs=12 if not mobile else 13))
    return svg(W, int(H), '\n'.join(body), f'Homepage structure of {d["url"]}')


if __name__ == '__main__':
    for k, spec in SPECS.items():
        (OUT / f'{k}.svg').write_text(horizontal(spec), encoding='utf-8')
        (OUT / f'{k}-m.svg').write_text(vertical(spec), encoding='utf-8')
    # Site-structure maps were used before real screenshots existed. Pass --sitemaps to regenerate them.
    import sys
    if '--sitemaps' in sys.argv:
        for k, d in SITES.items():
            (OUT / f'site-{k}.svg').write_text(sitemap(k, d, 1000), encoding='utf-8')
            (OUT / f'site-{k}-m.svg').write_text(sitemap(k, d, 640, mobile=True), encoding='utf-8')
    print('wrote', len(list(OUT.glob('*.svg'))), 'files to', OUT)
