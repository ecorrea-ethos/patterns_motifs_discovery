#!/usr/bin/env python3
"""Assemble one self-contained deck HTML from the engine (assets/engine) and a deck folder.

    python3 -I scripts/assemble.py <deck-dir>

<deck-dir> holds:
    deck.json     {"title": "...", "out": "../my-deck.html", "brand": "ethos" | null, "wordmark": "Name", "inject": {"rows": "inject/rows.json"}}
    slides.html   section 4: the <section class="slide"> elements, in presentation order
    data.js       section 5: DECK, PHOTO, DATA (and optional DECK.checks); no <script> tag
    builders.js   optional section 7b: builders that only this deck needs

Order of the output file: head, theme (brand slot filled when a brand is named), base, sprites (logo symbols), slides, chrome,
data, helpers, builders, deck builders, boot. `/*INJECT:name*/[]` markers in data.js are replaced by the JSON file named in "inject".
"""
import html, json, pathlib, re, sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
ENGINE, BRANDS = SKILL / 'assets' / 'engine', SKILL / 'assets' / 'brands'
SLOT = re.compile(r'/\* >>> BRAND SLOT START \*/.*?/\* <<< BRAND SLOT END \*/', re.S)
MAX_LINES, MAX_KB = 2200, 150


def read(p):
    s = pathlib.Path(p).read_text(encoding='utf-8')
    return s if s.endswith('\n') else s + '\n'


def fail(msg):
    sys.exit('assemble: ' + msg)


def logo_symbols(brand, wordmark):
    if brand:
        frag = (BRANDS / brand / 'logo.svgfrag').read_text(encoding='utf-8').strip()
    else:
        frag = read(BRANDS / 'neutral' / 'logo.svgfrag').strip().replace('__WORDMARK__', html.escape(wordmark))
    return frag.replace('<symbol ', '<symbol fill="currentColor" stroke="none" ')


def main(deck_dir):
    d = pathlib.Path(deck_dir).resolve()
    if not (d / 'deck.json').exists():
        fail('no deck.json in ' + str(d))
    cfg = json.loads((d / 'deck.json').read_text(encoding='utf-8'))
    for k in ('title', 'out'):
        if not cfg.get(k):
            fail('deck.json needs "' + k + '"')
    brand = cfg.get('brand')
    if brand and not (BRANDS / brand / 'brand.css').exists():
        fail('unknown brand "' + str(brand) + '"; folders in assets/brands: ' + ', '.join(sorted(p.name for p in BRANDS.iterdir())))

    head = read(ENGINE / '00_head.html').replace('__TITLE__', html.escape(cfg['title']))
    if brand:
        head = head.replace('data-theme="light"', 'data-theme="brand"', 1)
    theme = read(ENGINE / '10_theme.css')
    if brand:
        theme = SLOT.sub(lambda m: (BRANDS / brand / 'brand.css').read_text(encoding='utf-8').strip(), theme, count=1)
    sprites = read(ENGINE / '30_sprites.html').replace('<!--LOGO-->', logo_symbols(brand, cfg.get('wordmark', 'Your logo')))
    data = read(d / 'data.js')
    for name, rel in cfg.get('inject', {}).items():
        marker = re.compile(r'/\*INJECT:' + re.escape(name) + r'\*/(\[\]|\{\})')
        if not marker.search(data):
            fail('data.js has no /*INJECT:' + name + '*/[] or /*INJECT:' + name + '*/{} marker')
        payload = json.dumps(json.loads((d / rel).read_text(encoding='utf-8')), ensure_ascii=False, separators=(',', ':'))
        data = marker.sub(lambda m: payload, data, count=1)
    own = read(d / 'builders.js') if (d / 'builders.js').exists() else ''

    out = ''.join([head, theme, read(ENGINE / '20_base.css'), sprites, read(d / 'slides.html'), read(ENGINE / '35_chrome.html'),
                   data, read(ENGINE / '60_helpers.js'), read(ENGINE / '70_builders.js'), own, read(ENGINE / '80_boot.js')])
    for left in ('__TITLE__', '<!--LOGO-->', '/*INJECT:'):
        if left in out:
            fail('unreplaced placeholder ' + left)
    dst = (d / cfg['out']).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding='utf-8')
    lines, kb = len(out.splitlines()), len(out.encode('utf-8')) // 1024
    print(str(dst) + ': ' + str(lines) + ' lines, ' + str(kb) + ' KB')
    if lines > MAX_LINES or kb > MAX_KB:
        print('warning: over the size budget (' + str(MAX_LINES) + ' lines / ' + str(MAX_KB) + ' KB); remove unused builders or datasets')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        fail('usage: python3 -I scripts/assemble.py <deck-dir>')
    main(sys.argv[1])
