#!/usr/bin/env python3
"""THE WORLD TODAY - Tuesday 24 November 2026.

Pure Python 3 standard library. Draws a 1024x1024 newspaper front page
summing up the day's world news and writes it to entry.png.

No network, no randomness, no timestamps: two runs write identical bytes.
The output directory comes from MAKEFUN_OUTPUT_DIR, default /output.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 231)
PANEL = (238, 231, 216)
INK = (20, 20, 20)
GREY = (112, 106, 94)
RED = (176, 32, 32)
ORANGE = (198, 98, 16)
BLUE = (28, 68, 120)
TEAL = (14, 110, 104)
YELLOW = (255, 200, 60)
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)


# ---------------------------------------------------------------- canvas

def set_px(buf, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def fill_rect(buf, x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        s = (yy * W + x0) * 3
        buf[s:s + len(row)] = row


def hline(buf, x, y, w, c, t=1):
    fill_rect(buf, x, y, w, t, c)


def vline(buf, x, y, h, c, t=1):
    fill_rect(buf, x, y, t, h, c)


def line(buf, x0, y0, x1, y1, c):
    """Bresenham line."""
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(buf, x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle_outline(buf, cx, cy, r, c):
    """Midpoint circle outline."""
    x = 0
    y = r
    d = 3 - 2 * r
    while y >= x:
        for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                       (cx + x, cy - y), (cx - x, cy - y),
                       (cx + y, cy + x), (cx - y, cy + x),
                       (cx + y, cy - x), (cx - y, cy - x)):
            set_px(buf, px, py, c)
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6


def disc(buf, cx, cy, r, c):
    """Filled circle."""
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(r * r - dy * dy))
        hline(buf, cx - dx, cy + dy, 2 * dx + 1, c)


def ellipse(buf, cx, cy, rx, ry, c):
    """Thin ellipse outline, sampled parametrically."""
    for deg in range(0, 360, 2):
        a = math.radians(deg)
        set_px(buf, cx + int(rx * math.cos(a)), cy + int(ry * math.sin(a)), c)


def polyline(buf, pts, c):
    for a, b in zip(pts, pts[1:]):
        line(buf, a[0], a[1], b[0], b[1], c)


# ---------------------------------------------------------------- font
# A 5x7 bitmap font, drawn by hand: '#' is ink, '.' is blank.
# Seven rows per glyph, five columns each.

FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
}


def text_w(s, sc):
    return len(s) * 6 * sc


def draw_text(buf, x, y, s, sc, color):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == '#':
                    fill_rect(buf, cx + c * sc, y + r * sc, sc, sc, color)
        cx += 6 * sc
    return cx - x


def draw_centered(buf, y, s, sc, color):
    draw_text(buf, (W - text_w(s, sc)) // 2, y, s, sc, color)


def wrap_text(s, sc, max_w):
    lines = []
    cur = ''
    for word in s.split(' '):
        trial = (cur + ' ' + word).strip()
        if text_w(trial, sc) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(buf, x, y, s, sc, max_w, color, leading=None):
    if leading is None:
        leading = 9 * sc
    for ln in wrap_text(s, sc, max_w):
        draw_text(buf, x, y, ln, sc, color)
        y += leading
    return y


# ---------------------------------------------------------------- icons

def globe(buf, cx, cy, r):
    """Wireframe globe with a red crack: the climate story."""
    circle_outline(buf, cx, cy, r, INK)
    ellipse(buf, cx, cy, r, r // 3, INK)
    ellipse(buf, cx, cy, r // 3, r, INK)
    hline(buf, cx - r, cy, 2 * r + 1, INK)
    crack = [(cx + 4, cy - r + 8), (cx + 18, cy - r + 34),
             (cx - 6, cy - r + 62), (cx + 16, cy - r + 92),
             (cx - 8, cy - r + 120), (cx + 10, cy - r + 148),
             (cx - 2, cy + r - 10)]
    polyline(buf, crack, RED)
    # thicken the crack by redrawing it shifted by one pixel
    shifted = [(px + 1, py) for px, py in crack]
    polyline(buf, shifted, RED)


def ship(buf, x, y):
    """Small cargo ship: the Hormuz story."""
    fill_rect(buf, x + 2, y + 16, 36, 8, BLUE)
    line(buf, x + 2, y + 16, x + 8, y + 24, BLUE)
    line(buf, x + 38, y + 16, x + 32, y + 24, BLUE)
    vline(buf, x + 20, y + 2, 14, INK, 2)
    fill_rect(buf, x + 22, y + 2, 10, 6, RED)
    hline(buf, x, y + 27, 44, TEAL, 2)
    hline(buf, x + 8, y + 31, 28, TEAL, 2)


def estonia_flag(buf, x, y):
    """Estonian blue-black-white tricolour on a pole."""
    vline(buf, x, y, 32, INK, 2)
    fill_rect(buf, x + 3, y, 38, 8, BLUE)
    fill_rect(buf, x + 3, y + 8, 38, 8, BLACK)
    fill_rect(buf, x + 3, y + 16, 38, 8, WHITE)
    hline(buf, x + 3, y, 38, INK)
    hline(buf, x + 3, y + 23, 38, INK)
    vline(buf, x + 40, y, 24, INK)
    vline(buf, x + 3, y, 24, INK)


def flame(buf, x, y):
    """Small flame: the Banten fire."""
    cx = x + 18
    disc(buf, cx, y + 18, 12, ORANGE)
    disc(buf, cx, y + 20, 7, RED)
    disc(buf, cx, y + 22, 3, YELLOW)
    line(buf, cx - 10, y + 10, cx, y - 4, ORANGE)
    line(buf, cx + 10, y + 10, cx, y - 4, ORANGE)


def train(buf, x, y):
    """Small train: the Nepal rail link."""
    fill_rect(buf, x + 2, y, 32, 6, TEAL)
    fill_rect(buf, x, y + 4, 36, 18, TEAL)
    fill_rect(buf, x + 6, y + 8, 8, 6, WHITE)
    fill_rect(buf, x + 22, y + 8, 8, 6, WHITE)
    disc(buf, x + 10, y + 26, 4, INK)
    disc(buf, x + 26, y + 26, 4, INK)
    hline(buf, x, y + 30, 40, INK, 2)


def burst(buf, cx, cy, r):
    """Starburst: strikes and explosions for the Kyiv strip."""
    for k in range(12):
        a = math.pi * k / 6
        x1 = cx + int(r * math.cos(a))
        y1 = cy + int(r * math.sin(a))
        line(buf, cx, cy, x1, y1, WHITE)
    disc(buf, cx, cy, 8, RED)
    disc(buf, cx, cy, 3, WHITE)


# ---------------------------------------------------------------- layout

MARGIN = 30
CW = W - 2 * MARGIN  # 964


def draw_page(buf):
    # --- masthead
    hline(buf, MARGIN, 26, CW, INK, 5)
    draw_centered(buf, 40, "THE WORLD TODAY", 9, INK)
    draw_centered(buf, 116, "TUESDAY, 24 NOVEMBER 2026", 3, INK)
    hline(buf, MARGIN, 126, 228, INK, 2)
    hline(buf, W - MARGIN - 228, 126, 228, INK, 2)
    hline(buf, MARGIN, 150, CW, RED, 4)

    # --- lead story: COP31
    globe(buf, 125, 280, 88)
    draw_text(buf, 240, 176, "CLIMATE - COP31 - ANTALYA", 2, RED)
    draw_text(buf, 240, 204, "COP31 COLLAPSES", 6, INK)
    draw_text(buf, 240, 252, "NO FOSSIL-FUEL DEAL", 6, INK)
    draw_block(buf, 240, 312,
               "Climate talks in Antalya, Turkiye end in deadlock. "
               "194 nations reject the draft pact, which never mentions "
               "fossil fuels, so the EU and island states refuse to sign it.",
               2, 754, INK, 20)
    hline(buf, MARGIN, 398, CW, INK, 2)

    # --- four secondary stories, 2 x 2 grid
    col_w = 468
    row1_y = 414
    row2_y = 580
    vline(buf, 511, row1_y, 316, GREY, 2)
    hline(buf, MARGIN, 566, CW, GREY, 2)

    def cell(x, y, bar, kicker, head1, head2, body, icon):
        fill_rect(buf, x, y, 6, 138, bar)
        draw_text(buf, x + 16, y, kicker, 2, RED)
        draw_text(buf, x + 16, y + 28, head1, 3, INK)
        draw_text(buf, x + 16, y + 53, head2, 3, INK)
        draw_block(buf, x + 16, y + 86, body, 2, col_w - 16, INK, 20)
        icon(buf, x + col_w - 48, y)

    cell(MARGIN, row1_y, BLUE, "STRAIT OF HORMUZ",
         "25 SEAFARERS", "KILLED AT SEA",
         "UN counts 25 seafarers killed in attacks around the strait, "
         "a vital oil shipping lane.", ship)
    cell(526, row1_y, RED, "ESTONIA - RUSSIA",
         "RUSSIA WARNS OF", "'OPEN WAR'",
         "Moscow warns of open war if Estonia closes its border "
         "as planned.", estonia_flag)
    cell(MARGIN, row2_y, ORANGE, "BANTEN, INDONESIA",
         "FACTORY FIRE", "KILLS 24",
         "A candy factory fire kills 24 people, with around 30 "
         "more missing.", flame)
    cell(526, row2_y, TEAL, "INDIA - NEPAL",
         "INDIA PLEDGES", "$1.6BN TO NEPAL",
         "India pledges $1.6 billion in aid after floods, plus a "
         "new rail link.", train)

    # --- dark strip: Kyiv + Sparta II
    fill_rect(buf, MARGIN, 748, CW, 110, BLACK)
    burst(buf, 78, 803, 26)
    draw_text(buf, 122, 768, "KYIV HIT AS SHIP BURNS AT SEA", 3, WHITE)
    draw_block(buf, 122, 806,
               "Russian strikes hit the Kyiv region, and cargo ship "
               "Sparta II burns in the Gulf of Finland.",
               2, 856, WHITE, 20)

    # --- footer: also today
    draw_text(buf, MARGIN, 890, "ALSO TODAY - ", 2, RED)
    draw_text(buf, MARGIN + text_w("ALSO TODAY - ", 2), 890,
              "VERSTAPPEN WINS LAS VEGAS GP - ALCARAZ WINS MAIDEN ATP FINALS",
              2, INK)
    draw_text(buf, MARGIN, 916, "BEPICOLOMBO ENTERS MERCURY ORBIT", 2, INK)
    draw_text(buf, MARGIN, 942,
              "WORLD CHESS CHAMPIONSHIP OPENS IN GENEVA - GUKESH VS SINDAROV",
              2, INK)
    draw_centered(buf, 968,
                  "Compiled from world news reports of 24 November 2026.",
                  2, GREY)


# ---------------------------------------------------------------- PNG

def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return out


def write_png(path, buf, w, h):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += _chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def main():
    buf = bytearray(bytes(PAPER) * (W * H))
    draw_page(buf)
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, 'entry.png'), buf, W, H)


if __name__ == '__main__':
    main()
