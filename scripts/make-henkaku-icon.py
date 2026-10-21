#!/usr/bin/env python3
# Draws the HENkaku menu's icon: an ensō (a Zen brush circle), white on transparent, in the manner of
# the HENkaku logo: a thick stroke starting at the lower left with a rounded blob, solid up the left
# side and over the top, turning to dry brush down the right side and breaking into streaks at the
# bottom, leaving the circle open at the lower left. Drawn here from scratch (no copy of the logo).
#
#   python scripts/make-henkaku-icon.py assets/henkaku.png
#
# Needs numpy and Pillow. Rendered at 4x and scaled down for smooth edges.

import math
import sys

import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/henkaku.png"
SIZE = 512
SCALE = 4
N = SIZE * SCALE

rng = np.random.default_rng(1802)  # fixed: the same icon every time

y, x = np.mgrid[0:N, 0:N].astype(np.float32)
cx = cy = N / 2
dx = x - cx
dy = cy - y  # y up
r = np.hypot(dx, dy)
phi = np.degrees(np.arctan2(dy, dx)) % 360.0  # counterclockwise from +x

# The stroke runs clockwise from 212 degrees (about 8 o'clock) round to -90 (6 o'clock):
# s = 0 at the start, 1 at the end
START, SWEEP = 212.0, 302.0
s = ((START - phi) % 360.0) / SWEEP
inside_sweep = s <= 1.0

R0 = N * 0.355
# the brush wanders a little in and out
centre = R0 * (1.0 + 0.025 * np.sin(s * 5.1 + 0.6) + 0.012 * np.sin(s * 13.0))
# thick at the start, fullest over the top, a little thinner as it dries out, tapering at the end
width = N * (0.105 + 0.018 * np.sin(np.clip(s, 0, 1) * math.pi) - 0.02 * np.clip((s - 0.55) / 0.45, 0, 1))
width *= np.where(s > 0.9, np.clip(1.0 - (s - 0.9) / 0.1 * 0.55, 0.3, 1.0), 1.0)
half = width / 2

u = (r - centre) / half  # -1 inner edge .. 1 outer edge
edge = np.clip((half - np.abs(r - centre)) / SCALE, 0.0, 1.0)  # about a pixel of soft edge

# Dry brush from s = 0.5 on: bristle streaks along the stroke (by position across it) that open
# up towards the end, and breaks along it
bristles = 160
ub = np.clip((u + 1.0) / 2.0, 0.0, 0.9999) * bristles
streak_level = rng.random(bristles + 1).astype(np.float32)
bristle = streak_level[ub.astype(np.int32)]
dry = np.clip((s - 0.5) / 0.5, 0.0, 1.0) ** 1.3
# breaks along the stroke, finer towards the end
along = np.sin(s * 220.0 + bristle * 40.0) * 0.5 + 0.5
texture = np.where(bristle < dry * 0.85, 0.0, 1.0)
texture *= np.where((along < dry * 0.45) & (bristle < dry * 1.1), 0.0, 1.0)
# the outer side dries first, as a brush dragged round does
texture *= np.where((u > 0.35) & (bristle < dry * 1.25), 0.0, 1.0)

stroke = np.where(inside_sweep & (np.abs(u) <= 1.0), edge * texture, 0.0)

# The start: a rounded blob where the brush came down
sx = cx + R0 * 1.01 * math.cos(math.radians(START))
sy = cy - R0 * 1.01 * math.sin(math.radians(START))
blob_r = N * 0.064
blob = np.clip((blob_r - np.hypot(x - sx, y - sy)) / SCALE, 0.0, 1.0)

# A few flecks around the end, flicked off the dry brush
specks = np.zeros_like(r)
for _ in range(9):
    t = 0.97 + rng.random() * 0.07
    a = math.radians(START - t * SWEEP)
    rr = R0 * (1.0 + (rng.random() - 0.5) * 0.12)
    px = cx + rr * math.cos(a)
    py = cy - rr * math.sin(a)
    sr = N * (0.0015 + rng.random() * 0.0035)
    specks = np.maximum(specks, np.clip((sr - np.hypot(x - px, y - py)) / SCALE, 0.0, 1.0))

alpha = np.clip(np.maximum(np.maximum(stroke, blob), specks), 0.0, 1.0)

rgba = np.zeros((N, N, 4), dtype=np.uint8)
rgba[..., 0:3] = 248  # a warm white, as ink on rice paper the other way round
rgba[..., 3] = (alpha * 255).astype(np.uint8)
img = Image.fromarray(rgba, "RGBA").resize((SIZE, SIZE), Image.LANCZOS)
img.save(OUT)
print("wrote", OUT)
