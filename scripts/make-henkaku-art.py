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


def buttons():
    """The PlayStation button symbols for the in-game HENkaku menu (assets/buttons, 64x64)"""
    out = os.path.join(ROOT, "assets", "buttons")
    os.makedirs(out, exist_ok=True)
    S, K = 64, 4  # drawn 4x larger, then shrunk: smooth edges
    size = S * K

    def disc():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((2 * K, 2 * K, size - 2 * K, size - 2 * K), fill=(0x20, 0x24, 0x2C, 255))
        return img, d

    def save(img, name):
        img.resize((S, S), Image.LANCZOS).save(os.path.join(out, name))

    c, w = size / 2, 5.5 * K
    img, d = disc()
    s = 13 * K
    d.line((c - s, c - s, c + s, c + s), fill=(0x8F, 0xB6, 0xFF, 255), width=int(w))
    d.line((c - s, c + s, c + s, c - s), fill=(0x8F, 0xB6, 0xFF, 255), width=int(w))
    save(img, "cross.png")
    img, d = disc()
    r = 14 * K
    d.ellipse((c - r, c - r, c + r, c + r), outline=(0xFF, 0x7A, 0x7A, 255), width=int(w))
    save(img, "circle.png")
    img, d = disc()
    s = 13 * K
    d.rectangle((c - s, c - s, c + s, c + s), outline=(0xFF, 0x8A, 0xD8, 255), width=int(w))
    save(img, "square.png")
    img, d = disc()
    s = 16 * K
    pts = [(c, c - s), (c - s, c + s * 0.62), (c + s, c + s * 0.62)]
    d.line(pts + [pts[0]], fill=(0x4F, 0xE0, 0xB0, 255), width=int(w), joint="curve")
    save(img, "triangle.png")
    # the D-pad's left and right
    img, d = disc()
    a, h = 9 * K, 9 * K
    for sign in (-1, 1):
        tip = c + sign * 21 * K
        d.polygon([(tip, c), (tip - sign * a * 1.3, c - h), (tip - sign * a * 1.3, c + h)], fill=(0xE8, 0xEC, 0xF4, 255))
    d.rectangle((c - 4 * K, c - 4 * K, c + 4 * K, c + 4 * K), fill=(0x9A, 0xA6, 0xBD, 255))
    save(img, "left_right.png")


def main():
    buttons()
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
