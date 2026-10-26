# Engine guide

Contracts of the template. Read before writing slides or a builder. Design rules (theme, chart grammar, narrative, geometry) are in `spec.md`.

Contents: 1 File layout · 2 DATA and `{{ }}` binding · 3 Slide kinds and markup · 4 Builder catalogue · 5 Helpers and tokens · 6 Flags, keys and `?check` · 7 Add a builder · 8 Regression test for engine changes · 9 Gotchas

## 1. File layout

`scripts/assemble.py <deck-dir>` writes one HTML file in this order. Each section opens with a banner `/* ===== N. NAME [ENGINE|CONTENT] ===== */`.

| # | Section | Comes from | Type |
|---|---|---|---|
| (head) | doctype, title, HOW THIS FILE WORKS comment | `engine/00_head.html` | ENGINE |
| 1 | THEME: tokens for light, dark, paper, and the BRAND SLOT | `engine/10_theme.css`; slot filled from `brands/<brand>/brand.css` | ENGINE + BRAND SLOT |
| 2 | BASE: stage, slide kinds, head, footer, chips, notes, overview, print | `engine/20_base.css` | ENGINE |
| 3 | SPRITES: about 40 line icons `i-*`, logo symbols | `engine/30_sprites.html`; logo from `brands/<brand>/logo.svgfrag` | ENGINE |
| 4 | SLIDES | `<deck>/slides.html` | CONTENT |
| (chrome) | closes the stage, adds `#notes`, `#overview`, `#help`, opens `<script>` | `engine/35_chrome.html` | ENGINE |
| 5 | DATA | `<deck>/data.js` | CONTENT |
| 6 | HELPERS | `engine/60_helpers.js` | ENGINE |
| 7 | BUILDERS | `engine/70_builders.js` | ENGINE |
| 7b | DECK BUILDERS (optional) | `<deck>/builders.js` | CONTENT |
| 8 | BOOT: binding, render, navigation, `?check`; closes `</script></body></html>` | `engine/80_boot.js` | ENGINE |

`deck.json`:

```json
{ "title": "page title", "out": "../my-deck.html", "brand": "ethos", "wordmark": "Placeholder logo text", "inject": { "rows": "inject/rows.json" } }
```

- `brand`: a folder name in `assets/brands/`, or `null` for the neutral themes (then `<html data-theme="light">`, no brand theme in the `T` cycle). With a brand the page opens in the brand theme and `T` cycles brand, light, dark, paper.
- `wordmark`: text of the neutral placeholder logo; ignored when a brand supplies a logo.
- `inject`: `name: file` replaces the marker `/*INJECT:name*/[]` (or `/*INJECT:name*/{}` for an object) inside `data.js` with that JSON, minified. Use it for a large table that a script generates (see `example-chest-pain/gen_rows.py`), so `data.js` stays readable.
- `out` is relative to the deck folder; parent folders are created.

## 2. DATA and `{{ }}` binding

Numbers live only in `DATA`. Everything else cites them.

```js
const DECK = { name: 'Footer name', people: [{ key: 'ab', name: 'Alex Brown', role: 'Role' }] };   // everyone listed shows on cover and closing, in order (two or three fit); role is optional
const PHOTO = /*INJECT:photo*/{};                                                                     // key -> data URI (scripts/photo_to_datauri.py) or relative path; no key gives initials
const DATA = { delay: { id: 'delay', title: '', unit: '', kind: 'counted', window: '', denominator: '', exclusions: '', source: '', formula: '', values: { /* anything */ } } };
DECK.checks = [ () => '' ];                                                                           // optional; each returns '' or one issue sentence
```

