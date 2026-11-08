# Readability, legibility and accessibility principles for a game's scrolling text / combat log

Method note (read first): in this session WebFetch could not reach learn.microsoft.com, devdocs.xbox.com or gameaccessibilityguidelines.com (DNS blocked by the session's network policy). Findings below therefore come from search-result snippets of those primary pages plus secondary sources. Where a figure was not confirmed from a primary page in this session it is marked **[unverified here]**. Figures that are long-standing published standards (WCAG thresholds) are cited to the W3C page, but the page text itself was not re-fetched.

## 1. What GAG, Xbox Accessibility Guidelines (XAG 101/102/103) and WCAG say that applies to a text log

### Takeaway
All three converge on: readable default size plus user-scalable text; 4.5:1 contrast for information-carrying text (3:1 for large text, non-text UI and inactive elements); contrast measured against the *worst* part of a busy/translucent background; never colour alone; and letting players read at their own pace (pause / scroll back). A combat log is in scope of XAG 101 as HUD/non-player communication text.

### Cited Findings
**Game Accessibility Guidelines (GAG)**
- GAG lists "use an easily readable default font size" as a Basic-tier guideline; text size is among the four most-complained-about issues (with remapping, colour-blindness and subtitle presentation) — [GAG full list](https://gameaccessibilityguidelines.com/full-list/), [GAG Basic](https://gameaccessibilityguidelines.com/basic/) (via search snippets)
- GAG includes "ensure no essential information is conveyed by a fixed colour alone" — [GAG full list](https://gameaccessibilityguidelines.com/full-list/) (via search snippet)
- GAG cognitive guidance (Basic): "Allow players to progress through text prompts at their own pace" — [GAG full list](https://gameaccessibilityguidelines.com/full-list/) (via search snippet)
- IGDA GA-SIG "Game Accessibility Top Ten" repeats text size and colour as top items — [IGDA GA-SIG Top Ten](https://igda-gasig.org/how/game-accessibility-top-ten-se/)
- A secondary summary states a minimum of 28px at 1080p (or equivalent) and that all text should be resizable — [abratabia summary](https://www.abratabia.com/game-accessibility/accessibility-guidelines.php) **[unverified here against XAG/GAG primary text]**

**Xbox Accessibility Guidelines**
- XAG 101 (Text display) scope explicitly covers non-player communications via text, HUD elements, on-screen objectives/instructions and text chat; it includes displaying text in sentence case rather than ALL CAPS or all lowercase — [XAG 101](https://learn.microsoft.com/da-dk/gaming/accessibility/xbox-accessibility-guidelines/101), [devdocs XAG 101 deep dive](https://devdocs.xbox.com/build/game-principles/accessibility/xag-deep-dives/xag-101-text-display) (via search snippets)
- XAG 102 (Contrast): "Text that provides important information or context for gameplay should either have a contrast ratio of at least 4.5:1 against the background, or have an option to adjust contrast to meet these requirements." — [XAG 102](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/102)
- XAG 102: text on inactive elements ≥3:1; an earlier version-history entry gives ≥2.5:1 for disabled elements; placeholder/input text 4.5:1 standard, 3:1 large-scale — [XAG 102](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/102), [XAG version history](https://learn.microsoft.com/en-us/xbox/accessibility/xag-version-history)
- XAG 102: over a non-solid background, measure contrast between text and the *lowest-contrasting area* of the background; for semi-transparent backplates verify the ratio in a worst-case scenario; outlining elements helps — [XAG 102](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/102)
- Microsoft recommends not relying on colour alone and, where unavoidable, letting players choose colours of key elements (XAG 103 "Additional channels for visual and audio cues") — [XAG 103](https://learn.microsoft.com/en-gb/gaming/accessibility/xbox-accessibility-guidelines/103) (via search snippet)
- XAG large-text size thresholds per platform exist in a table that was not retrievable — see Gaps.

**WCAG 2.x** (standard values; pages not re-fetched)
- 1.4.3 Contrast (Minimum, AA): 4.5:1 normal text, 3:1 large text (≥18pt, or ≥14pt bold); 1.4.6 Enhanced (AAA): 7:1 / 4.5:1 — [W3C Understanding 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)
- 1.4.11 Non-text Contrast (AA): icons, graphical objects, focus indicators ≥3:1 against adjacent colours — [U. Iowa WCAG 2.1 SC list](https://itaccessibility.uiowa.edu/wcag21SC)
- 1.4.1 Use of Color (A): colour is not the only visual means of conveying information — [W3C Understanding 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)
- 1.4.12 Text Spacing (AA): no loss of content when user sets line height 1.5× font size, paragraph spacing 2×, letter spacing 0.12×, word spacing 0.16× — [W3C Understanding 1.4.12](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing) (criterion confirmed by search; numeric values from the standard, not re-read here)
- 1.4.8 Visual Presentation (AAA): width ≤80 characters (40 for CJK), line spacing ≥1.5 within paragraphs, not fully justified — [W3C Understanding 1.4.8](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation) **[not re-read here]**
- 2.2.2 Pause, Stop, Hide (A): moving/auto-updating content that starts automatically and lasts >5 s must be pausable/stoppable/hideable — [W3C Understanding 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide) **[not re-read here]**; 2.2.1 Timing Adjustable — [W3C 2.2.1](https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable)

**APCA (WCAG 3 candidate)**
- Lc 90 preferred for body/fluent text; Lc 75 minimum for body text columns; Lc 60 minimum for non-body content text — [APCA Easy Intro](https://git.apcacontrast.com/documentation/APCAeasyIntro.html), [APCA in a Nutshell](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html)
- Size pairings conflict between Myndex documents: Lc 90 at ≥14px/400 and Lc 75 at ≥18px/400 (Nutshell); Bronze lists Lc 75 for 24px/300, 18px/400, 16px/500, 14px/700; compliance doc lists Lc 75 at 16px — [APCA minimum compliance](https://git.apcacontrast.com/documentation/minimum_compliance.html), [Bridge-PCA](https://bridgepca.com/)
- APCA is polarity-aware (light-on-dark scores differently from dark-on-light), motivation in — [WhyAPCA](https://github.com/Myndex/SAPC-APCA/blob/master/documentation/WhyAPCA.md)

### Inferences
- For a log over gameplay art, a solid or high-opacity backplate is the cheapest way to *guarantee* 4.5:1, since XAG measures against the worst background pixel.
- Secondary/dimmed log text (timestamps, dice breakdowns) can drop toward the 3:1 "inactive" tier, but anything carrying outcome (hit/miss/damage/death) should stay ≥4.5:1 (or APCA Lc ≥75).
- Sentence case over ALL CAPS matters for a retro game whose native font may be uppercase-only.

### Gaps
- Exact XAG 101 numeric font sizes (px at 1080p/4K, large-text table) not retrievable: learn.microsoft.com and devdocs.xbox.com were blocked; the 28px figure is secondary.
- AbleGamers/Includification text-specific items were not retrieved.
- Ian Hamilton GDC talk content not retrieved.

## 2. Colour: never colour alone, colour-blind-safe palettes, how many colours, halation

### Takeaway
About 8% of men / 0.5% of women have red-green deficiency, so red=damage/green=heal pairs must carry a second cue (glyph, word, position). Keep semantic colours to ~5-7 (≤8 hue-only); use a CVD-safe set such as Okabe-Ito or Tol Bright; on dark backgrounds avoid pure white and fully saturated hues.

### Cited Findings
- ~8% of men and ~0.5% of women have red-green CVD (≈1 in 12 men, 1 in 200 women); deuteranomaly ~5% of males, protanomaly ~1%; tritan defects are rare and not sex-linked (estimates 0.001%–<0.3%, inconsistent) — [Colour Blind Awareness](https://colourblindawareness.org/?p=409), [WebExhibits](https://webexhibits.org/causesofcolor/2C.html), [types summary](https://color-blind-test.pages.dev/learn/types-of-color-blindness)
- Okabe-Ito 8-colour palette: #E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00, #CC79A7, #000000 (popularised by Bang Wong, Nature Methods 2011) — [thematic okabe_ito](https://rdrr.io/github/rstudio/thematic/man/okabe_ito.html), [ConceptViz reference](https://conceptviz.app/blog/okabe-ito-palette-hex-codes-complete-reference)
- Paul Tol "bright" 7-colour scheme: #4477AA, #EE6677, #228833, #CCBB44, #66CCEE, #AA3377, #BBBBBB; Tol's bright/high-contrast/vibrant/muted schemes are stated colour-blind safe — [khroma tol](https://rdrr.io/cran/khroma/man/tol.html), [LaTeX colorblind package](https://ctan.math.illinois.edu/macros/latex/contrib/colorblind/documentation.pdf)
- Number of categories: accuracy in categorical tasks stable up to ~6 categories then declines sharply — [arXiv subitizing study](https://arxiv.org/pdf/2508.17460); hue-only schemes max ~8 categories — [Wikipedia: Color code](https://en.wikipedia.org/wiki/Color_code); "5-7 colours per view" attributed to Healey/Ware by a secondary blog — [colorpick.app](https://colorpick.app/blog/color-data-visualization-guide) (secondary; primary not checked)
- Only 15-40% of colour-blind people can correctly name surface colour codes with 8-10 categories — [Wikipedia: Color code](https://en.wikipedia.org/wiki/Color_code) (secondary)
- Redundant colour+shape encodings improve categorical discrimination — [CatPAW arXiv](https://arxiv.org/pdf/2602.06792)
- Halation: pure white on pure black gives the strongest "bleed/glow", worse for astigmatism (prevalence quoted 30-47%, inconsistent); recommendations: off-white text, dark-grey background (~RGB 30-40), desaturate accents ~10-20% — [colorcontrast.org](https://www.colorcontrast.org/blog/why-dark-mode-text-hard-to-read/), [atmos.style](https://atmos.style/blog/dark-mode-ui-best-practices), [UX Dictionary](https://uxdictionary.io/article/mitigating-text-halation-in-dark-mode-typography) (design blogs, not clinical)
- Dark mode helps some readers but not all — [BOIA](https://www.boia.org/blog/dark-mode-can-improve-text-readability-but-not-for-everyone)

### Inferences
- Red vs green for "damage dealt vs taken" or "hit vs miss" is the single most common CVD failure; vermilion (#D55E00) vs blue (#0072B2) from Okabe-Ito separates for all three dichromacies. Pair with a word/glyph anyway.
- On a 256-colour VGA palette the designer can pick near-Okabe-Ito entries; pure yellow (#F0E442) is fine on dark but fails contrast on light.
- A log with more than ~6 semantic colours stops being decodable by colour; extra categories should use glyphs or indentation.

### Gaps
- No primary Healey/Ware quotation retrieved. No game-specific study on combat-log colour counts found.

## 3. Typography for logs: monospace vs proportional, size, leading, line length, spacing, emphasis, pixel fonts

### Takeaway
Typographic norms: 45-90 characters per line, leading ~120-145% (WCAG AAA asks 1.5), large x-height, sentence case. There is no controlled study showing monospace scans faster for logs; its demonstrable advantage is column alignment of numbers (tabular figures achieve the same in a proportional font). For tiny bitmap fonts, height matters more than width and ~5 px x-height is the practical floor.

### Cited Findings
- Butterick: average line length 45-90 characters including spaces ("two to three alphabets"); line spacing 120-145% of point size — [Practical Typography](https://practicaltypography.com/), [line-length source](https://git.matthewbutterick.com/mbutterick/pollen-tfl/raw/commit/e6a29bc840708c21fc1d6a2ea80c5bf628707fd2/line-length.html.pm)
- WCAG 1.4.8 (AAA) ≤80 chars, line spacing ≥1.5 — [W3C 1.4.8](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation) [not re-read here]
- Monospace vs proportional: no study tests fonts specifically for reading code/logs; Beier group's letter-width work suggests wider letters aid recognition, and width changes eye movements rather than speed — [Natewave Mono research notes](https://natewave.github.io/natewave-mono/) (secondary summary); iA's "duospace" rationale for near-monospace writing fonts — [iA](https://ia.net/topics/in-search-of-the-perfect-writing-font)
- Tabular (fixed-width) lining figures stop column "jitter"; right-align numbers for comparison; keep consistent decimals; figure spaces pad alignment; monospace is a fallback when a face lacks tabular figures — [Media Atelier](https://www.mediaatelier.com/en-CH/Posts/Tabular-Figures), [Matthew Strom, tables](https://matthewstrom.com/writing/tables), [CreativePro](https://creativepro.com/the-path-to-beautiful-tables-part-iii-working-with-numbers/2/), [Adobe Spectrum table](https://spectrum.adobe.com/page/table)
- Low-resolution legibility: large x-height, wide apertures, low stroke variation help — [Wikipedia: Legibility](https://en.wikipedia.org/wiki/Legibility); reducing glyph width hurts readability less than reducing height — [USPTO 7219309](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7219309); reading speed peaks around x-height ≈0.3° visual angle, critical size ≈0.2° — [Imarc](https://www.imarc.com/blog/best-font-size-for-any-device) (secondary citing Legge-type research)
- Bitmap minimums (designer opinion, not studies): 5x5 cell claimed minimum for reasonably legible Latin without anti-aliasing — [Pixel Five](https://bitfume.com/tools/fonts/pixel-five/); 5x3 "lowest still somewhat readable" — [Hackaday](https://hackaday.com/2026/10/10/slim-type-for-small-screens-with-pixelfonts/)
- Little research on whether hinting/subpixel rendering improves readability — [Readability Research, arXiv 2107.09615](https://arxiv.org/pdf/2107.09615)

### Inferences
- At 320x200 (inference): an 8x8 cell font gives 40 columns, a 6x8 gives ~53, a 5x8/4x6 gives 64-80. 40 is below Butterick's 45 floor; ~53 lands inside the 45-90 band. At 8 px line pitch with ~5-6 px glyph height, leading is ~133-160% — inside the recommended range; going to 7 px pitch loses descender clearance.
- In a bitmap font every glyph is already fixed-width or nearly so, so the monospace question mostly reduces to: keep digits the same width so numbers stack.
- Emphasis: at pixel sizes "bold" usually means +1 px stroke, which can close counters; colour or a glyph prefix is likely more legible than bold (inference; no source found).
- Letter spacing: one empty pixel column between glyphs is the minimum; WCAG's 0.12em equals ~1 px at 8 px size.

### Gaps
- No peer-reviewed study comparing monospace vs proportional for scanning numeric logs found. No controlled study on 5x7/6x8 bitmap legibility found.

## 4. Scanning: F-pattern, front-loading, outcome-first

### Takeaway
Readers scan the left edge and the first words of each line; NN/g finds users typically take in about two words (they tested the first 11 characters) of list items. Put the outcome (HIT/MISS/KILLED, damage) and the actor at the line start; push derivations later.

### Cited Findings
- NN/g "First 2 Words": users typically see ~2 words of each list item; test used the first 11 characters; ~35% of links gave no clue from 11 characters — [NN/g First 2 Words](https://www.nngroup.com/articles/first-2-words-a-signal-for-scanning/)
- F-pattern from NN/g 2006 eye-tracking: fixations concentrate on top lines and left edge; front-load key information — [searchscore summary of NN/g](https://searchscore.io/guides/seo/evidence/nngroup-f-pattern-scanning/), [vocab.design](https://vocab.design/f-pattern)
- Some secondary blogs overstate this (e.g. "first two words critical") — [ATTCK](https://attck.com/blog/how-users-see-scan-and-ignore/) (practitioner heuristic)

### Inferences
- "Kuzak HITS Sadira for 7" scans better than "Kuzak attacks Sadira, rolls 15 + 7 = 22 vs AC 18, hits for 7"; put the roll detail in a dimmed second clause or second line.
- A consistent fixed order (actor, verb/outcome, target, amount, then detail) lets the eye learn column positions.

### Gaps
- NN/g studies are of web pages/links, not streaming logs; transfer is an inference.

## 5. Hierarchy, progressive disclosure, chunking, glyphs, number formatting, verbosity

### Takeaway
Show summary first and detail on demand (progressive disclosure); separate turns/rounds with whitespace or rules; use glyphs as a redundant (not sole) cue meeting 3:1; format maths consistently with aligned numbers; offer filter/verbosity levels.

### Cited Findings
- Progressive disclosure defers secondary information to keep attention on primary content, making interfaces easier to learn and less error-prone — [NN/g video](https://www.nngroup.com/videos/progressive-disclosure/), [Wikipedia](https://en.wikipedia.com/wiki/Progressive_disclosure); empirical evidence for it is described as limited (low-authority source) — [skills.cat](https://skills.cat/skills/bfmcneill/agi-marketplace/progressive-disclosure)
- Non-text cues (icons) need ≥3:1 contrast — [U. Iowa WCAG SC list](https://itaccessibility.uiowa.edu/wcag21SC)
- Redundant shape+colour encoding beats colour alone — [CatPAW](https://arxiv.org/pdf/2602.06792)
- Number alignment/tabular figures — see section 3 sources ([Strom](https://matthewstrom.com/writing/tables))
- Solarized deliberately lowers brightness contrast while keeping hue contrast, uses CIELAB lightness steps symmetric between light/dark, motivated by eye fatigue from high-contrast schemes; built as a 16-colour terminal palette (later revision reportedly moved to OKLab, unconfirmed) — [Solarized README](https://raw.github.com/altercation/solarized/master/README.md), [Wikipedia: Solarized](https://wikipedia.com/wiki/Solarized)

### Inferences
- Solarized's body text (base0 #839496 on base03 #002b36) is roughly 4.7:1 by my recollection, i.e. "low contrast" schemes still clear AA; a log can use a lightness ladder (bright = outcome, mid = normal, dim = detail) in the same way. (Hex/ratio from memory, not fetched.)
- Log viewers (inference from common practice, no source retrieved): log-level colouring paired with a fixed-width level tag (ERROR/WARN) is the dev-tools equivalent of colour + glyph redundancy.
- Turn grouping: a blank line or a dim rule per round, and indenting sub-events (damage, saves) under the action line.
- Verbosity: tiers like Summary / Normal / Full rolls let new players avoid maths while rules-literate players audit dice.

### Gaps
- No sources retrieved on chat UI or game combat-log filter design specifically, or on log-level colouring readability studies.

## 6. Reading speed and pacing for streamed text

### Takeaway
Subtitle norms give a ceiling of ~15-20 characters per second with minimum durations near 0.8-1 s; streamed text should either wait for the player or be pausable and scroll-backable (WCAG 2.2.2; GAG "own pace").

### Cited Findings
- Netflix English adult limit reported as 20 cps (17 children); many other languages 17 cps adult / 13 children; minimum event duration 5/6 s, maximum 7 s — [subtitle-toolset guide](https://subtitle-toolset.pages.dev/guides/subtitle-reading-speed/), [titlevision](https://titlevision.dk/sm/reading_speed.htm) (secondary)
- BBC: 160-180 words per minute (≈15-17 cps by conversion), ~0.3 s per word — [subtitle-toolset guide](https://subtitle-toolset.pages.dev/guides/subtitle-reading-speed/) (secondary)
- Eye-tracking research on subtitle speed — [PLOS ONE / PMC6007935](https://pmc.ncbi.nlm.nih.gov/articles/PMC6007935)
- GAG: allow players to progress through text at their own pace — [GAG full list](https://gameaccessibilityguidelines.com/full-list/)
- WCAG 2.2.2 Pause, Stop, Hide — [W3C 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide) [not re-read here]

### Inferences
- A 50-character log line needs ~2.5-3.3 s at 15-20 cps; several lines per action at AI speed will outrun readers, so a scroll-back buffer or "wait for key" mode is needed.
- Newest-at-bottom with auto-scroll that stops when the user scrolls up is the common chat pattern (inference, unsourced).

### Gaps
- Official Netflix/BBC guides not fetched; no game-specific study on combat-log reading speed found.
