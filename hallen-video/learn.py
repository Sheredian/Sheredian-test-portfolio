"""Kids learning version: short chunks, words light up one by one, read then repeat, verse cards, recap."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
from art import hallen, jesus, mom, heart
from render import (put, put_c, camera, notes, birds, ease, blink, chip, wrap, music, jesus_with_glow,
                    BG, BG_SEPIA, SMALLGLOW, ICONS, ICONS7, HX, HY, JX, JY, W, H, FPS, TA)

F_K = ImageFont.truetype(TA, 44, layout_engine=ImageFont.Layout.RAQM)
F_S = ImageFont.truetype(TA, 38, layout_engine=ImageFont.Layout.RAQM)
F_L = ImageFont.truetype(TA, 26, layout_engine=ImageFont.Layout.RAQM)
F_CARD = ImageFont.truetype(TA, 64, layout_engine=ImageFont.Layout.RAQM)
F_NUM = ImageFont.truetype(TA, 110, layout_engine=ImageFont.Layout.RAQM)
F_T = ImageFont.truetype(TA, 50, layout_engine=ImageFont.Layout.RAQM)
F_R = ImageFont.truetype(TA, 28, layout_engine=ImageFont.Layout.RAQM)

J, HL = 'இயேசு', 'ஹாலன்'
PER_WORD = 0.9
READ_LAB = 'இயேசு வாசிக்கிறார்'
REP_LAB = 'ஹாலனோடு சேர்ந்து நீயும் சொல்லு!'

VERSES = [
    (2, 'நன்றி சொல்லு', ['ஆண்டவருக்கு நன்றி செலுத்துங்கள்!', 'அவர்தம் பெயரைச் சொல்லி வழிபடுங்கள்!',
                        'அவர்தம் செயல்களை மக்களினங்கள் அறியச் செய்யுங்கள்.'],
     'அதாவது, கடவுளுக்கு நன்றி சொல்லு. அவர் செய்த நல்லதை எல்லாருக்கும் சொல்லு.', 'நன்றி இயேசப்பா!'),
    (3, 'பாட்டு பாடு', ['அவருக்குப் பாடல் பாடுங்கள்;', 'அவரைப் புகழ்ந்தேத்துங்கள்!',
                       'அவர்தம் வியத்தகு செயல்கள் அனைத்தையும் எடுத்துரையுங்கள்!'],
     'கடவுளுக்குப் பாட்டு பாடு. அவர் செய்த அதிசயங்களைச் சொல்லு.', None),
    (4, 'சந்தோஷமா இரு', ['அவர்தம் திருப்பெயரை மாட்சிப்படுத்துங்கள்;', 'ஆண்டவரைத் தேடுவோரின் இதயம் அக்களிப்பதாக!'],
     'கடவுளைத் தேடுறவங்க மனசு எப்பவும் சந்தோஷமா இருக்கும்.', None),
    (5, 'பலம் கேள்', ['ஆண்டவரையும் அவரது ஆற்றலையும் தேடுங்கள்!', 'அவரது திருமுகத்தை இடையறாது நாடுங்கள்!'],
     'கஷ்டமா இருக்கா? கடவுளிடம் பலம் கேள். எப்போதும் அவரிடம் போ.', None),
    (6, 'மறக்காதே', ['அவர் செய்த வியத்தகு செயல்களை நினைவு கூருங்கள்!', 'அவர்தம் அருஞ்செயல்களையும்,',
                    'அவரது வாய் மொழிந்த நீதித் தீர்ப்புகளையும் நினைவில் கொள்ளுங்கள்.'],
     'இன்னைக்கு கடவுள் உனக்கு என்ன நல்லது செய்தார்? அதை மறக்காதே.',
     'லஞ்ச் கொடுத்தார், ஃப்ரெண்ட் கொடுத்தார், பாட்டியோட அன்பு கொடுத்தார்!'),
]
RECAP = ['கடவுளுக்கு நன்றி சொல்லு', 'கடவுளுக்குப் பாட்டு பாடு', 'கடவுளைத் தேடு, சந்தோஷமா இரு',
         'கடவுளிடம் பலம் கேள்', 'அவர் செய்த நல்லதை மறக்காதே']

# ------------------------------------------------------------------ timeline
TL, EV, SC_START = [], {}, {}
_t = 0.0


def add(scene, dur, kind=None, who=None, label=None, text=None, **kw):
    global _t
    SC_START.setdefault(scene, _t)
    seg = dict(scene=scene, start=_t, end=_t + dur, kind=kind, who=who, label=label, text=text, **kw)
    TL.append(seg)
    _t += dur
    return seg


def say_dur(text):
    return max(3.5, 0.6 * len(text.split()) + 2.4)


def kar_dur(text):
    return PER_WORD * len(text.split()) + 1.6


add(0, 3.2, 'title')
add(0, say_dur('x x x x x'), 'say', HL, HL, 'இயேசப்பா… இந்த வசனம் எனக்குப் புரியலையே.')
add(0, 0.6)
add(1, 4.6)
add(1, say_dur('x x x x x x'), 'say', J, J, 'வா ஹாலன். நாம ரெண்டு பேரும் சேர்ந்து படிப்போம்.')
add(1, 0.6)
for n, (sc, idea, chunks, simple, reply) in enumerate(VERSES, 1):
    if sc == 5:
        EV['flash'] = (_t, _t + 5.0)
        add(sc, 5.0, 'flash')
    add(sc, 3.4, 'card', num=n, idea=idea)
    for c in chunks:
        add(sc, kar_dur(c), 'read', J, READ_LAB, c)
        add(sc, kar_dur(c), 'repeat', HL, REP_LAB, c)
    seg = add(sc, say_dur(simple), 'say', J, J, simple)
    EV[f'simple{sc}'] = seg['start']
    if reply:
        seg = add(sc, say_dur(reply) + (1.5 if sc == 6 else 0), 'say', HL, HL, reply)
        EV[f'reply{sc}'] = (seg['start'], seg['end'])
    add(sc, 0.8)
add(7, 2.0)
add(7, say_dur('x x x x x x x x'), 'say', HL, HL, 'அம்மா! இன்னைக்கு கடவுள் எனக்கு என்ன நல்லது செய்தார் தெரியுமா?')
add(7, 1.2)
EV['recap'] = _t
add(7, 3.0 + 3.0 * len(RECAP), 'recap')
EV['end'] = _t
add(7, 8.0, 'end')
TOTAL = _t
SC_ORDER = sorted(SC_START.items(), key=lambda kv: kv[1])
VNUM = {sc: i for i, (sc, *_r) in enumerate(VERSES, 1)}


def seg_at(t):
    for s in TL:
        if s['start'] <= t < s['end']:
            return s
    return TL[-1]


def scene_of(t):
    cur = SC_ORDER[0]
    for sc, st in SC_ORDER:
        if t >= st:
            cur = (sc, st)
    return cur[0], t - cur[1]


def speaking(t, who):
    s = seg_at(t)
    return s['who'] == who and s['kind'] in ('say', 'read', 'repeat') and t < s['end'] - 0.5


def mouth_for(t, who, default='smile'):
    if speaking(t, who):
        return 'open' if int(t * 7) % 2 == 0 else default
    return default


# ------------------------------------------------------------------ text boxes
def layout(words, font, width):
    sp = font.getlength(' ')
    lines, cur, cw = [], [], 0
    for w in words:
        wl = font.getlength(w)
        if cur and cw + sp + wl > width:
            lines.append(cur)
            cur, cw = [], 0
        cur.append((w, wl))
        cw += (sp if cw else 0) + wl
    if cur:
        lines.append(cur)
    return lines, sp


def text_box(fr, seg, t):
    kind = seg['kind']
    words = seg['text'].split()
    font = F_K if kind in ('read', 'repeat') else F_S
    lh = 62 if font is F_K else 54
    lines, sp = layout(words, font, 610)
    h = 70 + lh * len(lines) + 16
    box = Image.new('RGBA', (680, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    if kind == 'repeat':
        bg, labc, lit = (14, 60, 50, 215), (160, 245, 210, 255), (150, 240, 200, 255)
    elif kind == 'read':
        bg, labc, lit = (40, 22, 12, 215), (255, 210, 120, 255), (255, 214, 90, 255)
    else:
        bg, labc, lit = (20, 16, 24, 200), ((255, 210, 120, 255) if seg['who'] == J else (150, 236, 205, 255)), None
    d.rounded_rectangle([0, 0, 679, h - 1], 30, fill=bg)
    d.text((32, 16), seg['label'], font=F_L, fill=labc)
    lt = t - seg['start'] - 0.5
    nlit = len(words) if lit is None else max(0, min(len(words), int(lt / PER_WORD) + 1)) if lt >= 0 else 0
    k = 0
    for li, ln in enumerate(lines):
        tw = sum(wl for _, wl in ln) + sp * (len(ln) - 1)
        x = (680 - tw) / 2
        y = 64 + li * lh
        for w, wl in ln:
            if lit is None:
                col = (255, 255, 255, 255)
            elif k < nlit:
                col = lit
            else:
                col = (255, 255, 255, 150)
            d.text((x, y), w, font=font, fill=col)
            if lit is not None and k == nlit - 1:
                d.rounded_rectangle([x, y + lh - 8, x + wl, y + lh - 3], 3, fill=lit)
            x += wl + sp
            k += 1
    a = min(1.0, (t - seg['start']) / 0.25, (seg['end'] - t) / 0.25)
    put_c(fr, box, 360, 1160 - h / 2, max(0.0, a))


def verse_card(fr, seg, t):
    lt, dur = t - seg['start'], seg['end'] - seg['start']
    a = min(1.0, lt / 0.4, (dur - lt) / 0.4)
    fr.alpha_composite(Image.new('RGBA', (W, H), (40, 20, 10, int(140 * a))))
    d = ImageDraw.Draw(fr)
    pop = 0.7 + 0.3 * ease(lt / 0.5)
    r = 110 * pop
    d.ellipse([360 - r, 560 - r, 360 + r, 560 + r], fill=(255, 214, 90, int(255 * a)))
    num = str(seg['num'])
    d.text((360 - F_NUM.getlength(num) / 2, 560 - 78), num, font=F_NUM, fill=(110, 50, 20, int(255 * a)))
    for txt, fnt, y, col in ((f'வசனம் {num}', F_S, 370, (255, 255, 255)),
                             (seg['idea'], F_CARD, 700, (255, 236, 190))):
        d.text((360 - fnt.getlength(txt) / 2, y), txt, font=fnt, fill=col + (int(255 * a),))


def recap(fr, t):
    lt = t - EV['recap']
    a = ease(lt / 0.8)
    fr.alpha_composite(Image.new('RGBA', (W, H), (30, 18, 12, int(175 * a))))
    d = ImageDraw.Draw(fr)
    ttl = 'இன்று நாம் கற்றது'
    d.text((360 - F_T.getlength(ttl) / 2, 240), ttl, font=F_T, fill=(255, 236, 190, int(255 * a)))
    for i, line in enumerate(RECAP):
        p = ease((lt - 2.0 - i * 3.0) / 0.6)
        if p <= 0:
            continue
        y = 400 + i * 130
        x = 46 + (1 - p) * 40
        d.ellipse([x, y, x + 76, y + 76], fill=(255, 214, 90, int(255 * p)))
        d.text((x + 38 - F_S.getlength(str(i + 1)) / 2, y + 8), str(i + 1), font=F_S, fill=(110, 50, 20, int(255 * p)))
        now = (lt - 2.0 - i * 3.0) < 3.0
        d.text((x + 100, y + 14), line, font=F_R, fill=((255, 214, 90) if now else (255, 255, 255)) + (int(255 * p),))


def end_card(fr, t):
    lt = t - EV['end']
    a = ease(lt / 0.8)
    fr.alpha_composite(Image.new('RGBA', (W, H), (30, 18, 12, int(190 * a))))
    d = ImageDraw.Draw(fr)
    col = (255, 236, 190, int(255 * a))
    tx = 'திருப்பாடல்கள் 105:1-5'
    d.text((360 - F_CARD.getlength(tx) / 2, 400), tx, font=F_CARD, fill=col)
    for k, ln in enumerate(wrap('இன்று கடவுள் உங்களுக்கு செய்த நல்லது என்ன? கமெண்டில் சொல்லுங்கள்.', F_S, 580)):
        d.text((360 - F_S.getlength(ln) / 2, 540 + k * 58), ln, font=F_S, fill=(255, 255, 255, int(255 * a)))
    cr = 'வசனம்: திருவிவிலியம்'
    d.text((360 - F_L.getlength(cr) / 2, 1180), cr, font=F_L, fill=(255, 220, 170, int(220 * a)))


# ------------------------------------------------------------------ frame
def draw(t):
    sc, lt = scene_of(t)
    seg = seg_at(t)
    flash = 'flash' in EV and EV['flash'][0] <= t < EV['flash'][1]
    f = (BG_SEPIA if flash else BG).convert('RGBA')
    z, cx, cy = 1.0, 360, 640
    he = 'closed' if blink(t) else 'open'
    je = 'closed' if blink(t, 1) else 'open'

    if sc == 0:
        arms = 'scratch' if (lt % 3.0) > 1.5 else 'hold'
        put(f, hallen(arms, 'sit', he, mouth_for(t, HL, 'flat'), 'confused'), HX, HY)
        z, cx, cy = 1.25 - 0.1 * ease(lt / 9), 300, 820
    elif sc == 1:
        if lt < 4.2:
            x = 820 - (820 - JX) * ease(lt / 4.0)
            jesus_with_glow(f, jesus('open', 'stand', je, 'smile'), x, 990 - abs(math.sin(lt * 4)) * 6)
        else:
            jesus_with_glow(f, jesus('rest', 'sit', je, mouth_for(t, J)), JX, JY)
        put(f, hallen('hold', 'sit', he, mouth_for(t, HL, 'o' if 1.5 < lt < 4.5 else 'smile'),
                      'up' if lt > 1.5 else 'confused'), HX, HY)
    elif sc == 2:
        jesus_with_glow(f, jesus('point' if speaking(t, J) else 'rest', 'sit', je, mouth_for(t, J)), JX, JY, math.sin(t * 2))
        put(f, hallen('hold', 'sit', he, mouth_for(t, HL)), HX, HY)
        for i, k in enumerate(('mom', 'dad', 'grandma')):
            p = (t - EV['simple2'] - 0.5 - i * 1.2) / 6.0
            if 0 < p < 1.6:
                y = 640 - ease(min(p, 1.0)) * 330
                a = min(1.0, p * 4) * (1.0 if p < 1.3 else max(0.0, (1.6 - p) / 0.3))
                put_c(f, ICONS[k], 290 + (i - 1) * 150, y, a)
    elif sc == 3:
        jesus_with_glow(f, jesus('clap1' if int(t * 3) % 2 else 'clap2', 'sit', je, mouth_for(t, J)), JX, JY)
        hop = abs(math.sin(lt * 2.6)) * 10
        m = mouth_for(t, HL, 'big') if speaking(t, HL) else ('big' if int(t * 3) % 2 else 'smile')
        put(f, hallen('sing', 'stand', 'happy', m), 215, 1010 - hop)
        notes(f, t, SC_START[3])
        birds(f, t, SC_START[3] + 0.5)
    elif sc == 4:
        jesus_with_glow(f, jesus('touch', 'sit', je, mouth_for(t, J)), JX, JY)
        happy = lt > 4
        put(f, hallen('hold', 'sit', 'happy' if happy else he, mouth_for(t, HL, 'big' if happy else 'smile')), HX, HY)
        pul = 0.6 + 0.4 * math.sin(t * 3)
        put_c(f, SMALLGLOW, HX - 2, HY - 150, alpha=min(1.0, lt / 2) * pul, scale=1.4)
        d = ImageDraw.Draw(f)
        heart(d, HX - 2, HY - 152, 18 * (0.9 + 0.15 * math.sin(t * 3)), (255, 120, 120, int(230 * min(1, lt / 2))))
        z, cx, cy = 1.0 + 0.6 * ease(lt / 3), HX + 70, HY - 230
    elif sc == 5:
        if flash:
            wob = math.sin(lt * 9) * 6
            put(f, hallen('bag', 'stand', 'closed' if int(lt * 2) % 2 else 'open', 'flat', 'confused'), 360 + wob, 1020)
            put_c(f, chip('நேற்று… பள்ளிக்குப் போகும் வழியில்'), 360, 470)
        else:
            jesus_with_glow(f, jesus('rest', 'sit', je, mouth_for(t, J)), JX, JY, math.sin(t * 2))
            put(f, hallen('pray', 'sit', 'closed', mouth_for(t, HL)), HX, HY)
            z, cx, cy = 1.15, 380, 800
    elif sc == 6:
        jesus_with_glow(f, jesus('rest', 'sit', je, mouth_for(t, J)), JX, JY)
        put(f, hallen('count', 'sit', he, mouth_for(t, HL), 'up'), HX, HY)
        rs, re_ = EV['reply6']
        step = (re_ - rs - 1.5) / 3
        for i, k in enumerate(('lunch', 'friend', 'love')):
            t0 = SC_START[6] + 4.0 + i * 1.6
            if t > t0:
                p = ease((t - t0) / 0.5)
                bump = 1.0
                s0 = rs + i * step
                if s0 < t < s0 + step:
                    bump = 1.0 + 0.22 * math.sin((t - s0) / step * math.pi)
                put_c(f, ICONS7[k], 150 + i * 210, 470, p, scale=max(0.05, p) * bump)
    elif sc == 7:
        if lt < 2.0:
            jesus_with_glow(f, jesus('bless', 'sit', je, 'smile'), JX, JY, 1)
            put(f, hallen('hold', 'sit', 'happy', 'smile'), HX, HY)
        else:
            jesus_with_glow(f, jesus('rest', 'sit', je, 'smile'), JX, JY)
            ma = ease((lt - 2.2) / 0.8)
            hug = lt > 4.6
            if ma > 0:
                put(f, mom('hug' if hug else 'down', 'closed' if hug else 'open'), 382 if hug else 362, 846, 0.8, ma)
            p = ease((lt - 2.0) / 2.6)
            if hug:
                put(f, hallen('down', 'stand', 'happy', mouth_for(t, HL, 'big')), 338, 866, 0.82)
            else:
                ph = 'run1' if int(lt * 6) % 2 else 'run2'
                put(f, hallen(ph, ph, 'open', 'big'), HX + (352 - HX) * p, HY + (862 - HY) * p, 1.0 - 0.18 * p)
        z, cx, cy = 1.0 + 0.35 * (1 - ease((lt - 6.0) / 4.0)), 380, 780

    fr = camera(f, z, cx, cy)
    if sc in VNUM and not flash:
        put_c(fr, chip(f'திருப்பாடல்கள் 105:{VNUM[sc]}'), 360, 110)
    k = seg['kind']
    if k in ('say', 'read', 'repeat'):
        text_box(fr, seg, t)
    elif k == 'card':
        verse_card(fr, seg, t)
    if k == 'title':
        a = min(1.0, t / 0.6, (seg['end'] - t) / 0.5)
        fr.alpha_composite(Image.new('RGBA', (W, H), (40, 20, 10, int(120 * a))))
        d = ImageDraw.Draw(fr)
        for txt, fnt, y, col in (('ஹாலனும் இயேசுவும்', F_CARD, 290, (255, 236, 190)),
                                 ('திருப்பாடல்கள் 105:1-5', F_S, 395, (255, 255, 255))):
            d.text((360 - fnt.getlength(txt) / 2, y), txt, font=fnt, fill=col + (int(255 * a),))
    if t >= EV['recap'] and t < EV['end'] + 0.8:
        recap(fr, t)
    if t >= EV['end']:
        end_card(fr, t)
    for sc_, st in SC_ORDER[1:]:
        dd = abs(t - st)
        if dd < 0.25:
            fr.alpha_composite(Image.new('RGBA', (W, H), (255, 240, 220, int(255 * (1 - dd / 0.25) * 0.85))))
    if t < 0.5:
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - t / 0.5)))))
    if t > TOTAL - 0.8:
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * min(1, (t - TOTAL + 0.8) / 0.8)))))
    return fr.convert('RGB')


if __name__ == '__main__':
    print(f'TOTAL {TOTAL:.1f}s', {sc: round(st, 1) for sc, st in SC_ORDER})
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        for tt in map(float, sys.argv[2:]):
            draw(tt).save(f'still_{tt:06.1f}.png')
        sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == 'info':
        for s in TL:
            print(round(s['start'], 1), s['scene'], s['kind'], (s['text'] or '')[:30])
        sys.exit()
    out = sys.argv[1]
    music('music.wav', dur=TOTAL)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', 'music.wav',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out],
                         stdin=subprocess.PIPE)
    N = int(TOTAL * FPS)
    for i in range(N):
        p.stdin.write(draw(i / FPS).tobytes())
        if i % 1200 == 0:
            print('frame', i, '/', N, flush=True)
    p.stdin.close()
    p.wait()
    print('done', out)
