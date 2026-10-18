# Version 2: what changed and why

## Self-audit of v1: the ten weaknesses
1. **Three of six featured projects had no visual.** The Agent web system, Google Ads agent and Document RAG showed text "flow chips" that read as wireframes.
2. **Client-site cards were typographic boxes.** They had no structure or imagery, and no path to real screenshots.
3. **Gold Medalist was buried.** It appeared in a small grey pill and one snapshot cell.
4. **Wrong location.** Peshawar appeared in the hero, the snapshot and the structured data. The current location is Rawalpindi.
5. **Projects started too far down the page.** A tall, scroll-driven Method section came first.
6. **The project grid was repetitive.** Equal-sized cards gave no hierarchy between flagship and minor work.
7. **The hero didn't show evidence.** A long paragraph of prose, no links to proof, and no location indicator.
8. **Too much continuous motion.** The attention field drifted on its own, a pulse circled the loop, and dashed connectors animated constantly.
9. **No résumé access in the header.** The footer also had no professional links.
10. **Small visual inconsistencies.** Mixed card radii, an empty-looking Method sticky column on mobile, and an overlong Method section.

## What v2 does
| Area | Change |
|---|---|
| Project visuals | Five original system and pipeline diagrams (`assets/images/diagrams/*.svg`), each with a desktop and a phone layout, generated from `tools/make_diagrams.py`. Every node maps to a stage on your résumé, and each diagram is labelled (e.g. "Conceptual diagram · verified stages only"). The real screenshots (YouTube assistant, ClassMate, AcademicGuard) are kept, and AcademicGuard combines its UI screenshot with its pipeline diagram. |
| Client sites | The page structure of each live homepage, mapped section by section, labelled **"Page structure · not a screenshot"**. `tools/capture_screenshots.py` captures the real sites and swaps them in automatically (see README). |
| Showcase layout | Three alternating spotlight rows (large visual; problem / role / notable; stack; actions), then a three-up tile row, the client sites, and the earlier-projects list. Projects now come directly after the snapshot. |
| Hero | Location and availability chips, name, explicit role line, a shorter thesis, three evidence links to case studies (agents, RAG, fine-tuning), and a stronger CTA row. |
| Gold Medalist | A dark plaque with a metallic laurel-medal emblem, overlapping the portrait in the first screen on desktop and mobile. There is also a gold-tinted "Recognition" cell in the snapshot and a full award card in Education. Only documented facts are used: Gold Medalist, BS Software Engineering, CECOS University, CGPA 3.94/4.00, 2022–2026. |
| Location | Rawalpindi, Pakistan in the hero, snapshot, contact (with PKT/UTC+5), footer, meta description, OG/Twitter text, JSON-LD `addressLocality` and the social image. Peshawar remains only where it is historical: the CECOS campus and the Arfa Kareem internship. |
| Motion | Removed all continuous motion. The field only reacts while a pointer is over the hero, then fades. The loop fills once when scrolled into view. The plaque gets a single sheen. The tests check that no animation is running after the page settles. |
| Navigation | Résumé button in the header. Projects is second in the nav. The footer has Email, LinkedIn, GitHub, Credly and Résumé links. |
| Social image | Regenerated with the location and the Gold Medalist plaque. |

## Acceptance checklist (each item checked; see QA_REPORT.md for evidence)
- [x] Visibly more polished and distinctive: before/after screenshots reviewed at 1440, 768 and 390px.
- [x] Identity clear in the first screen: name, role line, thesis, location, Gold Medalist and CTAs are all above the fold at 1440×900.
- [x] Gold Medalist prominent and accurate: the test checks the plaque is fully inside the first viewport on desktop and mobile.
- [x] Location is Rawalpindi: the test checks body text, JSON-LD and `<head>`, with Peshawar only in historical lines.
- [x] Every featured project has a meaningful visual or a labelled technical diagram: the test checks all 9 cards have a loaded image with alt text.
- [ ] **Genuine website screenshots: not done.** The build environment can't reach the three sites. Structure maps stand in, clearly labelled, and the one-command capture script replaces them.
- [x] No fake interfaces, metrics or screenshots: diagrams contain no numbers; structure maps are labelled "not a screenshot".
- [x] Cards communicate problem, contribution and technical value: spotlights have Problem / My role / Notable rows; tiles have a "Built:" line.
- [x] Motion restrained: no continuous animation after settle (tested), and reduced motion is respected (tested).
- [x] Critical content needs no hover or waiting: the first frame is complete, reveals apply only below the fold, and the no-JS render is tested.
- [x] Responsive: no horizontal overflow at 320, 360, 375, 414, 768, 1024 and 1440px (tested).
- [x] Résumé, project links, navigation and contact work (tested; Formspree mocked).
- [x] No broken images or missing files: all local assets return 200 (tested).
- [x] Accessibility and reduced motion checked (tests/a11y_check.py, tests/test_site.py).
- [x] Tests executed: 67/67 interaction checks pass.
- [x] Run and deploy instructions: README.md.
