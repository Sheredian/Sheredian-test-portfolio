"""Builds the Game2Grow x SNS MoU milestone video.

Frames are drawn with Pillow and piped into ffmpeg. Music is synthesized
with numpy so the video has no outside assets or license issues.

Usage: python3 make_video.py <photo1> <photo2> <collage> <out.mp4>
"""
import math
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1350, 30
XF = 0.7  # crossfade seconds

FONT_DIR = "/usr/share/fonts/opentype/inter/"
F_BLACK = FONT_DIR + "InterDisplay-Black.otf"
F_XBOLD = FONT_DIR + "InterDisplay-ExtraBold.otf"
F_BOLD = FONT_DIR + "InterDisplay-Bold.otf"
F_SEMI = FONT_DIR + "InterDisplay-SemiBold.otf"
F_MED = FONT_DIR + "InterDisplay-Medium.otf"

WHITE = (255, 255, 255)
ACCENT = (255, 181, 71)     # warm gold
CORAL = (255, 122, 122)     # matches the story colour
NAVY = (12, 18, 34)

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


# ---------------------------------------------------------------- images

def load(path):
    return Image.open(path).convert("RGB")


def ken_burns(img, t, dur, box0, box1):
    """Smooth sub-pixel pan/zoom from crop box0 to box1 (x0,y0,x1,y1)."""
    e = ease_in_out(t / dur)
    box = tuple(a + (b - a) * e for a, b in zip(box0, box1))
    return img.resize((W, H), Image.LANCZOS, box=box)


def fit_box(cx, cy, w, img):
    """4:5 crop box of width w centred on (cx, cy), kept inside the image."""
    w = min(w, img.width, img.height * W / H)
    h = w * H / W
    x0 = min(max(cx - w / 2, 0), img.width - w)
    y0 = min(max(cy - h / 2, 0), img.height - h)
    return (x0, y0, x0 + w, y0 + h)


def make_gradient(top_alpha, bottom_alpha, start=0.0):
    g = Image.new("L", (1, H))
    for y in range(H):
        p = y / (H - 1)
        if p < start:
            a = top_alpha
        else:
            q = (p - start) / (1 - start)
            a = top_alpha + (bottom_alpha - top_alpha) * (q ** 0.9)
        g.putpixel((0, y), int(a))
    g = g.resize((W, H))
    layer = Image.new("RGBA", (W, H), NAVY + (0,))
    layer.putalpha(g)
    return layer


GRAD_BOTTOM = make_gradient(30, 250, 0.22)
GRAD_FULL = make_gradient(150, 235, 0.0)
GRAD_TOP = make_gradient(0, 230, 0.55).transpose(Image.FLIP_TOP_BOTTOM)


def vignette():
    v = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(v)
    d.ellipse((-W * 0.25, -H * 0.2, W * 1.25, H * 1.2), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.putalpha(v.point(lambda p: int((255 - p) * 0.55)))
    return layer


VIGNETTE = vignette()


# ---------------------------------------------------------------- text

def draw_lines(base, lines, t, y_start, gap=18, align="center", x_left=80):
    """lines: list of dicts {segs:[(text,color)], font, at, size}.
    Each line slides up and fades in at its own start time."""
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    sd = ImageDraw.Draw(shadow)
    y = y_start
    for ln in lines:
        f = font(ln["font"], ln["size"])
        asc, desc = f.getmetrics()
        lh = asc + desc
        p = ease_out((t - ln["at"]) / 0.7)
        if p > 0:
            alpha = int(255 * p)
            dy = (1 - p) * 46
            total = sum(td.textlength(s, font=f) for s, _ in ln["segs"])
            x = (W - total) / 2 if align == "center" else x_left
            for s, col in ln["segs"]:
                sd.text((x + 2, y + dy + 5), s, font=f, fill=(0, 0, 0, int(alpha * 0.75)))
                td.text((x, y + dy), s, font=f, fill=col + (alpha,))
                x += td.textlength(s, font=f)
            if ln.get("underline"):
                u = ease_out((t - ln["at"] - 0.35) / 0.8)
                if u > 0:
                    ux0 = (W - total) / 2
                    uy = y + dy + lh + 6
                    td.rounded_rectangle((ux0, uy, ux0 + total * u, uy + 10), 5,
                                         fill=ACCENT + (alpha,))
        y += lh + gap
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    base.alpha_composite(shadow)
    base.alpha_composite(text_layer)


def L(text, at, size=60, f=F_BOLD, color=WHITE, **kw):
    segs = text if isinstance(text, list) else [(text, color)]
    return dict(segs=segs, at=at, size=size, font=f, **kw)


def lines_height(lines, gap=18):
    h = 0
    for ln in lines:
        a, d = font(ln["font"], ln["size"]).getmetrics()
        h += a + d + gap
    return h - gap


def heart(draw, cx, cy, s, fill):
    pts = []
    for i in range(200):
        a = 2 * math.pi * i / 200
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * s, cy - y * s))
    draw.polygon(pts, fill=fill)


