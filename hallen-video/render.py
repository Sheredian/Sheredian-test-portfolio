import math, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from art import hallen, jesus, mom, person_icon, glow, house_bg, sepia, heart

W, H, FPS = 720, 1280, 24
TOTAL = 118.0
TA = '/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf'
F_SUB = ImageFont.truetype(TA, 31, layout_engine=ImageFont.Layout.RAQM)
F_LAB = ImageFont.truetype(TA, 24, layout_engine=ImageFont.Layout.RAQM)
F_CHIP = ImageFont.truetype(TA, 26, layout_engine=ImageFont.Layout.RAQM)
F_BIG = ImageFont.truetype(TA, 50, layout_engine=ImageFont.Layout.RAQM)
F_NOTE = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 54)

SCENES = [0, 9, 17, 36, 52, 66, 82, 103, 118]
VREF = {2: 'திருப்பாடல்கள் 105:1', 3: 'திருப்பாடல்கள் 105:2', 4: 'திருப்பாடல்கள் 105:3',
        5: 'திருப்பாடல்கள் 105:4', 6: 'திருப்பாடல்கள் 105:5'}

J, HL = 'இயேசு', 'ஹாலன்'
JV = J + ' (வசனம்)'
# (start, end, speaker, label, text)
SUBS = [
    (3.0, 8.6, HL, HL, 'இயேசப்பா… இந்த வசனம் எனக்குப் புரியலையே.'),
    (13.4, 16.8, J, J, 'வா ஹாலன். நாம ரெண்டு பேரும் சேர்ந்து படிப்போம்.'),
    (17.4, 22.2, J, JV, 'ஆண்டவருக்கு நன்றி செலுத்துங்கள்! அவர்தம் பெயரைச் சொல்லி வழிபடுங்கள்!'),
    (22.2, 27.0, J, JV, 'அவர்தம் செயல்களை மக்களினங்கள் அறியச் செய்யுங்கள்.'),
    (27.0, 32.4, J, J, 'அதாவது, கடவுளுக்கு நன்றி சொல்லு. அவர் செய்த நல்லதை எல்லாருக்கும் சொல்லு.'),
    (32.4, 35.6, HL, HL, 'நன்றி இயேசப்பா!'),
    (36.4, 41.2, J, JV, 'அவருக்குப் பாடல் பாடுங்கள்; அவரைப் புகழ்ந்தேத்துங்கள்!'),
    (41.2, 46.0, J, JV, 'அவர்தம் வியத்தகு செயல்கள் அனைத்தையும் எடுத்துரையுங்கள்!'),
    (46.0, 51.6, J, J, 'கடவுளுக்குப் பாட்டு பாடு. அவர் செய்த அதிசயங்களைச் சொல்லு.'),
    (52.4, 56.8, J, JV, 'அவர்தம் திருப்பெயரை மாட்சிப்படுத்துங்கள்;'),
    (56.8, 61.2, J, JV, 'ஆண்டவரைத் தேடுவோரின் இதயம் அக்களிப்பதாக!'),
    (61.2, 65.6, J, J, 'கடவுளைத் தேடுறவங்க மனசு எப்பவும் சந்தோஷமா இருக்கும்.'),
    (66.4, 71.0, J, JV, 'ஆண்டவரையும் அவரது ஆற்றலையும் தேடுங்கள்!'),
    (71.0, 75.6, J, JV, 'அவரது திருமுகத்தை இடையறாது நாடுங்கள்!'),
    (75.6, 81.6, J, J, 'கஷ்டமா இருக்கா? கடவுளிடம் பலம் கேள். எப்போதும் அவரிடம் போ.'),
    (82.4, 87.6, J, JV, 'அவர் செய்த வியத்தகு செயல்களை நினைவு கூருங்கள்!'),
    (87.6, 93.0, J, JV, 'அவர்தம் அருஞ்செயல்களையும், அவரது வாய் மொழிந்த நீதித் தீர்ப்புகளையும் நினைவில் கொள்ளுங்கள்.'),
    (93.0, 97.4, J, J, 'இன்னைக்கு கடவுள் உனக்கு என்ன நல்லது செய்தார்? அதை மறக்காதே.'),
    (97.4, 102.6, HL, HL, 'லஞ்ச் கொடுத்தார், ஃப்ரெண்ட் கொடுத்தார், பாட்டியோட அன்பு கொடுத்தார்!'),
    (104.5, 109.8, HL, HL, 'அம்மா! இன்னைக்கு கடவுள் எனக்கு என்ன நல்லது செய்தார் தெரியுமா?'),
]


