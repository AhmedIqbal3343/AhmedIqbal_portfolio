# Ahmed Iqbal — AI Engineer portfolio

A single-page, static portfolio. It uses plain HTML, CSS and JavaScript, with no framework, no build step and no runtime dependencies.

## Why a static site (stack decision)

- **Hosting:** the current site is on GitHub Pages (`ahmediqbal3343.github.io/AhmedIqbal_portfolio/`), and a static site deploys there as is.
- **Backend:** none is needed. The only dynamic feature is the contact form, which posts to Formspree.
- **Animation:** GSAP and Framer Motion were considered. Every motion in this design (token-streamed headline, scroll-linked progress, a sticky step diagram, FLIP filtering, a panel transition and a canvas field) runs on the Web Animations API, IntersectionObserver and CSS. That saves roughly 70 KB of library code and removes a CDN dependency.
- **Weight:** about 330 KB on first load, before web fonts (13 requests, including the lazy diagrams near the fold). Measured locally at LCP ≈ 0.2 s and CLS 0 (see `docs/QA_REPORT.md`).
- **No-JS fallback:** all content is in the HTML. If JavaScript fails, every section is still readable, and the case studies appear in-page with working anchor links.

## Structure

```
index.html                    the whole site (content lives here)
404.html                      not-found page (GitHub Pages picks it up automatically)
robots.txt, sitemap.xml       SEO
site.webmanifest              icons / theme colour
assets/
  css/styles.css              design tokens (light + dark) and all styles
  js/main.js                  interactions; each feature fails independently
  files/Ahmed_Iqbal_Resume.pdf   ← the résumé the buttons download
  images/
    ahmed-portrait-720.webp, ahmed-portrait-1200.webp   cleaned cut-out portrait
    og-image.png              1200×630 social preview
    favicon.svg, apple-touch-icon.png, icon-512.png
    projects/*.webp           project screenshots from your archive (converted, resized)
    projects/site-*.webp      real client-site screenshots (from your ZIP)
    skills/*.svg              technology logos (Simple Icons, CC0) used by the skills slider
    companies/*.webp          DX Creativ, AKTI and Cognifyz logos (experience timeline)
    social/*.png              LinkedIn, GitHub, Credly and Gmail icons (contact)
    diagrams/*.svg            system/pipeline diagrams (desktop + phone)
docs/
  V2_CHANGES.md               self-audit of v1, what changed in v2, acceptance checklist
  ASSET_MANIFEST.md           every image/logo, its source and status (generated)
  AUDIT_AND_RESEARCH.md       audit of the 5 old versions, research matrix, design direction
  OPEN_QUESTIONS.md           facts to confirm + what each answer would unlock
  QA_REPORT.md                what was tested, results, self-assessment
tools/
  skills.json                 single source of truth for every skill: level, logo, colour, evidence, click target
  build_skills.py             regenerates the skills slider, inventory, skills-data.js and docs/ASSET_MANIFEST.md
  make_diagrams.py            regenerates every diagram from a small spec
  capture_screenshots.py      captures the live client sites and switches the cards to real screenshots
tests/
  test_site.py                82 automated interaction/integrity checks (Playwright)
  a11y_check.py               heading order, labels, alt text, contrast (both themes)
```

## Run locally

```bash
cd portfolio
python3 -m http.server 8765        # any static server works
# open http://localhost:8765/
```

## Test

```bash
pip install playwright && playwright install chromium
python3 -m http.server 8765 &      # from the portfolio folder
python3 tests/test_site.py http://localhost:8765/
python3 tests/a11y_check.py http://localhost:8765/
```

## Deploy (GitHub Pages, same URL as today)

1. In your `AhmedIqbal_portfolio` repository, move the old files into an `old/` folder (or delete them).
2. Copy everything in this folder to the repository root and push to the branch Pages serves.
3. Go to Settings → Pages and confirm the source branch. The site keeps the same URL.
4. If you move to a custom domain, update the URL in four places: `<link rel="canonical">`, the `og:` and `twitter:` URLs in `index.html`, `robots.txt` and `sitemap.xml`.

Netlify, Vercel or Cloudflare Pages also work. Drag the folder in, with no build command and `.` as the output directory.

## Things only you can configure

| What | Where | Why |
|---|---|---|
| **Formspree form** | `action="https://formspree.io/f/xreywzdr"` in `index.html` | Copied from your old site. I couldn't confirm it's still active. Log in to formspree.io and check the form exists, then add your live domain under *Settings → Allowed domains*. If it doesn't exist, create a new form and replace the ID. Until then, the form shows an honest "wasn't sent, email me" message and never a fake success. |
| **Résumé** | `assets/files/Ahmed_Iqbal_Resume.pdf` | Replace the file and keep the same name. Every button points at this path. |
| **Portrait** | `assets/images/ahmed-portrait-720.webp` / `-1200.webp` | To use a new photo, export 720×900 and 1200×1500 WebP (4:5). A transparent background works best. |

## Client-site screenshots

The client-site cards and case studies use the real homepage screenshots you supplied, at `assets/images/projects/site-<name>-1600.webp` and `-800.webp`. To refresh them later, run this on any computer with internet access:

```bash
pip install playwright pillow
playwright install chromium
python3 tools/capture_screenshots.py
```

It overwrites those files. No HTML edits are needed.

## Skills slider

The slider and the full skills inventory are generated from `tools/skills.json`. To add or change a skill:

1. Edit its entry. Set `level` to `pro`, `proj` or `used`; `used` lists project keys; `docs` is the fallback link; `icon` is a Simple Icons slug; `row` (1 or 2) puts it in the slider.
2. Run `python3 tools/build_skills.py`. It rewrites the marked blocks in `index.html`, `assets/js/skills-data.js`, the logo files and `docs/ASSET_MANIFEST.md`.

Clicking a logo opens the first project in its `used` list. A skill with no project opens its official docs in a new tab. Logos are single-colour SVGs from Simple Icons (CC0). The build inlines them into `index.html` as an SVG sprite, so they display even when the page is opened straight from disk or from another host. Every file in `assets/images/skills/` appears on the slider. The slider moves continuously and stops only while the pointer is over a row (or a logo has keyboard focus).

## Diagrams

The system diagrams in `assets/images/diagrams/` are generated, not drawn by hand. Edit the stages in `tools/make_diagrams.py` (the `SPECS` and `SITES` dictionaries) and run `python3 tools/make_diagrams.py`. Each diagram is written in two layouts: `name.svg` for desktop and `name-m.svg` for phones. Only add stages your systems actually have. Once you share the Google Ads agent's real workflow, its diagram is the first one to update.

## Editing content

All content is in `index.html`, in clearly commented sections: HERO, SNAPSHOT, METHOD, EXPERIENCE, WORK, CASE STUDIES, SKILLS, EDUCATION, RESUME and CONTACT.

- **New project card:** copy an `<article class="card">`. Set `data-tags` to any of `agents nlp rag web ml`. The filter counts update automatically.
- **New case study:** add an `<article class="case" id="case-SLUG">` inside `#case-studies`, then link to it with `href="#case-SLUG" data-case="SLUG"`. The panel, deep links and previous/next navigation pick it up automatically.
- **Skill evidence links:** edit the `S` map in `assets/js/main.js` (search for `/* skills evidence */`).