def kicker(base, text, t, at, y):
    """Small pill label above a block of text."""
    p = ease_out((t - at) / 0.6)
    if p <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(F_SEMI, 30)
    tw = d.textlength(text, font=f)
    pw, ph = tw + 56, 58
    x0 = (W - pw) / 2
    a = int(255 * p)
    d.rounded_rectangle((x0, y, x0 + pw, y + ph), ph / 2, fill=CORAL + (int(a * 0.95),))
    d.text((W / 2, y + ph / 2), text, font=f, fill=WHITE + (a,), anchor="mm")
    base.alpha_composite(layer)


# ---------------------------------------------------------------- backgrounds

def dark_bg(t):
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    for i, (col, r, ph) in enumerate([(CORAL, 420, 0.0), (ACCENT, 360, 2.1), ((90, 120, 255), 380, 4.2)]):
        cx = W / 2 + math.sin(t * 0.35 + ph) * 260
        cy = H / 2 + math.cos(t * 0.28 + ph) * 330
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (70,))
    glow = glow.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(22)).resize((W, H), Image.BILINEAR)
    img.alpha_composite(glow)
    return img


def photo_frame(img, t, dur, b0, b1, grad=GRAD_BOTTOM):
    fr = ken_burns(img, t, dur, b0, b1).convert("RGBA")
    fr.alpha_composite(VIGNETTE)
    fr.alpha_composite(grad)
    return fr


# ---------------------------------------------------------------- scenes

