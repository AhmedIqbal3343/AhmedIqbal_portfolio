# QA report (v3: skills slider and ZIP assets)

Tested 18 Oct 2026 against a local static server, with Playwright and Chromium 1.56.

## Limits of this test run
- **Web fonts:** Google Fonts is blocked in the sandbox, so every screenshot used fallback fonts. Check the typography on the deployed site.
- **External links** (docs, LinkedIn, live sites): checked for correct URLs and `target`/`rel` attributes, not for whether they load.
- **Lighthouse and axe-core:** couldn't be installed. Browser timing metrics and a custom structure and contrast check were used instead.
- **Contact form:** delivery tested against a mocked Formspree only.
- **Browser:** Chromium only.

## Automated tests: `tests/test_site.py`
```
PASS no empty "#" links                                                                    | []
PASS every in-page anchor has a target                                                     | 17 anchors, missing=[]
PASS external links use target=_blank rel=noopener                                         | 55 external; bad=[]
PASS all local assets return 200                                                           | 36 checked; bad=[]
PASS résumé PDF serves as a real PDF                                                       | status=200 bytes=298313
PASS résumé download filename                                                              | Ahmed_Iqbal_Resume.pdf
PASS résumé download actually downloads                                                    | Ahmed_Iqbal_Resume.pdf
PASS current location is Rawalpindi everywhere; Peshawar only in history                   | Peshawar lines kept: ['Peshawar · On-site', 'CECOS University of IT & Emerging Sciences, Peshawar']
PASS Gold Medalist plaque fully visible in first screen (desktop)                          | [581.53125, 673.765625, 900]
PASS every featured project and site card has a loaded, alt-texted visual                  | 9 cards; bad=[]
PASS no CSS/WAAPI animation left running once settled (slider drift is a pausable scroll)  | []
PASS slider: every node has a real destination (case, section or safe external link)       | 34 nodes; bad=[]
PASS slider: loop copies hidden from AT and tab order                                      | 68
PASS slider: every node has a descriptive accessible name                                
PASS slider + inventory: all logo SVGs exist and are SVG                                   | 34 logos; bad=[]
PASS slider: rows drift in opposite directions                                             | [1393, 2551] -> [1434, 2510]
PASS slider: no pause / arrow controls (continuous marquee)                              
PASS slider: every logo renders (inline SVG, no CORS dependency)                           | []
PASS slider: every file in assets/images/skills appears on the slider                      | 34 on slider vs 34 files; missing=[]
PASS slider: hover pauses the row and shows a tooltip with evidence                        | NumPy | USED IN PROFESSIONAL WORK · AI, ML & DEEP LEARNING | Cognifyz Technologies | Arfa Kareem Technologies |  | Click
PASS slider: resumes moving when the pointer leaves                                        | 1445 -> 1469
PASS slider: clicking PyTorch opens the AcademicGuard case study                         
PASS slider: tools without a project open official docs safely                             | ['https://docs.n8n.io/', '_blank', 'noopener']
PASS slider: keyboard focus scrolls the node into view and shows its tooltip               | ['docker', True, True]
PASS every slider skill is also in the full inventory                                      | []
PASS company logos load in the experience timeline                                         | [True, True, True]
PASS nav → Experience scrolls & highlights                                                 | top=80 current=Experience
PASS nav → Projects scrolls & highlights                                                   | top=80 current=Projects
PASS nav → Skills scrolls & highlights                                                     | top=80 current=Skills
PASS nav → Contact scrolls & highlights                                                    | top=80 current=Contact
PASS theme toggle switches and persists                                                    | dark dark rgb(12, 18, 20)
PASS theme toggles back                                                                  
PASS filter "agents" shows matching projects                                               | expected=7 visible=7 badge=7 status="Showing 7 of 17 projects"
PASS filter "nlp" shows matching projects                                                  | expected=8 visible=8 badge=8 status="Showing 8 of 17 projects"
PASS filter "rag" shows matching projects                                                  | expected=3 visible=3 badge=3 status="Showing 3 of 17 projects"
PASS filter "web" shows matching projects                                                  | expected=5 visible=5 badge=5 status="Showing 5 of 17 projects"
PASS filter "ml" shows matching projects                                                   | expected=5 visible=5 badge=5 status="Showing 5 of 17 projects"
PASS filter "all" shows matching projects                                                  | expected=17 visible=17 badge=17 status="Showing 17 of 17 projects"
PASS case study opens in panel with right content                                          | True AcademicGuard http://localhost:8765/#case-academicguard
PASS focus moves into the panel                                                            | dialog-h
PASS next / previous case navigation                                                       | YouTube Knowledge Assistant / AcademicGuard
PASS Escape closes panel, clears hash, restores focus                                      | closed=True url=http://localhost:8765/#contact focus=academicguard
PASS browser Back closes panel                                                           
PASS method-step link opens case                                                         
PASS close button closes panel                                                           
PASS deep link #case-agent-web opens                                                       | open=True imgs_ok=True
PASS deep link #case-ads-agent opens                                                       | open=True imgs_ok=True
PASS deep link #case-academicguard opens                                                   | open=True imgs_ok=True
PASS deep link #case-youtube-rag opens                                                     | open=True imgs_ok=True
PASS deep link #case-classmate opens                                                       | open=True imgs_ok=True
PASS deep link #case-doc-rag opens                                                         | open=True imgs_ok=True
PASS deep link #case-batteryonline opens                                                   | open=True imgs_ok=True
PASS skill chip shows evidence                                                             | Fine-tuning 1
PASS evidence link opens the case                                                        
PASS copy email puts address on clipboard + feedback                                       | ahmedkhanswati82@gmail.com / Email address copied
PASS email button is a mailto to the right address                                         | mailto:ahmedkhanswati82@gmail.com?subject=AI%20Engineer%20opportunity
PASS empty submit shows 3 errors and focuses first                                         | 3 3 f-name
PASS valid submit posts to Formspree and shows success                                     | Message sent. Thanks — I’ll reply to the email address you gave.
PASS form resets after success                                                           
PASS server error shows honest failure + email fallback                                    | Your message wasn’t sent. Form not found. Please email me directly at ahmedkhanswati82@gmail.com.
PASS network failure shows failure, never fake success                                     | Your message wasn’t sent. The form service could not be reached. Please email me directly at ahmedkhanswati82@gmail.com.
PASS first Tab reaches skip link                                                         
PASS skip link jumps to main                                                             
PASS initial load (local, no throttling)                                                   | {"lcp": 180, "cls": 0, "dcl": 207, "requests": 13, "kb": 420}
PASS no console errors (desktop)                                                           | []
PASS mobile: no horizontal overflow                                                        | [375, 375]
PASS mobile: Gold Medalist plaque visible in first screen                                  | [347.0625, 454.953125, 740]
PASS mobile menu opens                                                                     | hidden_before=True expanded=true visible=True
PASS mobile menu link navigates and closes menu                                          
PASS mobile menu closes on Escape                                                        
PASS no horizontal overflow at 320px                                                       | [320, 320]
PASS no horizontal overflow at 360px                                                       | [360, 360]
PASS no horizontal overflow at 414px                                                       | [414, 414]
PASS no horizontal overflow at 768px                                                       | [768, 768]
PASS no horizontal overflow at 1024px                                                      | [1024, 1024]
PASS tap targets ≥ 24px (outside running text)                                             | []
PASS mobile: case panel is full width                                                      | 375
PASS no console errors (mobile)                                                            | []
PASS reduced motion: nothing hidden, no streaming/caret                                    | pre=0 caret=0 tok=0
PASS reduced motion (OS setting): slider does not drift                                    | [1392, 2552] [1392, 2552]
PASS no-JS: case studies readable in page; card links jump to them                         | cases=True top=79.5625
PASS 404 page renders with link home                                                     

82/82 passed
```
Page weight went up to about 430 KB and 47 requests, because each technology logo is a small separate SVG (about 1 KB each). LCP and CLS were unaffected locally.

## Accessibility check: `tests/a11y_check.py`
Both themes: no duplicate IDs, every image has alt text, one `h1`, no skipped heading levels, all controls named, all fields labelled. The only contrast flags are the two known false positives from the header's `color-mix()` background.

## Slider-specific checks
- The loop copies are hidden from screen readers and the tab order, but stay clickable.
- Keyboard focus pauses the row, scrolls the node into view and shows the same tooltip as hover.
- Continuous drift with no pause controls; hovering stops the row and moving away resumes it (tested).
- Logos are inline SVG and were also verified rendering from `file://`.
- Rows are native horizontal scrollers, so swiping and trackpad scrolling work on touch devices.
- When the visitor's OS asks for reduced motion there is no drift; the rows stay swipeable.
- Drift runs only while the slider is on screen and the tab is visible.

## Visual review
1440×900 light and dark, and 390×844: slider rows, tooltip, inventory, browser-framed screenshots, timeline logos, contact icons and case-study screenshots. Fixed during review: underlined URL text in the browser frames, and mismatched screenshot heights in the case study.
