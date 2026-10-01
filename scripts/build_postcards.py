#!/usr/bin/env python3
"""Deterministic postcard layout. Run with Pillow and NumPy; --only builds samples."""
from pathlib import Path
import argparse
import json
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "images/photography"
ORIGINALS = SOURCE / "originals"
DEST = SOURCE / "postcards"
WIDTH, HEIGHT = 1086, 1448
PHOTO_BOTTOM, PHOTO_CONTENT_BOTTOM = 795, 781
TITLE_BASELINE, FOOTER_BASELINE = 890, 1392
ILLUSTRATION_CENTER = (543, 1125)
ILLUSTRATION_LIMIT = (440, 290)
TITLE_SIZE, FOOTER_SIZE, FOOTER_TRACKING = 52, 22, 1.6
HANDWRITING = "/System/Library/Fonts/Supplemental/Apple Chancery.ttf"
TYPEWRITER = "/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc"

# Phrases, place/date metadata and provenance of the extracted screenprints.
ASSETS = [
    ("Baoji_202407_1", "Across the quiet sky", "BAOJI", "2024.07", 930, 1275),
    ("Barcelona_202608_1", "A city reaching skyward", "BARCELONA", "2026.08", 1000, 1335),
    ("Barcelona_202608_2", "Beyond the leaves", "BARCELONA", "2026.08", 1000, 1335),
    ("Barcelona_202608_3", "Where light finds its way", "BARCELONA", "2026.08", 960, 1335),
    ("Beijing_202601_1", "Winter holds its breath", "BEIJING", "2026.01", 940, 1290),
    ("Fukushima_202307", "Running into summer", "FUKUSHIMA", "2023.07", 960, 1310),
    ("Guiyang_202607_1", "A pause in the green", "GUIYANG", "2026.07", 960, 1300),
    ("Hangzhou_202507_1", "A moment of stillness", "HANGZHOU", "2025.07", 970, 1340),
    ("Jeju_202607_1", "Two quiet companions", "JEJU", "2026.07", 990, 1290),
    ("Jeju_202607_2", "Where the shore slows", "JEJU", "2026.07", 980, 1300),
    ("Kamakura_202307_1", "A moment to keep", "KAMAKURA", "2023.07", 920, 1300),
    ("Kyoto_202307_1", "Under the vermilion eaves", "KYOTO", "2023.07", 990, 1340),
    ("Lisbon_202607_1", "A little closer to the sun", "LISBON", "2026.07", 995, 1340),
    ("Madrid_202607_1", "Beneath a quiet dome", "MADRID", "2026.07", 900, 1290),
    ("Sanya_202412_1", "The sea turns rose", "SANYA", "2024.12", 980, 1300),
    ("Seville_202607_1", "Light between the arches", "SEVILLE", "2026.07", 985, 1340),
    ("Tokyo_202307_1", "A small journey begins", "TOKYO", "2023.07", 1020, 1340),
    ("Xian_202407_1", "Evening writes in light", "XI'AN", "2024.07", 950, 1290),
]

def paper():
    rng = np.random.default_rng(381)
    grain = rng.normal(0, 0.9, (HEIGHT, WIDTH, 1))
    cloud = Image.fromarray(rng.integers(90, 165, (80, 60), dtype=np.uint8))
    cloud = np.asarray(cloud.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(16)), dtype=float)
    tone = (cloud - 127)[:, :, None] / 18
    rgb = np.clip(np.array([248, 241, 225])[None, None, :] + grain + tone, 0, 255).astype(np.uint8)
    return Image.fromarray(rgb, "RGB").convert("RGBA")

def illustration(stem, top, bottom):
    # Store the extracted screenprints independently of retired postcard exports.
    assets = ROOT / "scripts/postcard_illustrations"
    metadata = json.loads((assets / "manifest.json").read_text())[stem]
    with Image.open(assets / (stem + ".png")) as source:
        result = source.convert("RGBA")
    return result, metadata["source_crop"], metadata["ink_bbox"]


