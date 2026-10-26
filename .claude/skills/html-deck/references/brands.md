# Brands

A brand is a folder in `assets/brands/<name>/` with two files. Naming it in `deck.json` (`"brand": "<name>"`) fills the BRAND SLOT and makes the brand theme the default. Nothing else changes: no builder, helper, slide or BASE rule may hold a brand value.

| File | Content |
|---|---|
| `brand.css` | The whole block from `/* >>> BRAND SLOT START */` to `/* <<< BRAND SLOT END */`: an optional `@font-face` comment and one rule `html[data-theme="brand"] { ... }` with the tokens |
| `logo.svgfrag` | Two `<symbol>` elements, `logo-word` (the wordmark, used on cover and closing at 250 x 48, viewBox about 720 x 139) and `logo-mark`. Vector paths, no fill or stroke attributes (the assembler adds `fill="currentColor"`), so the logo follows the text color |

The neutral folder holds a placeholder logo with a `__WORDMARK__` text that the assembler fills from `deck.json`.

## Plug in a new brand (three steps)

1. **Tokens.** Copy `assets/brands/ethos/brand.css`, keep the markers, and map the guide with this table. Derive what the guide lacks and list it for the user.

   | Brand concept | Token |
   |---|---|
   | Primary brand color | `--accent`, `--accent-contrast` (text on a solid accent), `--accent-tint`, `--accent-ink`, `--accent-on-dark` |
   | Other brand colors | `--s2`..`--s8`, `--info` |
   | Success, warning, error | `--positive`, `--caution`, `--negative` (each with `-tint`, `-ink`, `-on-dark`); derive when the brand has none |
   | Neutrals | `--ink`, `--ink-2`, `--ink-3`, `--line`, `--line-strong`, `--bg-alt`, `--surface-2` |
   | Dark brand background | `--bg-dark`, `--ink-on-dark`, `--ink-2-on-dark`, `--ink-3-on-dark`, `--line-on-dark` |
   | Headline and body typeface | `--font-display`, `--font-body`, `--font-mono`, `--w-display` (the weight the brand's display face looks right at) |
   | Corner style, line weight | `--radius-card`, `--radius-inner`, `--stroke` |
   | Pattern motif | `--motif-a`, `--motif-b`, `--motif-alpha` |

2. **Logo.** Convert the guide's logo page to SVG with any PDF-to-SVG tool, copy the logo paths into `<symbol id="logo-word" viewBox="...">` and `<symbol id="logo-mark" viewBox="...">`, and remove fill and stroke attributes.
3. **Fonts.** Licensed fonts are not bundled. Put the font stack in `--font-display` and `--font-body` with fallbacks, and add `@font-face` rules (local() first, then a relative file) only when the user supplies the files. State in the report which face actually rendered.

Then assemble and run `?check` in every theme. The contrast table lists each token pair per theme with the nearest passing value; fix failures in `brand.css`. If a brand rule cannot be written as a token, tell the user; do not edit a builder.

## Ethos preset (Ethos Brand Guidelines 2026, `slides/Ethos-Brand-Guidelines-2026.pdf`)

Taken from the guide: accent = Dark Cypress `#05594F`; dark background = Dark Cypress; accent on dark = Bright Clover `#59F8B1`; ink = Night `#272727`; info = Neptune `#0B4368`; page tint = Light Truffle `#FAF9F5`; surface-2 = Truffle `#EFECE2`; accent tint = Light Cypress `#E3F8F6`; display face Portada (weight 600), body face Hauss; logo word and mark as vector paths.

Derived by us because the guide has no equivalent: `--positive #17835F`, `--caution #9A5B00`, `--negative #B3321F` with their tints, inks and on-dark values; `--ink-3 #6B6B6B` and the on-dark greys; the categorical series `--s2`..`--s8`; lines and the dark-theme hairlines.

Fonts: Portada and Hauss are licensed and not bundled, so decks show Merriweather, Iowan Old Style or Georgia for display and Helvetica Neue or Arial for body unless the fonts are installed on the presenting machine.

Roles in the deck follow the color meaning in `spec.md` 3.2: accent for the focus, positive for counted or done, caution for the old way and every estimate, negative for loss, info and the greys for context.
