"""
generate_dataset.py
--------------------
Creates a small synthetic image dataset so the app/detector can be exercised end-to-end.
"""

import os
import random
from PIL import Image, ImageDraw, ImageFilter

CROPS = [
    "rice", "wheat", "maize", "tomato",
    "potato", "cotton", "sugarcane", "chili",
]
PARTS = ["leaf", "root"]
CLASSES = ["healthy", "diseased"]
IMAGES_PER_CLASS = 15
IMG_SIZE = 256

BASE_DIR = os.path.join(os.path.dirname(__file__), "dataset")

LEAF_GREENS = [(60, 130, 40), (75, 150, 55), (45, 110, 35)]
ROOT_TANS = [(210, 190, 150), (225, 205, 170), (195, 175, 140)]
LESION_COLORS = [(90, 55, 20), (60, 35, 15), (30, 20, 15)]


def _cos(rad):
    import math
    return math.cos(rad)


def _sin(rad):
    import math
    return math.sin(rad)


def _blob_mask(size, jitter=18):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    cx, cy = size // 2, size // 2
    points = []
    for angle in range(0, 360, 12):
        rad = (angle / 180) * 3.14159
        r = size * 0.36 + random.uniform(-jitter, jitter)
        x = cx + r * (1.15 if -0.3 < (angle % 360) / 180 - 1 < 0.3 else 1.0) * _cos(rad)
        y = cy + r * _sin(rad)
        points.append((x, y))
    draw.polygon(points, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    return mask


def _base_canvas(base_color, size=IMG_SIZE):
    img = Image.new("RGB", (size, size), (250, 248, 244))
    mask = _blob_mask(size)

    fill = Image.new("RGB", (size, size), base_color)
    draw = ImageDraw.Draw(fill)
    for _ in range(40):
        x, y = random.randint(0, size), random.randint(0, size)
        r = random.randint(4, 14)
        shade = tuple(max(0, min(255, c + random.randint(-15, 15))) for c in base_color)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=shade)

    img.paste(fill, (0, 0), mask)
    return img, mask


def _add_veins(img, mask, size=IMG_SIZE):
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    vein_color = (35, 80, 25)
    draw.line([(cx, 20), (cx, size - 20)], fill=vein_color, width=2)
    for i in range(-3, 4):
        if i == 0:
            continue
        y = cy + i * 22
        draw.line([(cx, y), (cx + i * 40, y - 15)], fill=vein_color, width=1)
        draw.line([(cx, y), (cx - i * 40, y - 15)], fill=vein_color, width=1)
    return img


def _add_lesions(img, mask, size=IMG_SIZE, severity="random"):
    draw = ImageDraw.Draw(img)
    n_spots = random.randint(6, 22) if severity == "random" else severity
    for _ in range(n_spots):
        x, y = random.randint(20, size - 20), random.randint(20, size - 20)
        if mask.getpixel((x, y)) < 100:
            continue
        r = random.randint(4, 16)
        color = random.choice(LESION_COLORS)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        halo = tuple(min(255, c + 40) for c in color)
        draw.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], outline=halo, width=1)
    return img


def make_image(crop, part, cls):
    if part == "leaf":
        base_color = random.choice(LEAF_GREENS)
        img, mask = _base_canvas(base_color)
        img = _add_veins(img, mask)
        if cls == "diseased":
            img = _add_lesions(img, mask)
    else:
        base_color = random.choice(ROOT_TANS)
        img, mask = _base_canvas(base_color)
        if cls == "diseased":
            img = _add_lesions(img, mask, severity=random.randint(8, 20))

    img = img.filter(ImageFilter.SMOOTH_MORE)
    return img


def generate():
    total = 0
    for crop in CROPS:
        for part in PARTS:
            for cls in CLASSES:
                out_dir = os.path.join(BASE_DIR, crop, part, cls)
                os.makedirs(out_dir, exist_ok=True)
                for i in range(IMAGES_PER_CLASS):
                    img = make_image(crop, part, cls)
                    img.save(os.path.join(out_dir, f"img_{i:03d}.png"))
                    total += 1
    print(f"Generated {total} mock images under {BASE_DIR}")


if __name__ == "__main__":
    random.seed(42)
    generate()
