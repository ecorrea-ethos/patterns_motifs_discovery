---
name: html-deck
description: Build a presentation deck as ONE self-contained, offline HTML file with hand-built SVG data visualizations, claim-style slide titles, spoken speaker notes, themes (light, dark, paper, plus a brand slot filled with the Ethos preset), print-to-PDF and a ?check self-test. Use whenever the user asks for a slide deck, presentation, slides, a talk, a validation or review session deck, a "deck for Dr. Z / physicians / underwriters / leadership", or wants a notebook, report, docx, xlsx or analysis turned into slides, even if they never say HTML. Also use to add, edit or re-brand slides of an existing deck built with this skill (edit its source folder, then re-assemble), and to extend the builder library. Do not use for .pptx output (use the pptx skill) unless the user wants the HTML deck.
---

# html-deck

One `.html` file you open by double-click and present from. No network, no libraries, graphics drawn as inline SVG. The slides, the numbers and the brand live in separate places, so a deck can be rebuilt, re-themed or re-branded without touching the engine.

Why this shape: a deck that physicians and underwriters must *use* needs graphics that carry the argument, numbers that cannot drift between a slide, its notes and its footnote, and a way to prove nothing overflowed. The engine gives all three, so the work goes into the story and the data.

## What ships in this skill

| Path | What it is |
|---|---|
| `assets/engine/` | The ENGINE, topic-free: head, theme tokens, base CSS, sprites (icons, logo), chrome, helpers, builder library, boot, `?check`. Never edit it for one deck. |
| `assets/brands/ethos/` | Ethos preset: `brand.css` (the BRAND SLOT block) and `logo.svgfrag`. `neutral/` is the placeholder logo. |
| `assets/starter/` | Smallest working deck (5 slides, fictional, all numbers illustrative). Copy it to begin. |
| `assets/example-chest-pain/` | Worked example: 29 slides for physicians and underwriters (a working session with open questions), with its own `builders.js`, injected tables and the scripts that built them. Read it to see the patterns. |
| `scripts/assemble.py` | Concatenates engine + a deck folder into the one HTML file. |
| `references/engine.md` | Contracts: file layout, DATA schema, `{{ }}` binding, builder catalogue and data shapes, slide kinds, flags, how to add a builder, gotchas. Read before writing slides. |
| `references/spec.md` | The full design specification (the original prompt, v1): theme rules, chart grammar, narrative rules, geometry, acceptance checklist. Read before the art-director pass. |
| `references/brands.md` | How to plug in a brand, and what the Ethos preset derived. |

## Workflow

1. **Triage.** Wants `.pptx`: use the pptx skill. A deck folder already exists (a `deck.json` beside `slides.html`): edit its files and go to step 6. Never hand-edit the generated HTML; the next assemble would erase the edit.
2. **Intake.** Ask only for what the request and the source material leave open, in one round (AskUserQuestion, at most four questions). Do not ask for what has a default.
   - Topic and thesis: what should the room believe or do afterwards?
   - Audience (role, expertise, what they care about), presenters (name, role; people are named on the cover), setting and length (for example 20-minute talk plus 20 of questions).
   - Source: notebook, report, docx, xlsx. Read it yourself; take numbers only from it.
   - Purpose guard: for clinical decks, ask whether the deck is decision-free. Decision-free means no triage, routing, accept or decline, or underwriting recommendation, so the audience judges the findings without being steered.
   - Brand: Ethos preset (default in this project) or neutral.
   - Defaults when unsaid: English, plain and confident tone, no hype, 16 to 26 slides, about one content slide per 1.5 to 2 minutes, light theme with the brand slot filled when a brand is chosen.
3. **Evidence table.** List every number with: what was counted, definition, window, denominator, exclusions, source, and a kind: COUNTED, ESTIMATE (with its formula), ILLUSTRATIVE (fictional). When two sources disagree (for example a cohort of 150,368 in one extract and 139,416 in another run), pick one per number, say which, and tell the user. Do not add a counted number to an estimate; do not show a rate without its denominator.
4. **Assumptions and outline, then wait for approval.** At most 10 assumptions. Outline table: `# | kind | claim (title) | composition | dataset | tag`. Titles are claims ("Most reviews finish in an hour; a few take a week."), not topics. One claim per slide. Choose compositions by the claim; `references/engine.md` lists what exists and what each needs. Ask about any composition the library lacks only if it changes the story; otherwise plan to build it (step 5).
5. **Scaffold and write.** Source lives in the project, not in a scratch folder, so the deck can be rebuilt: `slides/<name>/` holding `deck.json`, `slides.html`, `data.js`, optional `builders.js`. Copy `assets/starter/` and edit.
   - `deck.json`: `title`, `out` (`../<name>.html`), `brand` (`"ethos"` or `null`), `wordmark`, `inject` (see engine.md).
   - Write `data.js` first, every number once, then `slides.html` citing numbers as `{{dataset.path|fmt}}` in text, notes and aria-labels, then `builders.js` for any composition the library lacks.
   - Presenter photo (when the user supplies one): `python3 -I .claude/skills/html-deck/scripts/photo_to_datauri.py <photo> <key> slides/<name>/inject/photo.json` (key = `DECK.people[].key`; `--cx --cy --side` aim the square crop at the face, so look at the photo first). It embeds a 256 px copy, so the deck stays one file. Then `const PHOTO = /*INJECT:photo*/{};` in `data.js` and `"photo": "inject/photo.json"` under `inject` in `deck.json`.
   - A new builder that is not tied to this deck's topic belongs in the engine library after the deck ships (step 9).