def speaking(t, who):
    for s, e, sp, _, _ in SUBS:
        if sp == who and s <= t < e:
            return True
    return False


def wrap(text, font, width):
    words, lines, cur = text.split(' '), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if font.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


_subcache = {}


def sub_img(i):
    if i in _subcache:
        return _subcache[i]
    s, e, sp, label, text = SUBS[i]
    lines = wrap(text, F_SUB, 600)
    lh = 46
    h = 40 + 34 + lh * len(lines) + 10
    im = Image.new('RGBA', (660, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 659, h - 1], 26, fill=(20, 16, 24, 190))
    col = (255, 210, 120, 255) if sp == J else (150, 236, 205, 255)
    d.text((30, 18), label, font=F_LAB, fill=col)
    for k, ln in enumerate(lines):
        d.text((30, 58 + k * lh), ln, font=F_SUB, fill=(255, 255, 255, 255))
    _subcache[i] = im
    return im


_chipcache = {}


def chip(text):
    if text in _chipcache:
        return _chipcache[text]
    w = int(F_CHIP.getlength(text)) + 50
    im = Image.new('RGBA', (w, 56), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, 55], 28, fill=(255, 250, 235, 230))
    d.text((25, 9), text, font=F_CHIP, fill=(130, 60, 30, 255))
    _chipcache[text] = im
    return im


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def blink(t, seed=0):
    p = (t + seed * 1.3) % 3.7
    return p < 0.12


def mouth_for(t, who, default='smile'):
    if speaking(t, who):
        return 'open' if int(t * 8) % 2 == 0 else default
    return default


BG = house_bg()
BG_SEPIA = sepia(BG)
GLOW = glow(230)
SMALLGLOW = glow(60, (255, 220, 120), 230)
ICONS = {k: person_icon(k, 130) for k in ('mom', 'dad', 'grandma')}
ICONS7 = {k: person_icon(k, 140) for k in ('lunch', 'friend', 'love')}

HX, HY = 282, 978     # Hallen seat (feet)
JX, JY = 475, 990     # Jesus seat (feet)


def put(frame, sprite, x, y, scale=1.0, alpha=1.0):
    im, feet, cx = sprite
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
        feet, cx = feet * scale, cx * scale
    if alpha < 1.0:
        a = im.getchannel('A').point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    frame.alpha_composite(im, (int(x - cx), int(y - feet)))


def put_c(frame, im, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        im = im.copy()
        im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    frame.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def jesus_with_glow(f, sprite, x, y, pulse=0.0):
    put_c(f, GLOW, x, y - 260, alpha=0.75 + 0.25 * pulse)
    put(f, sprite, x, y)


def flowers(f, t):
    d = ImageDraw.Draw(f)
    for i, (x, y) in enumerate(((40, 1080), (110, 1120), (600, 1090), (670, 1130), (520, 1150), (190, 1160))):
        sw = math.sin(t * 1.6 + i) * 6
        d.line([(x, y + 60), (x + sw, y)], fill=(50, 110, 50), width=5)
        for a in range(5):
            ang = a * 72 + t * 10
            px = x + sw + math.cos(math.radians(ang)) * 14
            py = y + math.sin(math.radians(ang)) * 14
            d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=(220, 50, 60) if i % 2 == 0 else (255, 190, 60))
        d.ellipse([x + sw - 7, y - 7, x + sw + 7, y + 7], fill=(255, 230, 120))


