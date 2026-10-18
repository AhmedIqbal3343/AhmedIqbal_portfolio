# Audit, research and design direction

## 1. Audit of the five previous versions

| File | Positioning | Stack | Notable strengths | Main problems |
|---|---|---|---|---|
| `index.html` (live on GitHub Pages) | "AI Engineer · LLM, Agentic AI & RAG" | Single HTML, Inter + Space Grotesk, Font Awesome, particles | Most complete content; certificate verify links; real repo/demo links for two ML projects | Skill **percentage bars** (Python 95% …); "10+ AI projects shipped" (unverifiable); CGPA **3.93** (résumé: 3.94); **fake form success**: `alert('Message sent successfully!')` fires before Formspree responds; "Demo Walkthrough" links to the LinkedIn *profile*; "View Code" links to the GitHub *homepage*; résumé is a Google Drive link that requires a click-through; Freelance role "Jan 2025 – Present" not on résumé |
| `ind.html` | Same as index | Same | Near-duplicate of index | Same issues as index |
| `inde.html` | "Data Scientist & AI Engineer" | Same | — | CGPA **3.92**; "100% accuracy" claim; "100% client satisfaction"; "5+ Satisfied Clients"; "2+ Years Experience"; dated positioning |
| `indexx.html` | "AI Engineer & AI/ML Researcher" | Fraunces + Hanken Grotesk + IBM Plex Mono | Best typography of the five; **correct** Formspree handling (fetch + success/error states) | Leads with research claims not on the current résumé (CNN-SAM 98% SOTA, papers under review); links to `Ahmed_Iqbal_Final_Resume.pdf` and `Ahmed_Iqbal_CV.pdf`, which aren't in the archive (broken) |
| `indexxx.html` | "AI / ML Engineer" | Bricolage Grotesque + Hanken + JetBrains Mono, fake terminal | Clear "Featured work" framing | `"shipped": 11` in a fake terminal, "Projects shipped & deployed: 11", "measurable impact" without measurements; same broken PDF links |

**Common weaknesses:** generic dark-gradient/glass look; metric tiles with unverifiable numbers; project cards that list tools but not the user's role or the system design; no case studies; inconsistent facts across versions.

**Kept:** certificate verification URLs, real demo/repo links (movie recommender, spam classifier), the Formspree endpoint (pending confirmation), every project screenshot, the portrait photos.

### Contradictions resolved (résumé wins)
- CGPA → **3.94 / 4.00, Gold Medalist**.
- Cognifyz → **Dec 2024 – Feb 2025** (old site: Jan 2025).
- AI Running Coach → listed as **Arfa Kareem** work (old site called it freelance). *Confirm.*
- Freelance AI Engineer role, BCG X simulation, CNN-SAM research, "Databases and SQL" certificate → **left out** (not on résumé). *Confirm whether to add.*
- Résumé spells the second site "GlanPlawPets"; the live domain is **glanpawspets.com**. The site uses GlanPawsPets. *Fix the typo in your résumé.*

## 2. Verified profile summary (from the Oct 2026 résumé PDF)
- AI Engineer, DX Creativ Digital Marketing & Agency, Apr 2026 – present (on-site)
- AI Full Stack Engineer Intern, Arfa Kareem Technologies, Peshawar, Dec 2025 – Feb 2026
- Junior Data Scientist Intern, Cognifyz Technologies (remote), Dec 2024 – Feb 2025
- BS Software Engineering, CECOS University, 2022 – 2026, CGPA 3.94/4.00, Gold Medalist
- Certificates: Stanford ML; Google Advanced Data Analytics; IBM Data Science; IBM Data Analyst
- Links: LinkedIn, GitHub (AhmedIqbal3343), Credly, email ahmedkhanswati82@gmail.com

Note: the Google Drive résumé link couldn't be opened from the build environment, so the uploaded PDF (created 5 Oct 2026) was used.