- `kind`: `counted`, `estimate`, `illustrative`, `draft` (chip says "Draft setting", caution color), `concept` (no chip, no footnote; use for diagrams and definitions).
- The chip and the footnote are generated from these fields. Footnote left = `formula`; right = window, denominator, exclusions, source. Long provenance runs to three lines and collides with a chart that reaches below y 946, so keep the fields short.
- Binding: `{{dataset.path|fmt}}`. The first segment is the `DATA` key; the rest is a path inside `values`, with array indexes as numbers (`{{patterns.rows.3.seqs.0.lift|x1}}`). Works in text nodes, `aria-label`, and any string inside `DATA` itself. An unresolved placeholder is a `?check` issue.
- Formatters `F`: `int` (grouped), `compact` (1.2k, 3.4M), `pct0`, `pct1`, `dec1`, `dec2`, `x1` (2.4×), `delta` (+12, −3 with a true minus), `dur` (median days to "same day" or "N days before/after"), `absdays`, `absmonths`, `approx` (≈), `word`, `Word` (number to word, 0 to 12). No formatter prints the raw value. Add formatters to `F` in `60_helpers.js` when a deck needs one, and keep decimals consistent inside a chart.
- Shares are fractions (0 to 1). Units are always shown.
- `DECK.checks` are the deck's own arithmetic: tallies add up, parts sum to the whole. Write at least one. Also use them to cross-check a number that two datasets state (a count parsed from a page against the same count taken from the plotted dots) and to guard a claim that a slide's text hard-codes (the example checks that the unstable sequences belong to exactly the two patterns the gap row names).
- `F.Word` and `F.word` cover 0 to 12 only; a larger count throws while the page binds, so print it as digits (no formatter). A thrown formatter leaves no `window.__deckCheck`; read the console first.
- A dataset may take a table generated by a script from the source documents (`inject`), and may derive rows from another dataset after the `DATA` literal (`DATA.cover.values.rows = DATA.preds.values.guideline.families.map(...)`), so a count is stated once.
- A section may carry `data-d="key"` itself (statement slides with a big number) so the chip and footnote appear without a graphic.

## 3. Slide kinds and markup

All slides are `<section class="slide ..." data-sec="Part name">`, in presentation order; the number is the index plus one. Only `.active` shows. Every slide has `<aside class="notes">`.

- **Content** (default): head + one graphic + notes.
  ```html
  <section class="slide" data-sec="The problem">
    <div class="head"><div class="kicker">01 · The problem</div><h1>The claim, as a sentence.</h1><p class="lede">One line that supports it.</p></div>
    <svg class="full" viewBox="0 0 1920 1080" data-g="rankedBars" data-d="delay" data-o='{"top":1}' role="img" aria-label="Key numbers: {{delay.rows.0.v|pct0}}"></svg>
    <aside class="notes">What to say, with the caveat and the hand-off.</aside>
  </section>
  ```
  `data-g` builder, `data-d` dataset, `data-o` JSON options. Add `data-chip="none"` to suppress the chip and footnote.
  **Room band** (optional, for working sessions): `<p class="room"><b>For the room</b><span>One open question?</span></p>` inside the slide, after the graphic. The label is free text: "Goal" carries the deck's goal on the first content slide when there is no separate goal slide. For that use add `class="room big"` (32 px text, sits at y 897 to 1010) together with `data-foot="none"` on the section, which drops the footnote and the footer line (the chip stays; `data-chip="none"` drops chip and footnote). The graphic must still end above y 860. It sits at y 872 to 926, above the footnote, so the graphic must end above y 860 (use the builder's spacing option, for example `rankedBars` `pitch`, or fewer rows). One question per slide, phrased so the audience answers from their own judgment. Content slides only; a dark slide has no tinted variant.