def birds(f, t, land):
    d = ImageDraw.Draw(f)
    targets = [(80, 330), (130, 350), (640, 330)]
    for i, (tx, ty) in enumerate(targets):
        p = ease((t - land - i * 0.6) / 2.5)
        sx, sy = (-60 if tx < 360 else 780), 150 + i * 30
        x, y = sx + (tx - sx) * p, sy + (ty - sy) * p - math.sin(p * math.pi) * 60
        flap = math.sin(t * 14 + i) * 10 * (1 - p)
        d.line([(x - 18, y - flap), (x, y + 6), (x + 18, y - flap)], fill=(50, 40, 50), width=5)
        if p >= 1:
            d.ellipse([x - 12, y - 4, x + 12, y + 12], fill=(70, 60, 80))


def notes(f, t, t0):
    d = ImageDraw.Draw(f)
    for i in range(6):
        p = ((t - t0) * 0.35 + i / 6) % 1.0
        x = 230 + math.sin(p * 6 + i) * 80 + (i % 3) * 40
        y = 640 - p * 420
        a = int(255 * math.sin(p * math.pi))
        d.text((x, y), '♪' if i % 2 else '♫', font=F_NOTE, fill=(150, 60, 120, a))


def camera(frame, z, cx, cy):
    if z <= 1.001:
        return frame
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return frame.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))


def scene_of(t):
    for i in range(8):
        if SCENES[i] <= t < SCENES[i + 1]:
            return i, t - SCENES[i]
    return 7, t - SCENES[7]