## 3. Live-site verification (fetched Oct 2026)
| Site | Platform | Verified features | Credit |
|---|---|---|---|
| quickjumpstart.ae | WordPress + Elementor 4.3.2 | Jump-start request form (name, phone, location, vehicle make); call/WhatsApp CTAs; brand pages; Dubai coverage areas; FAQ | Footer: "Powered by DX Creativ" |
| glanpawspets.com | WordPress + Elementor 4.2.3, custom mu-plugin | Per-species service pages; fixed-price packages → pre-filled WhatsApp; 14 areas; FAQ | Footer: "Powered by DX Creativ" |
| batteryonline.ae | Shopify | Make/model/year finder; ~50 brand pages; battery collections; cart; Tabby/cards/cash listed; van-request CTAs; FAQ; blog | No developer credit visible |

Observations you may want to pass on to the client teams: QuickJumpStart lists a contact email on a different domain (info@batteryfly.ae). GlanPawsPets lists "rabbit-safe shampoo" in a package, but its small-pet page says rabbits are never bathed.

## 4. Asset inventory
| File | Project | Used |
|---|---|---|
| Ahmed02.jpg / Ahmed03.jpg / attached cut-outs | Portrait | Cut-out #1 cleaned (halo removed, green spill neutralised) → hero |
| FYP1.png | AcademicGuard | Yes, **cropped to remove "95.3% / <30s / 100K+" UI copy**, which are unverified figures |
| youtube.png | YouTube RAG | Yes |
| classroomagent.png, classroomagent2.png | ClassMate AI | Yes |
| aicoachassistance.png, pharmaCDS.png, scholarlyte3bot.png, drbot3.png, aivideostab.jpeg, salesscraper*.png, movieproject.png, spamproject.png | Earlier projects | Converted to WebP in `assets/images/projects/`; the archive list is text-only to keep the page fast |
| google.*, ibm*, stanford.png, deep.png | Cert logos | Not used (text + verify links instead) |

## 5. Portfolio research (12 references)

| # | Site | First impression | Projects & depth | Recruiter usability | Motion / tech | Take | Avoid |
|---|---|---|---|---|---|---|---|
| 1 | itomdev.com | 3D sketch-textured corridor; JS-only | 4 projects, technical blurbs, no role breakdown | FAQ answers hiring questions | GSAP, R3F, Lenis | One strong concept carried throughout; FAQ-style clarity | Content locked behind JS; long award lists |
| 2 | viram-choksi.in (OS theme) | Boot + lock screen before content | Projects inside an app; depth unclear | Friction before substance | Framer Motion, window manager | Interaction can *be* the demo | Making recruiters "unlock" the page |
| 3 | ameen-abdullah.dev | Strong role line (Three.js/WebGPU) | Consistent card: cover, client, summary, tag, year | Email + FAQ visible; no résumé | GSAP ScrollTrigger, Theatre.js | Consistent card anatomy | Thin role descriptions |
| 4 | manahilmustafa.dev | Video hero + testimonials early | Projects as bare links | Repeated CTAs | Framer Motion, GSAP | Benefit-vs-risk framing; numbered process | Duplicate testimonials; zoom disabled; placeholder OG URL |
| 5 | gopinadipineni.github.io | Clear AI-engineer tagline | No case studies; empty section | Categorised skills | Framer Motion | Specific positioning sentence | Metrics without baselines |
| 6 | iamabdullahportfolio.vercel.app | Headline + proof row + key-value block | Claim → evidence → mini flow diagram; "reported" metrics hedged | **Best recruiter snapshot** | Carousel w/ keyboard | Recruiter snapshot; hedged proof lines; per-project flow diagrams | 12 numbered sections is a lot |
| 7 | tarunpatel.online | VS Code workspace metaphor | MDX case studies: features, challenges, solutions, impact | Contact form with real backend | Tilt glow cards, tsparticles | Case-study template; per-section accents | Generic star-field |
| 8 | brittanychiang.com | One-sentence value prop + socials | Numbered experience; projects with screenshots + metrics | Résumé one click away; skip link | Minimal | Reverse-chronological experience with tech tags; skip link | No visible email |
| 9 | tobiasahlin.com | Name + "I design, tinker, & teach." | Consistent cards; voice-driven copy | Minimal contact | (content is motion work) | Short, declarative voice | `user-scalable=no` |
| 10 | luloai.com (Yesid case study) | Concise hero without marketing language | Grouped by domain; role/stack/impact | Primary CTAs: projects + résumé | — | Two-CTA hero; domain grouping | "Measurable impact" with no measurements |
| 11 | webportfolios.dev (12 portfolios) | Directory | — | — | — | Restrained motion, theme toggle, consistent theming | — |
| 12 | devportfolios.dev (~70 portfolios) | Directory | — | — | — | Breadth of minimal vs animated approaches | — |