6. **Assemble and verify.**
   ```bash
   python3 -I .claude/skills/html-deck/scripts/assemble.py slides/<name>
   ```
   Serve `slides/` (the `deck-preview` entry of `.claude/launch.json`, port 8766) and drive it with the Browser tools; files outside the project cannot be driven. Add `&r=N` to the URL to defeat the cache after each rebuild.
   - `?check&static&theme=brand|light|dark|paper`: read `window.__deckCheck.issues` after about 1.5 s. Required: zero issues in every theme. The panel `pre#deck-check` lists each issue with its slide.
   - Look at every slide at full size (`?static#N`), plus overview (`O`), notes (`S`) and one dark and one paper slide. Fix what you see, not only what the check reports.
   - Console clean, `performance.getEntriesByType('resource').length` is 0 (no network).
   - Headless Chrome print and screenshots fail inside this sandbox, so a real PDF cannot be produced here. Say so; never claim a check you did not run.
7. **Art-director pass.** Name the five weakest slides (sparse cards, empty space, a chart whose point is not obvious in three seconds, two slides with the same composition in a row) and improve them. Blur test: the claim and the focal point must survive.
8. **Report** (spec section 13): 300 words or fewer: file name, how to open, keys, PDF steps (Chrome or Edge, Print, Save as PDF, Background graphics on, Margins none), the three brand steps, what is counted, estimate, illustrative or draft, what was verified and what could not be, known limitations, assumptions and deltas from the brief. Then "Skill extraction notes" (120 words or fewer) only when the user is growing the library.
9. **Grow the library (optional).** When a builder you wrote is generic, move it from the deck's `builders.js` into `assets/engine/70_builders.js` with a `G.meta` entry, parametrize any topic string, then rebuild `assets/example-chest-pain` and `assets/starter` and confirm zero issues and an unchanged render (regression in engine.md). Update the catalogue table in `references/engine.md`.

## Writing rules that the checks cannot see

- **Abbreviations: full term first, abbreviation in brackets after it** ("complete blood count (CBC)", never "CBC (complete blood count)"), in slides, notes and aria-labels. After building, scan for stragglers: `grep -noE "\b[A-Z]{2,}[0-9-]*\b" slides/<name>/slides.html slides/<name>/data.js | sort -t: -k3 -u`. Code identifiers that are the subject (ICD-10 codes such as R07.89) are fine.
- Titles are claims of at most about 70 characters, two lines at most; the lede is exactly one line (about 105 characters). Say "we", not "you", in notes.
- For a working session (the audience is asked to decide what is missing, not to hear results), end content slides with a room band (`<p class="room">`, engine.md section 3): one open question each, never leading. Gather the gaps on one slide with evidence and a question per row, and rank nothing, so the room does.
- Notes are spoken, first person plural, 40 to 150 words on content slides, one sentence on dividers. Each carries the caveat and the hand-off to the next slide; the cover note lists the keys.
- Define each new term in a card the first time it appears. Say what a number is not ("elapsed time, not effort", "care delivered, not diagnosis").
- Estimates start with `≈`, use the caution color, show their formula in the footnote, and the notes say "estimate" aloud. Illustrative data keeps its label on the slide.
- Never invent numbers, quotes, people or logos. People are initials avatars until the user supplies a photo (see step 5); never use stock or found photos.
- Color means a role (accent = focus, positive = counted or done, caution = old way or any estimate, negative = loss, info and greys = context), never an entity.
- No color, font or size literal outside the theme block; the check reports a BRAND LEAK otherwise. If a brand rule cannot be expressed as a token, tell the user; do not work around it inside a builder.

## Hard rules

- One file, offline: no frameworks, CDN, chart or icon libraries, web fonts, external images, analytics.
- The engine is shared. A change under `assets/engine/` must leave the example and the starter at zero issues in every theme, and the example's render byte-identical (hash of `#stage` innerHTML before and after) unless the change is meant to alter output; say which it is.
- Licensed brand fonts are not bundled. The brand stacks fall back to Georgia and Helvetica; tell the user what was actually rendered.
- Size budget: about 2,200 lines or 150 KB. The assembler warns; prune unused builders and datasets if it does.