def draw(t):
    sc, lt = scene_of(t)
    f = (BG_SEPIA if (sc == 5 and lt < 6.0) else BG).convert('RGBA')
    z, cx, cy = 1.0, 360, 640
    hb = blink(t)
    jb = blink(t, 1)
    he = 'closed' if hb else 'open'
    je = 'closed' if jb else 'open'

    if sc == 0:
        arms = 'scratch' if (lt % 3.0) > 1.5 else 'hold'
        put(f, hallen(arms, 'sit', he, mouth_for(t, HL, 'flat'), 'confused'), HX, HY)
        z = 1.25 - 0.1 * ease(lt / 9)
        cx, cy = 300, 820
    elif sc == 1:
        if lt < 4.2:
            x = 820 - (820 - JX) * ease(lt / 4.0)
            y = 990 - abs(math.sin(lt * 4)) * 6
            jesus_with_glow(f, jesus('open', 'stand', je, 'smile'), x, y + 70 * 0 + 0)
        else:
            jesus_with_glow(f, jesus('rest', 'sit', je, mouth_for(t, J)), JX, JY)
        m = 'o' if 1.5 < lt < 4.5 else 'smile'
        put(f, hallen('hold', 'sit', he, m, 'up' if lt > 1.5 else 'confused'), HX, HY)
    elif sc == 2:
        jesus_with_glow(f, jesus('point', 'sit', je, mouth_for(t, J)), JX, JY, math.sin(t * 2))
        mood = 'smile'
        put(f, hallen('hold', 'sit', he, mouth_for(t, HL, mood)), HX, HY)
        for i, k in enumerate(('mom', 'dad', 'grandma')):
            p = (lt - 9.5 - i * 1.2) / 6.0
            if 0 < p < 1.6:
                p2 = min(p, 1.0)
                x = 290 + (i - 1) * 150
                y = 640 - ease(p2) * 330
                a = min(1.0, p * 4) * (1.0 if p < 1.3 else max(0.0, (1.6 - p) / 0.3))
                put_c(f, ICONS[k], x, y, a)
    elif sc == 3:
        jesus_with_glow(f, jesus('clap1' if int(t * 4) % 2 else 'clap2', 'sit', je, mouth_for(t, J)), JX, JY)
        rise = ease(lt / 0.8)
        hop = abs(math.sin(lt * 3.2)) * 10
        put(f, hallen('sing', 'stand', 'happy', 'open' if int(t * 5) % 2 else 'big'), 215, 1010 - hop)
        notes(f, t, SCENES[3])
        birds(f, t, SCENES[3] + 0.5)
    elif sc == 4:
        jesus_with_glow(f, jesus('touch', 'sit', je, mouth_for(t, J)), JX, JY)
        put(f, hallen('hold', 'sit', 'happy' if lt > 3 else he, 'big' if lt > 3 else 'smile'), HX, HY)
        pul = 0.6 + 0.4 * math.sin(t * 4)
        put_c(f, SMALLGLOW, HX - 2, HY - 150, alpha=min(1.0, lt / 2) * pul, scale=1.4)
        d = ImageDraw.Draw(f)
        heart(d, HX - 2, HY - 152, 18 * (0.9 + 0.15 * math.sin(t * 4)), (255, 120, 120, int(230 * min(1, lt / 2))))
        z = 1.0 + 0.7 * ease(lt / 3)
        cx, cy = HX + 60, HY - 220
    elif sc == 5:
        if lt < 6.0:
            # flashback: struggling with the school bag
            wob = math.sin(lt * 9) * 6
            put(f, hallen('bag', 'stand', 'closed' if int(lt * 2) % 2 else 'open', 'flat', 'confused'), 360 + wob, 1020)
            put_c(f, chip('நேற்று… பள்ளிக்குப் போகும் வழியில்'), 360, 470)
        else:
            jesus_with_glow(f, jesus('rest', 'sit', je, mouth_for(t, J)), JX, JY, math.sin(t * 2))
            put(f, hallen('pray', 'sit', 'closed', 'smile'), HX, HY)
            z = 1.2
            cx, cy = 380, 780
    elif sc == 6:
        jesus_with_glow(f, jesus('rest', 'sit', je, mouth_for(t, J)), JX, JY)
        put(f, hallen('count', 'sit', he, mouth_for(t, HL, 'smile'), 'up'), HX, HY)
        for i, k in enumerate(('lunch', 'friend', 'love')):
            t0 = 1.5 + i * 1.6
            if lt > t0:
                p = ease((lt - t0) / 0.5)
                bump = 1.0
                for s, e in ((15.6 + i * 1.6, 16.6 + i * 1.6),):
                    if s < lt < e:
                        bump = 1.0 + 0.18 * math.sin((lt - s) / (e - s) * math.pi)
                put_c(f, ICONS7[k], 150 + i * 210, 470, p, scale=max(0.05, p) * bump)
    elif sc == 7:
        if lt < 2.0:
            jesus_with_glow(f, jesus('bless', 'sit', je, 'smile'), JX, JY, 1)
            put(f, hallen('hold', 'sit', 'happy', 'smile'), HX, HY)
        else:
            jesus_with_glow(f, jesus('rest', 'sit', je, 'smile'), JX, JY)
            # mom appears in the doorway
            ma = ease((lt - 2.2) / 0.8)
            hug = lt > 4.6
            if ma > 0:
                put(f, mom('hug' if hug else 'down', 'closed' if hug else 'open'), 382 if hug else 362, 846, 0.8, ma)
            p = ease((lt - 2.0) / 2.6)
            x = HX + (352 - HX) * p
            y = HY + (862 - HY) * p
            sc_ = 1.0 - 0.18 * p
            if hug:
                put(f, hallen('down', 'stand', 'happy', mouth_for(t, HL, 'big')), 338, 866, 0.82)
            else:
                ph = 'run1' if int(lt * 6) % 2 else 'run2'
                put(f, hallen(ph, ph, 'open', 'big'), x, y, sc_)
        zz = 1.0 + 0.35 * (1 - ease((lt - 5.0) / 4.0))
        z, cx, cy = zz, 380, 780
    # verse chip
    fr = camera(f, z, cx, cy)
    if sc in VREF:
        put_c(fr, chip(VREF[sc]), 360, 110)
    # subtitles
    for i, (s, e, sp, lab, txt) in enumerate(SUBS):
        if s <= t < e:
            a = min(1.0, (t - s) / 0.25, (e - t) / 0.25)
            im = sub_img(i)
            put_c(fr, im, 360, 1150 - im.height / 2 + 20 * 0, a)
    # end card
    if sc == 7 and lt > 8.5:
        a = ease((lt - 8.5) / 0.8)
        ov = Image.new('RGBA', (W, H), (30, 18, 12, int(150 * a)))
        fr.alpha_composite(ov)
        d = ImageDraw.Draw(fr)
        col = (255, 236, 190, int(255 * a))
        tx = 'திருப்பாடல்கள் 105:1-5'
        d.text((360 - F_BIG.getlength(tx) / 2, 420), tx, font=F_BIG, fill=col)
        q = wrap('இன்று கடவுள் உங்களுக்கு செய்த நல்லது என்ன? கமெண்டில் சொல்லுங்கள்.', F_SUB, 560)
        for k, ln in enumerate(q):
            d.text((360 - F_SUB.getlength(ln) / 2, 540 + k * 50), ln, font=F_SUB, fill=(255, 255, 255, int(255 * a)))
        cr = 'வசனம்: திருவிவிலியம்'
        d.text((360 - F_LAB.getlength(cr) / 2, 1180), cr, font=F_LAB, fill=(255, 220, 170, int(220 * a)))
    # opening title
    if t < 2.9:
        a = min(1.0, t / 0.6, (2.9 - t) / 0.5)
        ov = Image.new('RGBA', (W, H), (40, 20, 10, int(120 * a)))
        fr.alpha_composite(ov)
        d = ImageDraw.Draw(fr)
        for txt, fnt, y, col in (('ஹாலனும் இயேசுவும்', F_BIG, 300, (255, 236, 190)),
                                 ('திருப்பாடல்கள் 105:1-5', F_SUB, 390, (255, 255, 255))):
            d.text((360 - fnt.getlength(txt) / 2, y), txt, font=fnt, fill=col + (int(255 * a),))
    # scene dip
    for b in SCENES[1:-1]:
        dd = abs(t - b)
        if dd < 0.25:
            ov = Image.new('RGBA', (W, H), (255, 240, 220, int(255 * (1 - dd / 0.25) * 0.85)))
            fr.alpha_composite(ov)
    if t < 0.5:
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - t / 0.5)))))
    if t > TOTAL - 0.8:
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (t - TOTAL + 0.8) / 0.8))))
    return fr.convert('RGB')


