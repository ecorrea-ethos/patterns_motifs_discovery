#!/usr/bin/env python3
"""Crop a photo to a square, shrink it, and store it as a data URI in a JSON file the deck can inject.

    python3 -I scripts/photo_to_datauri.py <photo.jpg> <key> <deck-dir>/inject/photo.json [--cx 0.5] [--cy 0.4] [--side 1.0] [--size 256]

<key> is the DECK.people[].key the avatar belongs to. The JSON is {key: "data:image/jpeg;base64,..."}; an existing file is updated, so several presenters can share one.
In the deck folder: data.js says `const PHOTO = /*INJECT:photo*/{};` and deck.json says `"inject": {"photo": "inject/photo.json"}`.

The photo is embedded (not linked) so the deck stays one file that works from an email or a USB stick. The avatar is drawn at about 100 px, so 256 px is plenty
(about 15 KB). --cx and --cy place the crop centre as a fraction of the image width and height; --side is the square's edge as a fraction of the shorter
side (1.0 uses the whole width of a portrait photo, smaller values zoom in on the face). Needs Pillow.
"""
import argparse, base64, io, json, pathlib, sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit('photo_to_datauri: Pillow is missing; use /opt/miniconda3/envs/ethos_llm/bin/python -I')

ap = argparse.ArgumentParser()
ap.add_argument('photo'), ap.add_argument('key'), ap.add_argument('out')
ap.add_argument('--cx', type=float, default=0.5), ap.add_argument('--cy', type=float, default=0.4)
ap.add_argument('--side', type=float, default=1.0), ap.add_argument('--size', type=int, default=256)
a = ap.parse_args()

im = ImageOps.exif_transpose(Image.open(a.photo)).convert('RGB')
w, h = im.size
side = min(w, h) * a.side
left = min(max(a.cx * w - side / 2, 0), w - side)
top = min(max(a.cy * h - side / 2, 0), h - side)
im = im.crop((round(left), round(top), round(left + side), round(top + side))).resize((a.size, a.size), Image.LANCZOS)
buf = io.BytesIO()
im.save(buf, 'JPEG', quality=82, optimize=True)
uri = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')

out = pathlib.Path(a.out)
data = json.loads(out.read_text()) if out.exists() else {}
data[a.key] = uri
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(data, indent=1) + '\n')
print(str(out) + ': ' + a.key + ' -> ' + str(len(uri) // 1024) + ' KB data URI (' + str(a.size) + ' px square)')
