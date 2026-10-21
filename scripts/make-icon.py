#!/usr/bin/env python3
"""Home screen art for the package: sce_sys/icon0.png (512x512) and sce_sys/pic1.png (1920x1080),
from Vita3K's own logo (vita3k/Vita3K.ico in the source tree).

    python3 scripts/make-icon.py ~/vita3k-build/src/vita3k/vita3k/Vita3K.ico sce_sys
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

TOP = (0x0D, 0x23, 0x47)
BOTTOM = (0x04, 0x07, 0x0F)
ACCENT = (0x5F, 0xC4, 0xFF)


def gradient(w, h):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def bubbles(img, circles):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for (cx, cy, r, color, alpha) in circles:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(img.size) // 60))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def logo(ico_path, size):
    ico = Image.open(ico_path)
    ico.size = (256, 256)
    ico = ico.convert("RGBA")
    return ico.resize((size, size), Image.LANCZOS)


def glow(base, sprite, pos, radius, color):
    """The sprite's silhouette, blurred and tinted, under it."""
    alpha = sprite.split()[3]
    shadow = Image.new("RGBA", sprite.size, color + (0,))
    shadow.putalpha(alpha)
    pad = radius * 3
    canvas = Image.new("RGBA", (sprite.width + 2 * pad, sprite.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(shadow, (pad, pad))
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=radius))
    base.alpha_composite(canvas, (pos[0] - pad, pos[1] - pad))
    base.alpha_composite(sprite, pos)


def font(size, bold=True):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main():
    ico_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    # icon0: the logo on the launcher's colours
    icon = bubbles(gradient(512, 512), [(430, 90, 220, (0x2A, 0x6F, 0xD6), 60), (80, 470, 180, ACCENT, 40)])
    mark = logo(ico_path, 300)
    glow(icon, mark, ((512 - 300) // 2, 64), 18, ACCENT)
    d = ImageDraw.Draw(icon)
    f = font(58)
    text = "Vita3K"
    w = d.textlength(text, font=f)
    d.text(((512 - w) / 2, 380), text, font=f, fill=(0xF2, 0xF5, 0xFB))
    icon.convert("RGB").save(os.path.join(out_dir, "icon0.png"))

    # pic1: the home screen background while the app is selected
    pic = bubbles(gradient(1920, 1080), [(1500, 260, 520, (0x2A, 0x6F, 0xD6), 50), (1350, 980, 360, ACCENT, 34), (220, 1000, 300, (0x2A, 0x6F, 0xD6), 40)])
    mark = logo(ico_path, 560)
    glow(pic, mark, (1180, 250), 30, ACCENT)
    d = ImageDraw.Draw(pic)
    d.text((140, 430), "Vita3K", font=font(150), fill=(0xF2, 0xF5, 0xFB))
    d.text((150, 610), "PlayStation Vita emulator for PS4", font=font(44, bold=False), fill=ACCENT)
    pic.convert("RGB").save(os.path.join(out_dir, "pic1.png"))
    print("wrote", os.path.join(out_dir, "icon0.png"), os.path.join(out_dir, "pic1.png"))


if __name__ == "__main__":
    main()