def music(path, dur=TOTAL, sr=44100):
    n = int(dur * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    cl = 4.0
    for ci in range(int(dur / cl) + 1):
        ch = chords[ci % 4]
        s0 = int(ci * cl * sr)
        s1 = min(n, int((ci + 1) * cl * sr + sr))
        tt = np.arange(s1 - s0) / sr
        env = np.minimum(1, tt / 1.2) * np.exp(-np.maximum(0, tt - cl) * 3)
        for m in ch:
            out[s0:s1] += 0.05 * env * (np.sin(2 * np.pi * hz(m - 12) * tt) + 0.3 * np.sin(2 * np.pi * hz(m) * tt))
        # soft bell arpeggio
        for k in range(4):
            b0 = s0 + int(k * sr)
            if b0 >= n:
                break
            m = ch[k % 3] + 12
            bt = np.arange(min(int(1.5 * sr), n - b0)) / sr
            out[b0:b0 + len(bt)] += 0.035 * np.exp(-bt * 3) * np.sin(2 * np.pi * hz(m) * bt)
    out *= np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
    out = np.int16(np.clip(out, -1, 1) * 32767 * 0.9)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(out.tobytes())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        for tt in map(float, sys.argv[2:]):
            draw(tt).save(f'still_{tt:05.1f}.png')
        sys.exit()
    out = sys.argv[1] if len(sys.argv) > 1 else 'hallen.mp4'
    music('music.wav')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', 'music.wav',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out],
                         stdin=subprocess.PIPE)
    N = int(TOTAL * FPS)
    for i in range(N):
        p.stdin.write(draw(i / FPS).tobytes())
        if i % 240 == 0:
            print('frame', i, '/', N, flush=True)
    p.stdin.close()
    p.wait()
    print('done', out)