**Patterns to avoid:** unverifiable metric tiles, percentage skill bars, content hidden behind loaders/unlock screens, disabled pinch-zoom, testimonials or numbers that don't survive scrutiny, purple/blue gradient + glass.
**Patterns adopted:** recruiter snapshot (6), claim-plus-evidence with provenance (6, 10), case-study template (7), numbered reverse-chronological experience (8), one memorable concept carried through (1), two-CTA hero (10), skip link (8).

## 6. Creative directions considered

| Direction | Recruiter | Distinctive | AI fit | Sophistication | Feasible | Perf/a11y | Maintain |
|---|---|---|---|---|---|---|---|
| A. Dark engineering studio (near-black, luminous accent) | 4 | 2 (very common) | 4 | 4 | 5 | 4 | 5 |
| B. Editorial technical (serif display, generous whitespace) | 5 | 3 | 3 | 5 | 5 | 5 | 5 |
| **C. "Engineering notebook" (chosen)**: cool mineral ground, highlighter accent used like attention highlighting, a dark "bench" band for the work, live system diagrams | 5 | 4 | 5 | 4 | 5 | 5 | 5 |

**Why C:** it's built from the subject's own vocabulary. The hero headline streams in token by token, like model output, and its key nouns are then highlighted the way attention maps mark tokens. The hero background is an attention field: the pointer acts as a query, and the nearest points receive softmax-weighted lines. The Method section is a scroll-linked agent loop. Projects carry provenance badges (live / demo / internal / in development), much as a model card states where its evidence comes from.

## 7. Design system (summary; tokens live in `styles.css`)
- **Colour:** ground `#f1f3f2` (cool, green-biased), surface white, ink `#0f171c`, secondary `#46525a`, metadata `#5f6b72`, hairline `#d3d9d7`, highlighter `#f5d04a` (only ever *behind* ink text), interactive cobalt `#1f48c7`, provenance green/amber. The dark theme is designed separately, not inverted. The work band is always dark.
- **Type:** Schibsted Grotesk (display, 700–800, tight tracking) · Geist (body) · Martian Mono (labels/metadata). Fluid scale `--step--1 … --step-5`. Minimum label size is 0.68rem, used only for mono metadata.
- **Spacing:** 4-based scale (`--s-1 … --s-9`); sections use `clamp(4.5rem, …, 8.5rem)`.
- **Grid:** 1240px max, 12 columns for cards and the snapshot; 20px side gutters (safe-area aware).
- **Motion principles:** one orchestrated entrance (≈1.8 s), then motion only in response to scroll or pointer. Nothing loops except the 4px pulse on the loop ring and the dashed flow connectors. No scroll-jacking. Everything is disabled under `prefers-reduced-motion`, and nothing starts hidden in the first screen.
- **Accessibility rules:** skip link, visible focus ring, `aria-pressed` filters/chips, a native `<dialog>` for case studies (focus moves in and returns), labelled form fields with inline errors, 44px tap targets for icon buttons.