- **`dark`**: content on `--bg-dark`; builders read the on-dark palette automatically through `pal(svg)`. Use once mid-deck.
- **`hero`** (cover) and **`hero close`** (closing): see `assets/starter/slides.html`. Parts: `.motif` svg with `data-motif`, `.eyebrow`, `h1.title` with one `<em>`, `.rule`, `.team`, `.people` with `data-people`, `svg.logo` using `#logo-word`. The motif keeps clear of the text boxes it finds.
- **`statement`**: one sentence (`.big`, optional `<em>`) or one number (`.num`, a value such as `57%` counts up) plus `.cap`; wrap in `<div class="st"><div class="kicker">..</div> .. </div>`. Two to three per deck for rhythm.
- **`divider`**: `.numeral` (giant letter or number, aria-hidden), `svg.marks` with `data-marks`, `.dt` holding `.kicker`, `h1`, `p.line`. See the example slide 17.
- Not implemented though the spec names them: `agenda`, `image`. Add CSS to BASE (an ENGINE edit, see section 8) if a deck needs them.

Footer, chip and footnote are added by `decorate()` in BOOT on content slides; hero and divider slides get none.

## 4. Builder catalogue

`G.<name>(svg, dataset, options)`. Engine library (`assets/engine/70_builders.js`), with data shape and limits as in `G.meta`:

| Builder | Use when | `values` shape | Options (`data-o`) | Limits |
|---|---|---|---|---|
| `rankedBars` | compare a few categories; one or two lead | `rows[{k, l?, v, hi?}]` | `head`, `note[]`, `top` (rows in accent, default 1, `0` for none), `together`, `scale`, `ref`, `refLabel`, `fmt` (default `pct1`), `pitch` (row spacing in px; 60 keeps 7 rows above y 860 for a room band) | 2 to 8 rows |
| `lanes` | two cases share a start and diverge | `lanes[{who,end,icon}]`, `steps[2]`, `stepIcons[2]`, `same`, `later`, `bag` | none | 2 lanes, 2 shared steps |
| `pipeline` | a method as a short ordered chain; under it either rules or a picture per step | `phases[{t,a,b,hot?}]`, `stations[{t,d,i,hot?,art?}]`, then optional `band[{at,t}]` + `bandTitle` (rules tied to stations) or `art` on each station (key of `G.art`) | none | 4 to 6 stations (titles about 15 characters, descriptions about 80), 3 rules; picture cards 245 x 226 at 6 stations |
| `cards` | 3 or 4 parallel ideas (definitions, limits) | `cards[{t, pos?, d, k, i}]` | none | 4 cards 390 x 620, body 6 lines |
| `treemap` | parts of a whole, how big each is | `rows[{id, name, n, pct}]` | `highlight` (row index) | 4 to 10 tiles |
| `layers` | a rule built from parts and yes-or-no questions | `top`, `join?`, `legend?`, `parts[{t,d,chips[]}]` | none | 3 parts, 4 chips each |
| `quadrant` | a judgment grid the audience fills in | `x[2]`, `y[2]`, `cells[4]`, `hint`, `good?` | `chips` (dataset key whose `rows[]` have `{id,name}`) | 4 cells, 8 chips |
| `askList` | the closing ask | `rows[{q, t}]` | none | 3 to 6 rows |

Icons for `i` / `icon` fields: arrow-right, check, check-circle, x, plus, minus, user, users, file, folder, link, lock, shield, clock, calendar, search, filter, settings, bolt, spark, chart-bar, chart-line, layers, box, globe, message, flag, target, refresh, alert, info, download, code, branch, merge, star, eye, heart, pulse, flask.

Station pictures for `pipeline` are drawn by `G.art.<name>(g, x, y, w, h, P, svg)`, registered in the deck's `builders.js`; use the same primitives and palette `P` as a builder, no text under 20 px, and keep to the card box. The example has six (`guideline` paper, `cohort` of people, `bag` of coded events, `clusters`, `sequence`, `pubmed` logo). A third-party logo goes in as an image: `scripts/photo_to_datauri.py logo.svg <key> inject/photo.json`, drawn with `<image href=PHOTO[key]>` on a plate that stays light in every theme (`lum(C.bg) > .5 ? C.surface : C.ink`). Fetch a logo only from the owner's own site, and use it to name the source, never to imply endorsement; the leak scan does not read a base64 image.

