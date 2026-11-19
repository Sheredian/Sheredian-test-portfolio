"""Character and background drawing for the Hallen video. Everything is drawn at 2x and scaled down."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersample

# palette
SKIN_H = (176, 112, 72, 255)       # Hallen warm brown
SKIN_H_SH = (150, 92, 58, 255)
HAIR = (22, 18, 20, 255)
SHIRT = (170, 230, 206, 255)       # mint
SHIRT_SH = (140, 205, 180, 255)
PANTS = (30, 30, 38, 255)
SANDAL = (122, 74, 42, 255)
CAR = (47, 111, 214, 255)
SKIN_J = (201, 146, 104, 255)      # Jesus olive brown
HAIR_J = (82, 52, 32, 255)
ROBE = (250, 247, 238, 255)
ROBE_SH = (226, 220, 206, 255)
SASH = (163, 37, 43, 255)
LINE = (60, 40, 35, 255)
WHITE = (255, 255, 255, 255)


def limb(d, pts, w, col, joint=True):
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=col, width=w)
    if joint:
        r = w // 2
        for p in pts:
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)


def circ(d, c, r, col, outline=None, width=1):
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col, outline=outline, width=width)


def down(img, scale=SS):
    return img.resize((img.width // scale, img.height // scale), Image.LANCZOS)


# ---------------------------------------------------------------- Hallen
H_ARMS = {
    'down':  ([(140, 270), (120, 350), (124, 432)], [(260, 270), (280, 350), (276, 432)]),
    'hold':  ([(140, 270), (120, 350), (172, 388)], [(260, 270), (280, 350), (228, 388)]),
    'scratch': ([(140, 270), (120, 350), (172, 388)], [(260, 270), (306, 210), (262, 108)]),
    'sing':  ([(140, 270), (92, 218), (58, 150)], [(260, 270), (308, 218), (342, 150)]),
    'pray':  ([(140, 270), (128, 350), (190, 335)], [(260, 270), (272, 350), (210, 335)]),
    'count': ([(140, 270), (122, 352), (182, 372)], [(260, 270), (290, 345), (246, 292)]),
    'run1':  ([(140, 270), (104, 330), (118, 395)], [(260, 270), (300, 318), (318, 262)]),
    'run2':  ([(140, 270), (100, 318), (82, 262)], [(260, 270), (296, 330), (282, 395)]),
    'bag':   ([(140, 270), (140, 345), (160, 290)], [(260, 270), (260, 345), (240, 290)]),
    'hug':   ([(140, 270), (110, 230), (100, 170)], [(260, 270), (290, 230), (300, 170)]),
}
H_LEGS = {
    'stand': ([(170, 452), (162, 570), (164, 686)], [(230, 452), (238, 570), (236, 686)]),
    'sit':   ([(170, 452), (160, 512), (160, 612)], [(230, 452), (240, 512), (240, 612)]),
    'run1':  ([(170, 452), (132, 556), (112, 660)], [(230, 452), (262, 552), (300, 610)]),
    'run2':  ([(170, 452), (138, 552), (100, 610)], [(230, 452), (268, 556), (288, 660)]),
}


def hallen_face(d, eyes='open', mouth='smile', brows='normal'):
    cx, cy = 200, 150
    # hair back
    d.ellipse([116, 50, 284, 196], fill=HAIR)
    # ears
    d.ellipse([110, 138, 136, 182], fill=SKIN_H)
    d.ellipse([264, 138, 290, 182], fill=SKIN_H)
    # face
    d.ellipse([125, 72, 275, 238], fill=SKIN_H)
    # side swept fringe, parted on his right
    d.polygon([(124, 128), (132, 84), (170, 58), (236, 60), (276, 92), (280, 132),
               (262, 112), (230, 100), (196, 104), (162, 112), (138, 128)], fill=HAIR)
    d.line([(150, 78), (228, 66)], fill=(70, 62, 66, 255), width=3)
    # cheeks
    d.ellipse([140, 182, 168, 200], fill=(205, 120, 100, 110))
    d.ellipse([232, 182, 260, 200], fill=(205, 120, 100, 110))
    # brows
    if brows == 'confused':
        d.line([(152, 128), (186, 136)], fill=HAIR, width=6)
        d.line([(214, 132), (248, 122)], fill=HAIR, width=6)
    elif brows == 'up':
        d.line([(154, 122), (186, 120)], fill=HAIR, width=6)
        d.line([(214, 120), (246, 122)], fill=HAIR, width=6)
    else:
        d.line([(154, 130), (186, 127)], fill=HAIR, width=6)
        d.line([(214, 127), (246, 130)], fill=HAIR, width=6)
    # eyes
    for ex in (172, 228):
        if eyes == 'open':
            d.ellipse([ex - 14, 142, ex + 14, 176], fill=WHITE)
            circ(d, (ex, 161), 11, (52, 30, 20, 255))
            circ(d, (ex, 161), 5, (10, 6, 6, 255))
            circ(d, (ex + 4, 155), 4, WHITE)
        elif eyes == 'happy':
            d.arc([ex - 14, 150, ex + 14, 176], 200, 340, fill=(30, 20, 20, 255), width=5)
        else:  # closed
            d.arc([ex - 14, 140, ex + 14, 166], 20, 160, fill=(30, 20, 20, 255), width=5)
    # nose
    d.arc([190, 168, 210, 190], 30, 150, fill=SKIN_H_SH, width=4)
    # mouth
    if mouth == 'smile':
        d.arc([178, 180, 222, 214], 20, 160, fill=(90, 30, 30, 255), width=5)
    elif mouth == 'open':
        d.ellipse([184, 194, 216, 222], fill=(110, 30, 35, 255))
        d.ellipse([192, 208, 210, 222], fill=(220, 110, 110, 255))
    elif mouth == 'big':
        d.chord([174, 184, 226, 228], 0, 180, fill=(110, 30, 35, 255))
        d.rectangle([182, 206, 218, 211], fill=WHITE)
    elif mouth == 'o':
        d.ellipse([191, 196, 209, 218], fill=(110, 30, 35, 255))
    else:  # flat
        d.line([(186, 204), (214, 202)], fill=(90, 30, 30, 255), width=5)


def bible(d, box, open_=True):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 6, fill=(100, 56, 28, 255))
    if open_:
        mx = (x0 + x1) // 2
        d.rectangle([x0 + 5, y0 - 6, mx - 2, y1 - 6], fill=(252, 248, 236, 255))
        d.rectangle([mx + 2, y0 - 6, x1 - 5, y1 - 6], fill=(252, 248, 236, 255))
        for i in range(5):
            yy = y0 + 4 + i * (y1 - y0 - 16) / 5
            d.line([(x0 + 11, yy), (mx - 8, yy)], fill=(170, 160, 150, 255), width=2)
            d.line([(mx + 8, yy), (x1 - 11, yy)], fill=(170, 160, 150, 255), width=2)
    else:
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        d.line([(cx, cy - 16), (cx, cy + 16)], fill=(230, 190, 90, 255), width=5)
        d.line([(cx - 10, cy - 6), (cx + 10, cy - 6)], fill=(230, 190, 90, 255), width=5)


@lru_cache(maxsize=None)
def hallen(arms='hold', legs='sit', eyes='open', mouth='smile', brows='normal', book=None):
    """Returns (RGBA image at final size, feet y at final size, centre x)."""
    W, H = 400, 760
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if book is None:
        book = arms in ('hold', 'scratch')
    # school bag behind
    if arms == 'bag':
        d.rounded_rectangle([96, 250, 304, 520], 40, fill=(214, 64, 52, 255))
        d.rounded_rectangle([120, 400, 280, 500], 20, fill=(186, 48, 40, 255))
    # legs
    lp = H_LEGS[legs]
    for leg in lp:
        limb(d, leg, 58, PANTS)
    if legs == 'sit':
        d.ellipse([118, 430, 282, 500], fill=PANTS)
        circ(d, (160, 492), 36, (40, 40, 50, 255))
        circ(d, (240, 492), 36, (40, 40, 50, 255))
    for leg in lp:
        fx, fy = leg[-1]
        d.ellipse([fx - 22, fy - 6, fx + 22, fy + 12], fill=SKIN_H)
        d.ellipse([fx - 30, fy + 2, fx + 30, fy + 22], fill=SANDAL)
    # torso
    d.rounded_rectangle([128, 246, 272, 462], 34, fill=SHIRT)
    d.rectangle([128, 430, 272, 462], fill=SHIRT)
    d.rectangle([186, 236, 214, 256], fill=SKIN_H_SH)
    d.chord([178, 238, 222, 268], 0, 180, fill=SKIN_H_SH)
    # car print
    d.rounded_rectangle([160, 318, 240, 352], 10, fill=CAR)
    d.polygon([(178, 318), (190, 300), (216, 300), (228, 318)], fill=CAR)
    d.rectangle([186, 304, 218, 316], fill=(200, 230, 255, 255))
    circ(d, (178, 354), 9, (20, 20, 20, 255))
    circ(d, (222, 354), 9, (20, 20, 20, 255))
    if arms == 'bag':
        d.line([(150, 252), (150, 420)], fill=(150, 36, 30, 255), width=12)
        d.line([(250, 252), (250, 420)], fill=(150, 36, 30, 255), width=12)
    # arms
    la, ra = H_ARMS[arms]
    for i, arm in enumerate((la, ra)):
        limb(d, arm, 30, SKIN_H)
        # sleeve
        sx, sy = arm[0]
        ex, ey = arm[1]
        mx, my = sx + (ex - sx) * 0.55, sy + (ey - sy) * 0.55
        limb(d, [(sx, sy), (mx, my)], 44, SHIRT)
        hx, hy = arm[-1]
        circ(d, (hx, hy), 18, SKIN_H)
        # wrist bits: bracelet on his right (viewer left), watch on his left (viewer right)
        px, py = arm[-2]
        wx, wy = hx + (px - hx) * 0.28, hy + (py - hy) * 0.28
        if i == 0:
            circ(d, (wx, wy), 16, (210, 210, 220, 255))
            circ(d, (wx, wy), 12, (180, 180, 190, 255))
        else:
            circ(d, (wx, wy), 15, (25, 25, 25, 255))
    if book:
        if arms == 'scratch':
            bible(d, [140, 352, 214, 400], True)
            circ(d, (172, 392), 18, SKIN_H)
        else:
            bible(d, [150, 346, 250, 402], True)
            circ(d, (166, 392), 18, SKIN_H)
            circ(d, (234, 392), 18, SKIN_H)
    if arms == 'pray':
        d.polygon([(200, 300), (184, 340), (216, 340)], fill=SKIN_H)
        d.ellipse([182, 310, 218, 352], fill=SKIN_H)
        d.line([(200, 306), (200, 350)], fill=SKIN_H_SH, width=3)
    if arms == 'count':
        d.line([(244, 290), (240, 256)], fill=SKIN_H, width=12)
    # head on top
    hallen_face(d, eyes, mouth, brows)
    out = down(im)
    feet = max(p[-1][1] for p in lp) + 22
    return out, feet // SS, W // (2 * SS)


# ---------------------------------------------------------------- Jesus
J_ARMS = {
    'stand': ([(200, 340), (172, 520), (196, 680)], [(360, 340), (388, 520), (364, 680)]),
    'open':  ([(200, 340), (140, 500), (110, 600)], [(360, 340), (420, 500), (450, 600)]),
    'rest':  ([(200, 340), (176, 520), (236, 640)], [(360, 340), (384, 520), (324, 640)]),
    'point': ([(200, 340), (130, 470), (60, 530)], [(360, 340), (384, 520), (324, 640)]),
    'clap1': ([(200, 340), (186, 500), (266, 520)], [(360, 340), (374, 500), (294, 520)]),
    'clap2': ([(200, 340), (180, 500), (240, 500)], [(360, 340), (380, 500), (320, 500)]),
    'touch': ([(200, 340), (120, 400), (40, 440)], [(360, 340), (384, 520), (324, 640)]),
    'bless': ([(200, 340), (110, 330), (50, 250)], [(360, 340), (384, 520), (324, 640)]),
}


def jesus_face(d, eyes='open', mouth='smile'):
    # long hair behind
    d.polygon([(196, 150), (364, 150), (392, 352), (338, 362), (280, 320), (222, 362), (168, 352)], fill=HAIR_J)
    d.ellipse([196, 62, 364, 250], fill=HAIR_J)
    # neck
    d.rectangle([260, 260, 300, 312], fill=(180, 126, 88, 255))
    # face
    d.ellipse([214, 92, 346, 270], fill=SKIN_J)
    # hair front, centre parting
    d.polygon([(280, 78), (232, 96), (212, 150), (212, 220), (226, 160), (252, 112), (280, 98)], fill=HAIR_J)
    d.polygon([(280, 78), (328, 96), (348, 150), (348, 220), (334, 160), (308, 112), (280, 98)], fill=HAIR_J)
    # beard
    d.chord([216, 140, 344, 296], 10, 170, fill=HAIR_J)
    d.ellipse([244, 210, 316, 240], fill=HAIR_J)  # moustache
    # brows
    d.arc([226, 140, 266, 170], 200, 330, fill=HAIR_J, width=6)
    d.arc([294, 140, 334, 170], 210, 340, fill=HAIR_J, width=6)
    for ex in (248, 312):
        if eyes == 'open':
            d.ellipse([ex - 14, 168, ex + 14, 190], fill=WHITE)
            circ(d, (ex, 179), 9, (70, 40, 22, 255))
            circ(d, (ex + 3, 175), 3, WHITE)
            d.arc([ex - 15, 164, ex + 15, 190], 200, 340, fill=(60, 34, 24, 255), width=4)
        else:
            d.arc([ex - 14, 168, ex + 14, 192], 200, 340, fill=(50, 30, 20, 255), width=5)
    d.arc([270, 186, 290, 214], 40, 140, fill=(160, 104, 70, 255), width=4)
    if mouth == 'open':
        d.ellipse([266, 232, 294, 254], fill=(100, 34, 34, 255))
    else:
        d.arc([258, 222, 302, 252], 25, 155, fill=(110, 40, 36, 255), width=5)


@lru_cache(maxsize=None)
def jesus(arms='rest', pose='sit', eyes='open', mouth='smile'):
    W, H = 560, 1120
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if pose == 'stand':
        robe = [(196, 320), (364, 320), (420, 1050), (140, 1050)]
        feet = [(232, 1066), (328, 1066)]
    else:
        robe = [(196, 320), (364, 320), (404, 700), (440, 830), (420, 900), (140, 900), (120, 830), (156, 700)]
        feet = [(228, 916), (332, 916)]
    for fx, fy in feet:
        d.ellipse([fx - 30, fy - 18, fx + 30, fy + 12], fill=SKIN_J)
        d.ellipse([fx - 36, fy, fx + 36, fy + 22], fill=SANDAL)
    d.polygon(robe, fill=ROBE)
    d.ellipse([176, 296, 384, 380], fill=ROBE)
    # folds
    for x in (240, 280, 320):
        d.line([(x, 520), (x + (x - 280) * 0.3, robe[3][1] - 20 if pose == 'stand' else 880)], fill=ROBE_SH, width=4)
    if pose == 'sit':
        d.ellipse([120, 640, 440, 790], fill=ROBE)
        d.arc([120, 640, 440, 790], 0, 180, fill=ROBE_SH, width=5)
        d.line([(280, 720), (280, 880)], fill=ROBE_SH, width=4)
    # sash over his right shoulder (viewer left) to the other hip
    d.polygon([(196, 318), (250, 302), (380, 640), (392, 720), (340, 700)], fill=SASH)
    # arms in wide sleeves
    la, ra = J_ARMS[arms]
    for arm in (la, ra):
        limb(d, arm[:2], 62, ROBE)
        sx, sy = arm[1]
        hx, hy = arm[2]
        mx, my = sx + (hx - sx) * 0.75, sy + (hy - sy) * 0.75
        limb(d, [(sx, sy), (mx, my)], 58, ROBE)
        d.line([(sx, sy), (mx, my)], fill=ROBE_SH, width=3)
        limb(d, [(mx, my), (hx, hy)], 26, SKIN_J)
        circ(d, (hx, hy), 24, SKIN_J)
    jesus_face(d, eyes, mouth)
    out = down(im)
    return out, (max(f[1] for f in feet) + 22) // SS, W // (2 * SS)


# ---------------------------------------------------------------- Mom
@lru_cache(maxsize=None)
def mom(arms='down', eyes='open', mouth='smile'):
    W, H = 400, 820
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    skin = (170, 108, 72, 255)
    saree = (226, 96, 60, 255)
    border = (232, 186, 60, 255)
    d.polygon([(130, 260), (270, 260), (310, 800), (90, 800)], fill=saree)
    d.line([(96, 790), (304, 790)], fill=border, width=14)
    d.polygon([(250, 262), (280, 262), (150, 560), (124, 540)], fill=(196, 70, 50, 255))
    d.line([(266, 262), (138, 552)], fill=border, width=8)
    if arms == 'hug':
        A = ([(140, 290), (110, 400), (200, 470)], [(260, 290), (290, 400), (200, 470)])
    else:
        A = ([(140, 290), (120, 420), (130, 540)], [(260, 290), (280, 420), (270, 540)])
    for arm in A:
        limb(d, arm[:2], 34, (226, 96, 60, 255))
        limb(d, arm[1:], 28, skin)
        circ(d, arm[-1], 18, skin)
        circ(d, (arm[2][0] + (arm[1][0] - arm[2][0]) * 0.2, arm[2][1] + (arm[1][1] - arm[2][1]) * 0.2), 15, (230, 180, 60, 255))
    # head
    d.ellipse([140, 40, 260, 120], fill=HAIR)
    circ(d, (200, 50), 34, HAIR)  # bun
    d.rectangle([186, 220, 214, 262], fill=skin)
    d.ellipse([136, 70, 264, 240], fill=skin)
    d.chord([134, 60, 266, 170], 180, 360, fill=HAIR)
    circ(d, (200, 128), 6, (190, 20, 30, 255))
    for ex in (172, 228):
        if eyes == 'open':
            d.ellipse([ex - 12, 150, ex + 12, 174], fill=WHITE)
            circ(d, (ex, 162), 8, (40, 24, 18, 255))
        else:
            d.arc([ex - 12, 152, ex + 12, 176], 200, 340, fill=(40, 24, 18, 255), width=5)
    d.arc([180, 184, 220, 214], 20, 160, fill=(130, 30, 40, 255), width=5)
    out = down(im)
    return out, 800 // SS, W // (2 * SS)


# ---------------------------------------------------------------- small icons
def person_icon(kind, size=150):
    S = size * SS
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = S / 300
    def P(*v):
        return [x * k for x in v]
    ring = {'mom': (226, 96, 60), 'dad': (60, 120, 200), 'grandma': (150, 90, 170),
            'friend': (60, 160, 90), 'lunch': (230, 170, 40), 'love': (220, 70, 100)}[kind]
    d.ellipse(P(6, 6, 294, 294), fill=(255, 251, 240, 245), outline=ring + (255,), width=int(12 * k))
    skin = (176, 112, 72, 255)
    if kind in ('mom', 'dad', 'grandma', 'friend'):
        hair = (235, 235, 235, 255) if kind == 'grandma' else HAIR
        d.ellipse(P(80, 70, 220, 170), fill=hair)
        if kind in ('mom', 'grandma'):
            d.ellipse(P(118, 34, 182, 98), fill=hair)
        body = {'mom': (226, 96, 60, 255), 'dad': (240, 240, 240, 255), 'grandma': (150, 90, 170, 255), 'friend': (250, 200, 60, 255)}[kind]
        d.chord(P(60, 200, 240, 340), 180, 360, fill=body)
        d.ellipse(P(92, 84, 208, 222), fill=skin)
        d.chord(P(90, 72, 210, 150), 180, 360, fill=hair)
        for ex in (128, 172):
            d.arc(P(ex - 12, 136, ex + 12, 160), 200, 340, fill=(30, 20, 20, 255), width=int(6 * k))
        d.arc(P(126, 160, 174, 200), 20, 160, fill=(130, 30, 40, 255), width=int(6 * k))
        if kind == 'mom':
            d.ellipse(P(144, 116, 156, 128), fill=(190, 20, 30, 255))
        if kind == 'dad':
            d.chord(P(122, 168, 178, 192), 180, 360, fill=HAIR)
        if kind == 'grandma':
            d.ellipse(P(110, 132, 146, 164), outline=(90, 70, 60, 255), width=int(4 * k))
            d.ellipse(P(154, 132, 190, 164), outline=(90, 70, 60, 255), width=int(4 * k))
        if kind == 'friend':
            d.ellipse(P(196, 196, 262, 262), fill=(230, 80, 60, 255))
            d.arc(P(196, 196, 262, 262), 300, 60, fill=WHITE, width=int(5 * k))
    elif kind == 'lunch':
        for i, y in enumerate((90, 140, 190)):
            d.rounded_rectangle(P(90, y, 210, y + 46), int(10 * k), fill=(196, 202, 210, 255), outline=(150, 156, 166, 255), width=int(4 * k))
        d.arc(P(110, 46, 190, 120), 180, 360, fill=(150, 156, 166, 255), width=int(8 * k))
    elif kind == 'love':
        heart(d, 150 * k, 160 * k, 80 * k, (220, 70, 100, 255))
    return im.resize((size, size), Image.LANCZOS)


def heart(d, cx, cy, r, col):
    d.ellipse([cx - r, cy - r * 0.9, cx, cy + r * 0.1], fill=col)
    d.ellipse([cx, cy - r * 0.9, cx + r, cy + r * 0.1], fill=col)
    d.polygon([(cx - r * 0.97, cy - r * 0.25), (cx + r * 0.97, cy - r * 0.25), (cx, cy + r)], fill=col)


def glow(radius, col=(255, 214, 120), strength=170):
    S = radius * 2
    im = Image.new('RGBA', (S, S), col + (0,))
    px = im.load()
    for y in range(S):
        for x in range(S):
            dd = math.hypot(x - radius, y - radius) / radius
            if dd < 1:
                px[x, y] = col + (int(strength * (1 - dd) ** 2),)
    return im


# ---------------------------------------------------------------- background
def coconut_tree(d, base, height, lean, s=1.0):
    bx, by = base
    pts = []
    for i in range(30):
        t = i / 29
        x = bx + lean * t * t
        y = by - height * t
        pts.append((x, y))
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        w = int((34 - 14 * i / 29) * s)
        d.line([a, b], fill=(120, 88, 58, 255), width=w)
        if i % 2 == 0:
            d.line([(a[0] - w / 2, a[1]), (a[0] + w / 2, a[1])], fill=(96, 68, 44, 255), width=3)
    tx, ty = pts[-1]
    for ang in range(0, 360, 40):
        a = math.radians(ang + 10)
        L = 200 * s
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.55 + 50 * s
        mx, my = tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.3 - 30 * s
        d.line([(tx, ty), (mx, my), (ex, ey)], fill=(46, 120, 60, 255), width=int(16 * s), joint='curve')
        for j in range(1, 8):
            t = j / 8
            px = tx + (ex - tx) * t
            py = ty + (ey - ty) * t - 30 * s * math.sin(math.pi * t)
            d.line([(px, py), (px + math.cos(a + 1.2) * 40 * s, py + 40 * s)], fill=(60, 140, 70, 255), width=int(7 * s))
            d.line([(px, py), (px + math.cos(a - 1.2) * 40 * s, py + 40 * s)], fill=(60, 140, 70, 255), width=int(7 * s))
    for c in ((tx - 18 * s, ty + 26 * s), (tx + 14 * s, ty + 30 * s), (tx, ty + 44 * s)):
        circ(d, c, 16 * s, (110, 140, 50, 255))


def house_bg(W=720, H=1280):
    S = SS
    im = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    # sky gradient
    top, mid, low = (255, 166, 110), (255, 204, 140), (255, 232, 190)
    for y in range(0, 1000 * S):
        t = y / (1000 * S)
        if t < 0.6:
            u = t / 0.6
            c = tuple(int(top[i] + (mid[i] - top[i]) * u) for i in range(3))
        else:
            u = (t - 0.6) / 0.4
            c = tuple(int(mid[i] + (low[i] - mid[i]) * u) for i in range(3))
        d.line([(0, y), (W * S, y)], fill=c + (255,))
    # sun
    for r, a in ((260, 40), (190, 70), (130, 255)):
        circ(d, (560 * S, 360 * S), r, (255, 236, 170, a) if a < 255 else (255, 238, 180, 255))
    # far hills
    d.polygon([(0, 760 * S), (200 * S, 690 * S), (420 * S, 740 * S), (720 * S, 680 * S), (720 * S, 900 * S), (0, 900 * S)], fill=(160, 170, 110, 255))
    # trees behind house
    coconut_tree(d, (90 * S, 930 * S), 620 * S, -60 * S, 1.6)
    coconut_tree(d, (650 * S, 930 * S), 700 * S, 70 * S, 1.7)
    # ground
    for y in range(880 * S, H * S):
        t = (y - 880 * S) / ((H - 880) * S)
        c = (int(122 - 30 * t), int(170 - 40 * t), int(84 - 20 * t))
        d.line([(0, y), (W * S, y)], fill=c + (255,))
    # house
    d.rectangle([90 * S, 560 * S, 630 * S, 900 * S], fill=(244, 226, 190, 255))
    d.rectangle([90 * S, 860 * S, 630 * S, 900 * S], fill=(214, 190, 150, 255))
    d.polygon([(60 * S, 575 * S), (360 * S, 440 * S), (660 * S, 575 * S)], fill=(184, 82, 52, 255))
    for i in range(1, 9):
        y = 440 + i * 15
        d.line([((360 - (300 * i / 9)) * S, y * S), ((360 + (300 * i / 9)) * S, y * S)], fill=(160, 66, 42, 255), width=3 * S)
    d.rectangle([60 * S, 570 * S, 660 * S, 586 * S], fill=(150, 60, 40, 255))
    # pillars
    for x in (110, 600):
        d.rectangle([(x - 10) * S, 586 * S, (x + 10) * S, 900 * S], fill=(230, 210, 175, 255))
    # door
    d.rectangle([300 * S, 660 * S, 420 * S, 842 * S], fill=(66, 40, 28, 255))
    d.rectangle([292 * S, 652 * S, 428 * S, 662 * S], fill=(120, 74, 42, 255))
    d.rectangle([292 * S, 652 * S, 302 * S, 842 * S], fill=(120, 74, 42, 255))
    d.rectangle([418 * S, 652 * S, 428 * S, 842 * S], fill=(120, 74, 42, 255))
    # door warm interior light
    d.rectangle([306 * S, 668 * S, 414 * S, 842 * S], fill=(88, 56, 36, 255))
    # kolam on floor in front of door is skipped; windows
    for x0 in (150, 470):
        d.rectangle([x0 * S, 660 * S, (x0 + 100) * S, 770 * S], fill=(110, 140, 160, 255))
        d.rectangle([x0 * S, 660 * S, (x0 + 100) * S, 770 * S], outline=(120, 74, 42, 255), width=8 * S)
        for k in range(1, 4):
            xx = x0 + k * 25
            d.line([(xx * S, 664 * S), (xx * S, 766 * S)], fill=(80, 80, 80, 255), width=3 * S)
    # steps
    for (x0, x1, y0, y1) in ((200, 520, 920, 965), (232, 488, 882, 922), (262, 458, 842, 884)):
        d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=(196, 196, 190, 255))
        d.rectangle([x0 * S, y0 * S, x1 * S, (y0 + 8) * S], fill=(222, 222, 216, 255))
        d.line([(x0 * S, y1 * S), (x1 * S, y1 * S)], fill=(150, 150, 146, 255), width=3 * S)
    # bushes
    for cx, cy, r in ((120, 930, 70), (60, 960, 60), (610, 930, 74), (680, 960, 60)):
        circ(d, (cx * S, cy * S), r * S, (64, 128, 66, 255))
        circ(d, ((cx - 20) * S, (cy - 24) * S), (r * 0.6) * S, (84, 150, 80, 255))
    out = im.resize((W, H), Image.LANCZOS).convert('RGB')
    return out


def sepia(img):
    g = img.convert('L')
    return Image.merge('RGB', (g.point(lambda v: min(255, int(v * 1.08 + 10))),
                               g.point(lambda v: int(v * 0.92 + 6)),
                               g.point(lambda v: int(v * 0.72))))