def build_scenes(p1, p2, collage):
    # Collage panels (measured on the 1200x1600 collage).
    speaker = collage.crop((30, 520, 585, 1213))
    speaker = speaker.resize((speaker.width * 2, speaker.height * 2), Image.LANCZOS)
    speaker = speaker.filter(ImageFilter.UnsharpMask(2, 60, 2))
    audience = collage.crop((615, 815, 1178, 1520))
    audience = audience.resize((audience.width * 2, audience.height * 2), Image.LANCZOS)
    audience = audience.filter(ImageFilter.UnsharpMask(2, 60, 2))

    # Collage on a blurred copy of itself so it fills the 4:5 frame.
    cbg = collage.resize((W, int(W * collage.height / collage.width)))
    cbg = cbg.crop((0, (cbg.height - H) // 2, W, (cbg.height - H) // 2 + H))
    cbg = cbg.filter(ImageFilter.GaussianBlur(40))
    s = H / collage.height
    cfit = collage.resize((int(collage.width * s), H), Image.LANCZOS)
    cfull = cbg.copy()
    cfull.paste(cfit, ((W - cfit.width) // 2, 0))

    def s_open(t, dur=6.3):
        # Hook: the news is on screen from the very first frame.
        fr = photo_frame(p1, t, dur, fit_box(960, 700, 900, p1), fit_box(960, 740, 800, p1))
        fr.alpha_composite(GRAD_TOP)
        hp = ease_out((t - 0.9) / 0.5)
        if hp > 0:
            hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            beat = 1 + 0.07 * max(0, math.sin((t - 0.9) * 2 * math.pi * 1.1)) ** 6
            over = 1 + 0.25 * math.sin(min(hp, 1) * math.pi) * (1 - hp)
            heart(ImageDraw.Draw(hl), W / 2, 112, 2.6 * hp * beat * over, (240, 60, 80, int(255 * hp)))
            fr.alpha_composite(hl.filter(ImageFilter.GaussianBlur(14)))
            fr.alpha_composite(hl)
        top = [
            L("A proud and emotional milestone", 0.6, 50, F_BOLD),
            L([("for ", WHITE), ("Game2Grow!", ACCENT)], 0.85, 50, F_BOLD),
        ]
        draw_lines(fr, top, t, 170, gap=8)
        lines = [
            L("Game2Grow has signed its", -0.55, 58, F_SEMI),
            L([("FIRST MoU", ACCENT)], -0.5, 150, F_BLACK, underline=True),
            L("with SNS!", -0.45, 84, F_XBOLD),
        ]
        draw_lines(fr, lines, t, 880, gap=10)
        return fr

    def s_special(t, dur=6.3):
        sb0 = fit_box(555, 640, 1000, speaker)
        sb1 = fit_box(520, 700, 880, speaker)
        fr = photo_frame(speaker, t, dur, sb0, sb1)
        lines = [
            L("What makes this moment", 0.4, 60, F_SEMI),
            L([("truly special", ACCENT), (" is that SNS", WHITE)], 0.7, 60, F_SEMI),
            L("is not just another", 1.0, 60, F_SEMI),
            L("institution for me.", 1.3, 60, F_SEMI),
        ]
        draw_lines(fr, lines, t, 840)
        return fr

    def s_mba(t, dur=8.3):
        b0 = (0, 0, W, H)
        b1 = (W * 0.04, H * 0.0, W * 0.96, H * 0.92)
        fr = ken_burns(cfull, t, dur, b0, b1).convert("RGBA")
        fr.alpha_composite(GRAD_FULL)
        head = [
            L("It is the place where", 0.4, 62, F_SEMI),
            L([("I pursued my ", WHITE), ("MBA,", ACCENT)], 0.7, 86, F_XBOLD),
        ]
        draw_lines(fr, head, t, 250)
        items = ["discovered my potential,", "gained confidence,", "and found the courage", "to face the world."]
        starts = [1.7, 2.9, 4.1, 4.4]
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        f = font(F_BOLD, 56)
        y = 620
        for i, (txt, st) in enumerate(zip(items, starts)):
            p = ease_out((t - st) / 0.6)
            if p > 0:
                a = int(255 * p)
                x = 150 + (1 - p) * -40
                if i < 3:  # check mark bullet on each new idea
                    cy = y + 34
                    d.ellipse((x - 70, cy - 26, x - 18, cy + 26), fill=CORAL + (a,))
                    d.line([(x - 56, cy), (x - 47, cy + 10), (x - 31, cy - 10)], fill=WHITE + (a,), width=6, joint="curve")
                d.text((x, y), txt, font=f, fill=WHITE + (a,))
            y += 92 if i != 2 else 72
        sh = layer.filter(ImageFilter.GaussianBlur(8))
        fr.alpha_composite(sh)
        fr.alpha_composite(layer)
        return fr

    def s_years(t, dur=6.3):
        b0 = fit_box(560, 700, 1000, audience)
        b1 = fit_box(600, 640, 860, audience)
        fr = photo_frame(audience, t, dur, b0, b1)
        kicker(fr, "YEARS AGO", t, 0.3, 790)
        lines = [
            L("Years ago, I walked", 0.5, 66, F_BOLD),
            L("into this campus as a", 0.8, 66, F_BOLD),
            L([("student", ACCENT), (" with dreams.", WHITE)], 1.1, 66, F_BOLD),
        ]
        draw_lines(fr, lines, t, 880)
        return fr

    def s_today(t, dur=7.3):
        fr = photo_frame(p2, t, dur, fit_box(900, 700, 1000, p2), fit_box(960, 760, 820, p2))
        kicker(fr, "TODAY", t, 0.3, 790)
        lines = [
            L("Today, I walk back", 0.5, 66, F_BOLD),
            L([("as an ", WHITE), ("entrepreneur,", ACCENT)], 0.85, 76, F_XBOLD),
            L("with a dream of my own.", 1.5, 62, F_BOLD),
        ]
        draw_lines(fr, lines, t, 880)
        return fr

    def s_outro(t):
        fr = dark_bg(t + 40)
        lines = [
            L([("Game", WHITE), ("2", ACCENT), ("Grow", WHITE)], 0.3, 120, F_BLACK),
        ]
        draw_lines(fr, lines, t, 400)
        cta = [
            L("Want experiential training", 1.0, 56, F_BOLD),
            L([("for your ", WHITE), ("campus or team?", ACCENT)], 1.3, 56, F_BOLD),
        ]
        draw_lines(fr, cta, t, 600, gap=14)
        p2_ = ease_out((t - 2.1) / 0.8)
        if p2_ > 0:
            l2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d2 = ImageDraw.Draw(l2)
            a = int(255 * p2_)
            f = font(F_BOLD, 46)
            txt = "game2growsolutions.com"
            tw = d2.textlength(txt, font=f)
            pw, ph = (tw + 90) * (0.9 + 0.1 * p2_), 96
            d2.rounded_rectangle((W / 2 - pw / 2, 820, W / 2 + pw / 2, 820 + ph), ph / 2, fill=CORAL + (a,))
            d2.text((W / 2, 820 + ph / 2), txt, font=f, fill=WHITE + (a,), anchor="mm")
            fr.alpha_composite(l2)
        return fr

    return [
        (0.0, s_open),
        (6.3, s_special),
        (12.6, s_mba),
        (20.9, s_years),
        (27.2, s_today),
        (34.5, s_outro),
    ]


TOTAL = 41.0


_rng = np.random.default_rng(7)
GRAIN = [(_rng.normal(0, 2.5, (H, W, 1))).astype(np.int16) for _ in range(6)]


def render_frame(scenes, t):
    idx = max(i for i, (st, _) in enumerate(scenes) if st <= t)
    st, fn = scenes[idx]
    fr = fn(t - st)
    if idx > 0 and t - st < XF:
        pst, pfn = scenes[idx - 1]
        prev = pfn(t - pst)
        a = ease_in_out((t - st) / XF)
        fr = Image.blend(prev, fr, a)
    # fade in from / out to black
    k = min(1.0, (TOTAL - t) / 1.2)
    if k < 1:
        fr = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), fr, max(k, 0))
    # light film grain ties the photos together and hides upscaling softness
    arr = np.asarray(fr.convert("RGB"), dtype=np.int16) + GRAIN[(int(t * FPS) // 2) % len(GRAIN)]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- music

def make_music(path, dur=TOTAL, sr=44100):
    n = int(dur * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)

    def midi(m):
        return 440 * 2 ** ((m - 69) / 12)

    # I - V - vi - IV in C, warm and hopeful
    chords = [[48, 55, 60, 64, 67], [43, 55, 59, 62, 67], [45, 57, 60, 64, 69], [41, 53, 57, 60, 65]]
    bar = 4.0
    for b in range(int(math.ceil(dur / bar))):
        ch = chords[b % 4]
        t0 = b * bar
        i0, i1 = int(t0 * sr), min(n, int((t0 + bar + 1.5) * sr))
        tt = t[i0:i1] - t0
        env = np.minimum(1, tt / 0.9) * np.exp(-np.maximum(0, tt - bar) * 2.5)
        for m in ch:
            f = midi(m)
            tone = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt + 0.3) + 0.1 * np.sin(2 * np.pi * 3 * f * tt)
            tone *= 1 + 0.004 * np.sin(2 * np.pi * 0.25 * tt)
            out[i0:i1] += 0.05 * env * tone
        # soft piano-like arpeggio, starts after the intro
        if True:
            arp = [ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12, ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[4] + 19]
            for k, m in enumerate(arp):
                s0 = t0 + k * 0.5
                j0, j1 = int(s0 * sr), min(n, int((s0 + 2.0) * sr))
                if j0 >= n:
                    continue
                u = t[j0:j1] - s0
                f = midi(m)
                e = np.exp(-u * 3.2) * np.minimum(1, u / 0.005)
                out[j0:j1] += 0.07 * e * (np.sin(2 * np.pi * f * u) + 0.25 * np.sin(2 * np.pi * 2 * f * u))
        # low root
        f = midi(ch[0] - 12)
        out[i0:i1] += 0.08 * env * np.sin(2 * np.pi * f * tt)

    # simple reverb via a few feedback delays
    rev = out.copy()
    for d, g in [(0.113, 0.35), (0.173, 0.3), (0.241, 0.25), (0.367, 0.2)]:
        k = int(d * sr)
        tmp = np.zeros(n)
        tmp[k:] = out[:-k] * g
        rev += tmp
    out = 0.7 * out + 0.45 * rev

    fade = np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 3.0)
    out *= np.clip(fade, 0, 1)
    out /= np.max(np.abs(out)) + 1e-9
    out *= 0.6
    stereo = np.stack([out, np.roll(out, int(0.012 * sr))], axis=1)
    data = (stereo * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


# ---------------------------------------------------------------- main

def main():
    p1, p2, col, out = sys.argv[1:5]
    scenes = build_scenes(load(p1), load(p2), load(col))
    if len(sys.argv) > 5 and sys.argv[5] == "--preview":
        for tt in [float(x) for x in sys.argv[6].split(",")]:
            render_frame(scenes, tt).save(f"{out}_{tt:05.1f}.jpg", quality=88)
        return
    wav = out + ".wav"
    make_music(wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-tune", "grain", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "192k", "-shortest", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(TOTAL * FPS)
    for i in range(nframes):
        proc.stdin.write(render_frame(scenes, i / FPS).tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main()