Deck builders in `assets/example-chest-pain/builders.js` show how topic-specific compositions look: `seqStrip` (ordered chains with in-group versus rest bars), `timeline` (dot plot on a compressed axis against an anchor; `o.pitch` spacing, `o.window` shades a window around the anchor), `verdictGrid` (status per cell), `bundleCard` (one-page profile of a group), `chipField` (an inventory of about 40 names in four labelled panels, chip weight showing reuse; fits above a room band), `gapTable` (numbered findings with evidence and one question each, 5 to 8 rows). `chipField` and `gapTable` are generic and can move to the engine once a second deck needs them (workflow step 9).

Compositions the spec describes but the library does not have yet (`statTiles`, `columns`, `bullet`, `dumbbell`, `lines`, `areaStack`, `sparklines`, `gantt`, `donut`, `stacked100`, `waterfall`, `funnel`, `sankey`, `isotype`, `scatter`, `heatmap`, `distribution`, `venn`, `loop`, `zones`, `network`, `compare`, and others): build them in the deck's `builders.js` following section 7, using the recipes in `spec.md` section 7.4. Do not build ones the outline does not need.

## 5. Helpers and tokens

Inside a builder:

- `const P = pal(svg)`: palette with the camelCase token names (`P.ink`, `P.ink2`, `P.accent`, `P.accentTint`, `P.accentInk`, `P.accentContrast`, `P.positive`, `P.surface2`, `P.s1`..`P.s8`, ...). On a `.dark` slide it returns the on-dark values under the same names, so one builder serves both. Never write a color literal.
- Primitives (parent first, each returns its element): `R(p,x,y,w,h,{rx,fill,stroke,sw,dash})`, `Ln`, `Ci`, `Pa`, `Gr` (group), `el(tag, attrs, parent)`, `T(p,x,y,text,{size,w,fill,a,ls,op,font,caps})` (y is the baseline; `font` is `'body'|'display'|'mono'`), `TL(p,x,y,lines,opts)`, `ico`/`icoC` (icons), `AV(p,key,name,cx,cy,r,ring)` (avatar), `arrowMarker(svg,id,color)`.
- Text: `measure(text,size,weight,font,ls)`, `wrap(text,maxW,opts)` returns lines, `fit(text,maxW,{max,min,lines,w})` returns `{size, lines}`. SVG text does not wrap; always wrap by measured width. Never go below 20 px.
- Scales and format: `lin(d0,d1,r0,r1)`, `symlog`, `F.*`, `resolve(str)` for strings that may hold placeholders.
- Layout: `ZONE = { x0:135, x1:1785, y0:316, y1:946 }`, `S.*` sizes, `W.*` weights, `SH.*` shape values (`SH.radiusCard`, `SH.radiusInner`), `A(el, 'x'|'fade')` marks an element for entry motion, `label(...)`, `caps(...)`.
- Tokens are fixed names (spec.md section 3.1). Beyond the spec the engine adds `--fs-eyebrow --fs-name --fs-statement --fs-num --fs-cap --fs-title2`, used by the cover, statement and divider kinds. Only the THEME section and the BRAND SLOT may hold literals.

## 6. Flags, keys, `?check`