def place_photo(canvas, source_image, seed):
    photo = ImageOps.exif_transpose(source_image).convert("RGB")
    ratio = min(WIDTH / photo.width, PHOTO_CONTENT_BOTTOM / photo.height)
    w, h = round(photo.width * ratio), round(photo.height * ratio)
    scaled = photo.resize((w, h), Image.Resampling.LANCZOS)
    x, y = (WIDTH - w) // 2, PHOTO_CONTENT_BOTTOM - h
    canvas.alpha_composite(scaled.convert("RGBA"), (x, y))
    # Extend only the last row into the tear allowance, leaving the COMPLETE
    # original photograph visible above. No source pixels are cropped.
    allowance = 33
    edge = scaled.crop((0, h - 1, w, h)).resize((w, allowance))
    mask = Image.new("L", (w, allowance), 0)
    draw = ImageDraw.Draw(mask)
    rng = random.Random(seed)
    coarse = [rng.uniform(5, 23) for _ in range(w // 28 + 3)]
    boundary = []
    for px in range(w):
        t = px / 28
        idx, frac = int(t), t % 1
        v = coarse[idx] * (1 - frac) + coarse[idx + 1] * frac + rng.uniform(-1.7, 1.7)
        boundary.append(round(v))
    draw.polygon([(0, 0), (w - 1, 0)] + [(px, boundary[px]) for px in range(w - 1, -1, -1)], fill=255)
    edge.putalpha(mask)
    canvas.alpha_composite(edge, (x, PHOTO_CONTENT_BOTTOM))
    # Light frayed paper fibres on the torn strip, outside the actual photograph.
    fibres = Image.new("RGBA", canvas.size)
    fd = ImageDraw.Draw(fibres)
    for px in range(w):
        by = PHOTO_CONTENT_BOTTOM + boundary[px]
        fd.line((x + px, by - rng.randrange(1, 4), x + px, by + rng.randrange(2, 7)), fill=(250, 244, 230, rng.randrange(105, 230)), width=1)
    for _ in range(max(70, w // 4)):
        px = rng.randrange(w)
        by = PHOTO_CONTENT_BOTTOM + boundary[px]
        fd.line((x + px, by - 2, x + px + rng.uniform(-2, 2), by + rng.uniform(1, 5)), fill=(248, 239, 216, 125), width=1)
    canvas.alpha_composite(fibres)
    return [x, y, w, h], [photo.width, photo.height]

def cancellation(canvas, right_edge):
    rng = random.Random(99)
    scale = 3
    size = (230, 154)
    mask = Image.new("L", (size[0] * scale, size[1] * scale))
    d = ImageDraw.Draw(mask)
    for inset, width in [(5, 2), (10, 1)]:
        d.ellipse((inset * scale, 12 * scale, (122 - inset) * scale, (129 - inset) * scale), outline=155, width=width * scale)
    for row in range(4):
        pts = [(round(px * scale), round((45 + row * 17 + 5 * math.sin(px / 18)) * scale)) for px in range(98, 213)]
        d.line(pts, fill=140, width=2 * scale)
    arr = np.asarray(mask).copy()
    random_field = np.random.default_rng(51).random(arr.shape)
    arr[random_field < 0.20] = 0
    mask = Image.fromarray(arr).resize(size, Image.Resampling.LANCZOS)
    stamp = Image.new("RGBA", size, (38, 58, 70, 0))
    stamp.putalpha(mask)
    cx = min(WIDTH - 154, right_edge - 3)
    canvas.alpha_composite(stamp, (round(cx - 62), PHOTO_BOTTOM - 73))

def write_text(canvas, phrase, footer):
    # Render at 3x resolution for smooth pen strokes; every card uses the exact
    # same font sizes, horizontal centre and baselines.
    scale = 3
    layer = Image.new("RGBA", (WIDTH * scale, HEIGHT * scale))
    draw = ImageDraw.Draw(layer)
    hand = ImageFont.truetype(HANDWRITING, TITLE_SIZE * scale)
    typewriter = ImageFont.truetype(TYPEWRITER, FOOTER_SIZE * scale)
    if draw.textlength(phrase, font=hand) > 850 * scale:
        raise ValueError("Phrase too long for the fixed font size: " + phrase)
    draw.text((WIDTH * scale / 2, TITLE_BASELINE * scale), phrase, font=hand, anchor="ms", fill=(49, 67, 72, 238))
    lengths = [draw.textlength(ch, font=typewriter) for ch in footer]
    total = sum(lengths) + (len(footer) - 1) * FOOTER_TRACKING * scale
    x = (WIDTH * scale - total) / 2
    for ch, length in zip(footer, lengths):
        draw.text((x, FOOTER_BASELINE * scale), ch, font=typewriter, anchor="ls", fill=(52, 68, 72, 225))
        x += length + FOOTER_TRACKING * scale
    canvas.alpha_composite(layer.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS))

def build(only=None):
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for idx, (stem, phrase, place, date, top, bottom) in enumerate(ASSETS):
        if only and stem not in only:
            continue
        canvas = paper()
        with Image.open(ORIGINALS / (stem + ".jpg")) as source_image:
            rect, original_size = place_photo(canvas, source_image, 800 + idx)
        art, source_crop, ink_bbox = illustration(stem, top, bottom)
        art_x = ILLUSTRATION_CENTER[0] - art.width // 2
        art_y = ILLUSTRATION_CENTER[1] - art.height // 2
        canvas.alpha_composite(art, (art_x, art_y))
        cancellation(canvas, rect[0] + rect[2])
        footer = place + " · " + date
        write_text(canvas, phrase, footer)
        output = DEST / (stem + "_postcard.png")
        canvas.convert("RGB").save(output, optimize=True)
        records.append({"source": stem + ".jpg", "output": output.name, "phrase": phrase, "footer": footer,
                        "canvas": [WIDTH, HEIGHT], "original_size": original_size, "photo_rectangle": rect,
                        "illustration_rectangle": [art_x, art_y, art.width, art.height],
                        "illustration_source_crop": source_crop, "illustration_ink_bbox": ink_bbox,
                        "title_font": "Apple Chancery", "title_size": TITLE_SIZE, "title_baseline": TITLE_BASELINE,
                        "footer_font": "American Typewriter", "footer_size": FOOTER_SIZE,
                        "footer_baseline": FOOTER_BASELINE, "footer_center": WIDTH / 2})
        print(output.name, phrase)
    if not only:
        (DEST / "layout.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    return records

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="+")
    build(parser.parse_args().only)
