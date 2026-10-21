import re, os, sys
from PIL import Image, ImageOps
root = sys.argv[1]
html = open(os.path.join(root, "index.html"), encoding="utf-8").read()
srcs = sorted(set(re.findall(r'images/([a-z0-9-]+)\.jpg', html)))
out = os.path.join(root, "images", "opt"); os.makedirs(out, exist_ok=True)
def load(p):
    im = ImageOps.exif_transpose(Image.open(p)); return im.convert("RGB")
def resize(im, w):
    if im.width <= w: return im.copy()
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
total_in = total_out = 0
for name in srcs:
    p = os.path.join(root, "images", name + ".jpg"); total_in += os.path.getsize(p)
    im = load(p)
    for w in (480, 800, 1200):
        r = resize(im, w)
        r.save(f"{out}/{name}-{w}.webp", "WEBP", quality=72, method=6)
        if w in (480, 800):
            r.save(f"{out}/{name}-{w}.avif", "AVIF", quality=55, speed=4)
        if w == 800:
            r.save(f"{out}/{name}-{w}.jpg", "JPEG", quality=76, optimize=True, progressive=True)
    print(name, im.size)
# OG / social image 1200x630
hero = load(os.path.join(root, "images", "instalacion-tuberias-multicapa-bano-eibar.jpg"))
ImageOps.fit(hero, (1200, 630), Image.LANCZOS, centering=(0.5, 0.45)).save(f"{out}/og-mo-house-1200x630.jpg", "JPEG", quality=80, optimize=True, progressive=True)
# Logo variants
logo = ImageOps.exif_transpose(Image.open(os.path.join(root, "images", "logo-mo-house.png"))).convert("RGBA")
for s in (96, 192, 512):
    l = logo.resize((s, s), Image.LANCZOS)
    l.save(f"{out}/logo-mo-house-{s}.png", "PNG", optimize=True)
    l.save(f"{out}/logo-mo-house-{s}.webp", "WEBP", quality=85, method=6)
logo.resize((32, 32), Image.LANCZOS).save(f"{out}/favicon-32.png", "PNG", optimize=True)
logo.resize((180, 180), Image.LANCZOS).convert("RGBA").save(f"{out}/apple-touch-icon-180.png", "PNG", optimize=True)
total_out = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
print("in MB", total_in / 1e6, "out MB (all variants)", total_out / 1e6)
