#!/usr/bin/env python3
"""Draw the background used in the screenshots: a soft dusk gradient, 1920x1080, no third-party images.

    python3 tools/make-background.py out.jpg

Pure standard library. Writes a PNG if the name ends in .png, otherwise shells out to nothing and just
writes a PNG too; convert it with sips or ImageMagick if you want a JPEG.

Why a script instead of a photo: anything pulled off a wallpaper site carries a licence I cannot vouch
for, and the screenshots are the first thing anyone looks at. This is reproducible, it is ours, and it
costs a second to run.
"""

import math
import struct
import sys
import zlib

W, H = 1920, 1080

TOP = (0.012, 0.018, 0.030)   # near black at the very top
MID = (0.035, 0.070, 0.115)   # slate blue through the middle
BOT = (0.045, 0.095, 0.145)   # a touch lighter at the bottom, behind the shelf

# Two lights: a broad cool one in the middle, a tighter one high on the right.
COOL = dict(cx=0.50, cy=0.50, r=0.75, rgb=(0.20, 0.52, 0.72), amp=0.40, power=2.0)
HIGH = dict(cx=0.75, cy=0.20, r=0.60, rgb=(0.34, 0.62, 0.86), amp=0.26, power=2.4)


def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def base(y):
    t = y / (H - 1)
    if t < 0.55:
        k = smooth(t / 0.55)
        return tuple(TOP[i] + (MID[i] - TOP[i]) * k for i in range(3))
    k = smooth((t - 0.55) / 0.45)
    return tuple(MID[i] + (BOT[i] - MID[i]) * k for i in range(3))


def light(px, py, spec):
    """Radial falloff, 1 at the centre and 0 at the radius."""
    dx = (px - W * spec["cx"]) / (W * spec["r"])
    dy = (py - H * spec["cy"]) / (W * spec["r"])
    d = math.sqrt(dx * dx + dy * dy)
    if d >= 1.0:
        return (0.0, 0.0, 0.0)
    f = (1.0 - d) ** spec["power"] * spec["amp"]
    return tuple(c * f for c in spec["rgb"])


def main(out):
    rows = []
    for y in range(H):
        row = bytearray([0])                      # PNG filter byte: none
        r0, g0, b0 = base(y)
        for x in range(W):
            r, g, b = r0, g0, b0
            for spec in (COOL, HIGH):
                lr, lg, lb = light(x, y, spec)
                r += lr
                g += lg
                b += lb

            # vignette, heavier on the vertical axis
            vx = (x / (W - 1) - 0.5) * 2
            vy = (y / (H - 1) - 0.5) * 2
            v = 1.0 - 0.30 * clamp((vx * vx * 0.55 + vy * vy * 0.75) ** 0.85)

            # keep the bottom third dark so the glass shelf reads as glass, not a coloured bar
            if y > H * 0.62:
                v *= 1.0 - 0.42 * smooth((y - H * 0.62) / (H * 0.38))

            # a little dither, otherwise the gradient bands on an 8-bit panel
            n = (((x * 7 + y * 13) % 5) - 2) / 255.0 * 0.5

            row += bytes((
                int(clamp(r * v + n) * 255),
                int(clamp(g * v + n) * 255),
                int(clamp(b * v + n) * 255),
            ))
        rows.append(bytes(row))

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
           + chunk(b"IEND", b""))
    with open(out, "wb") as f:
        f.write(png)
    print("%s: %d bytes" % (out, len(png)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "background.png")
