#!/usr/bin/env python3
"""HENkaku's art from its ensō logo (assets/henkaku-logo.png, transparent):
assets/henkaku.png (512x512, the menus' icon), sce_sys/icon0.png (512x512) and sce_sys/pic1.png (1920x1080).

    python3 scripts/make-henkaku-art.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TEXT = (0xF2, 0xF5, 0xFB)
MUTED = (0x9A, 0xA6, 0xBD)


def logo(size):
    img = Image.open(os.path.join(ROOT, "assets", "henkaku-logo.png")).convert("RGBA")
    img = img.crop(img.getbbox())
    scale = size / max(img.size)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    square.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    return square


def background(w, h):
    """Black, lit softly from the middle, like henkaku.xyz"""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    r = min(w, h) * 0.45
    ImageDraw.Draw(glow).ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), fill=(0x30, 0x34, 0x3C, 255))
    return Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(radius=r / 2)))


def font(size, bold=True):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 os.path.join(ROOT, "fonts", "Roboto-Bold.ttf" if bold else "Roboto-Regular.ttf"),
                 "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def centered(d, y, text, f, fill, w):
    d.text(((w - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def main():
    logo(512).save(os.path.join(ROOT, "assets", "henkaku.png"))

    icon = background(512, 512)
    icon.alpha_composite(logo(330), (91, 52))
    d = ImageDraw.Draw(icon)
    centered(d, 398, "HENkaku", font(64), TEXT, 512)
    icon.convert("RGB").save(os.path.join(ROOT, "sce_sys", "icon0.png"))

    pic = background(1920, 1080)
    pic.alpha_composite(logo(620), (1160, 230))
    d = ImageDraw.Draw(pic)
    d.text((150, 420), "HENkaku", font=font(160), fill=TEXT)
    d.text((160, 610), "PlayStation Vita games on the PS4", font=font(46, bold=False), fill=MUTED)
    d.text((160, 680), "powered by Vita3K", font=font(34, bold=False), fill=MUTED)
    pic.convert("RGB").save(os.path.join(ROOT, "sce_sys", "pic1.png"))
    print("wrote assets/henkaku.png, sce_sys/icon0.png, sce_sys/pic1.png")


if __name__ == "__main__":
    main()