- URL flags: `?check`, `?static` (no motion), `?theme=brand|light|dark|paper`, `?notes`; `#7` opens slide 7. Motion is off under `prefers-reduced-motion`, `?static`, `?check` and print.
- Keys: arrows, space, PageUp/Down, Home/End, `S` notes, `F` fullscreen, `O` overview, `T` theme, `?` help, `Esc`. Click the outer 20% of the window; swipe on touch.
- Print: `@page 1920px 1080px`, one slide per page, graphics in their final state; page count equals slide count.
- `?check` shows `pre#deck-check` (green border when clean) and sets `window.__deckCheck = { issues, notes }`. It reports: unresolved `{{ }}`, script errors, BRAND LEAK (color or font-family literals outside THEME, in CSS after BASE, in script, in static `style/fill/stroke` attributes), text off the stage, text overlapping text, SVG text under 20 px, missing notes, content slide without a graphic, not exactly one `h1`, the deck's `DECK.checks`, and a contrast table of token pairs for every theme with the nearest passing value. Notes (not issues): text outside the side margins, a lede on two lines.
- Read it from the Browser tools: navigate to `…/deck.html?check&static&theme=X&r=N`, wait about 1.5 s, evaluate `JSON.stringify(window.__deckCheck)`.

## 7. Add a builder

```js
G.meta.myChart = { use: 'when to choose it', data: 'values{...}', limits: '3 to 8 rows', notes: 'options: o.x' };
G.myChart = function (svg, ds, o) {
  svg.textContent = '';                       // idempotent: rebuilt on theme change and after fonts load
  const P = pal(svg), rows = ds.values.rows;
  // geometry inside ZONE; every text through T/TL with wrap or fit; marks with A(el,'x'|'fade') if they should animate
};
```

Rules: pure and idempotent; colors from `P` only; ids for markers and clip paths prefixed with the builder name (all slides share one page); direct labels over legends; a zero baseline for bars; one annotation that states the insight; accent for the focus and greys for the context; the chart grammar in `spec.md` section 7.2. Put deck-specific builders in the deck's `builders.js`. Promote a generic one to `engine/70_builders.js` only after the deck ships, with every topic string moved into dataset fields.

## 8. Regression test for engine changes

After any edit under `assets/engine/`, rebuild both `assets/example-chest-pain` (use a copy of the folder whose `deck.json` `out` points somewhere servable) and `assets/starter`, then for each theme compare the render of a build made before the change with one made after. Serve both files from the same preview server and evaluate in each:

```js
await document.fonts.ready; await new Promise(r => setTimeout(r, 600));
const h = s => { let x = 5381; for (let i = 0; i < s.length; i++) x = ((x << 5) + x + s.charCodeAt(i)) | 0; return x; };
h(document.querySelector('#stage').innerHTML)
```

Load with `?static&theme=brand` (then dark, paper). Equal hashes mean equal output. Also confirm `?check` returns zero issues in every theme, and the console is clean. Remove the temporary copies afterwards.

## 9. Gotchas that cost time before

- Concatenating parts: a stray `</script>` inside a part stops the engine from loading (`G is not defined`). Only BOOT closes the script.
- `aspect-ratio` on a grid item whose only child is absolutely positioned collapses the row (overview thumbnails overlapped). The overview uses a `padding-top: 56.25%` spacer instead.
- The browser caches the file hard: add `&r=N` to the preview URL after each rebuild.
- The notes panel text lives in `<aside class="notes">`; BASE hides it inside slides (`.slide .notes{display:none}`).
- A graphic must end above y 946 or the footnote (up to three lines) overlaps it. Shorten the dataset's provenance fields first.
- `?check` skips `aria-hidden` text and parent-child text overlap on purpose (the giant divider numeral would otherwise report).
- JavaScript that needs black or white for contrast math must not write `rgb(0, 0, 0)`; the leak scan reads script text. `nearestPass` uses arrays for that reason. The scan's own regexes are built from fragments so the file does not match itself.
- Light-theme greys must keep 4.5:1 against `--surface-2`; the table shows the pair `ink3/surface2`.
- Treemap `highlight` is the index in the dataset's row order, not the sorted order.
- Headless Chrome (print, screenshot) fails inside this sandbox; the Browser pane works for everything but real PDF export.
- `python3` on this machine has no pandas; use `/opt/miniconda3/envs/ethos_llm/bin/python -I` for data scripts, and `python3 -I` for the assembler.
