"""Builds the 9:16 reel version of the Game2Grow x SNS MoU video.

Music is an original instrumental made with numpy, in the style of Tamil
motivational film BGM: thavil and parai style drums in a 3-3-2 groove,
a Keeravani (harmonic minor) lead with gamaka-like slides, and strings.
No copyrighted track is used.

Writes two files:
  <out>.mp4           reel with the music
  <out>-no-music.mp4  same reel, silent, for adding trending audio in Instagram

Usage: python3 make_reel.py <photo1> <photo2> <collage> <out-basename>
"""
import os
import subprocess
import sys
import wave

os.environ["REEL"] = "1"
import numpy as np  # noqa: E402

import make_video as mv  # noqa: E402

SR = 44100
BPM = 100
BEAT = 60 / BPM
S16 = BEAT / 4
BAR = BEAT * 4


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def place(out, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(out):
        return
    j = min(len(out), i + len(sig))
    out[i:j] += gain * sig[: j - i]


def env_exp(n, decay):
    t = np.arange(n) / SR
    return np.exp(-t / decay)


RNG = np.random.default_rng(3)


def lowpass(x, a):
    """One-pole low-pass. a in (0,1): smaller = darker."""
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


# --- drums -------------------------------------------------------------

def thavil_low(n=int(0.35 * SR)):
    t = np.arange(n) / SR
    f = 55 + 95 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env_exp(n, 0.12) + 0.3 * np.sin(2 * ph) * env_exp(n, 0.05)


def thavil_high(n=int(0.12 * SR)):
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 420 * t) * env_exp(n, 0.03)
    noise = RNG.standard_normal(n) * env_exp(n, 0.015)
    return 0.6 * tone + 0.5 * (noise - lowpass(noise, 0.25))


def clap(n=int(0.2 * SR)):
    noise = RNG.standard_normal(n)
    e = env_exp(n, 0.05)
    for off in (0.0, 0.011, 0.022):  # three quick slaps
        k = int(off * SR)
        e[k:k + 60] += 0.6
    bp = lowpass(noise, 0.5) - lowpass(noise, 0.08)
    return bp * e * 0.9


def impact(n=int(2.5 * SR)):
    t = np.arange(n) / SR
    f = 38 + 80 * np.exp(-t / 0.08)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.7)
    noise = RNG.standard_normal(n)
    crash = (noise - lowpass(noise, 0.3)) * env_exp(n, 0.5) * 0.25
    return boom + crash


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = RNG.standard_normal(n)
    sweep = noise - lowpass(noise, 0.15)
    return sweep * (t / dur) ** 2 * 0.3


# --- tonal -------------------------------------------------------------

def saw(f_curve, harmonics=8):
    ph = 2 * np.pi * np.cumsum(f_curve) / SR
    out = np.zeros_like(ph)
    for k in range(1, harmonics + 1):
        out += np.sin(k * ph) / k
    return out


def lead_note(m_from, m_to, dur):
    """Nadaswaram-ish lead: slides from m_from into m_to (gamaka), vibrato."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    slide = np.minimum(1, t / 0.07)
    m = m_from + (m_to - m_from) * (1 - (1 - slide) ** 2)
    vib = 0.18 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.25)
    f = midi(m + vib)
    tone = saw(f, 7)
    e = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.06) * (0.85 + 0.15 * np.exp(-t / 0.2))
    return tone * np.clip(e, 0, 1)


def pad(chord, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in chord:
        for det in (-0.08, 0.0, 0.08):
            out += saw(np.full(n, midi(m + det)), 4)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.5)
    return out * np.clip(e, 0, 1)


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env_exp(n, 0.25) * np.minimum(1, t / 0.005)


# D Keeravani (harmonic minor): D E F G A Bb C#
D4 = 62
CHORDS = [  # (bass root, pad chord)
    (38, [50, 53, 57, 62]),      # Dm
    (34, [46, 50, 53, 58]),      # Bb
    (36, [48, 52, 55, 60]),      # C
    (33, [45, 49, 52, 57]),      # A (major: the harmonic minor lift)
]
# hook: (start 16th, length in 16ths, midi), two bars long
HOOK = [
    (0, 3, 69), (3, 3, 70), (6, 2, 69), (8, 4, 67), (12, 2, 65), (14, 2, 67),
    (16, 3, 69), (19, 3, 65), (22, 2, 64), (24, 6, 62), (30, 2, 61),
]
HOOK_B = [
    (0, 3, 74), (3, 3, 73), (6, 2, 74), (8, 4, 76), (12, 2, 77), (14, 2, 76),
    (16, 3, 74), (19, 3, 70), (22, 2, 69), (24, 8, 69),
]


def make_music(path, dur, sections):
    """sections: dict of times (s) for groove start, lift, outro."""
    n = int(dur * SR)
    drums = np.zeros(n)
    tonal = np.zeros(n)
    lead = np.zeros(n)

    g0, lift, outro = sections["groove"], sections["lift"], sections["outro"]

    # opening hit right on frame 1 with the FIRST MoU text
    place(drums, impact(), 0.0, 0.9)

    lo, hi, cl = thavil_low(), thavil_high(), clap()
    nbars = int(np.ceil(dur / BAR)) + 1
    for b in range(nbars):
        t0 = b * BAR
        root, chord = CHORDS[b % 4]
        if t0 < dur:
            place(tonal, pad(chord, BAR + 0.4), t0, 0.022 if t0 < outro else 0.03)
        for s in range(16):
            ts = t0 + s * S16
            if ts >= dur:
                break
            in_groove = g0 <= ts < outro
            intro = ts < g0
            if intro:
                # soft heartbeat pulse under the opening
                if s in (0, 6, 8):
                    place(drums, lo, ts, 0.35)
                continue
            if not in_groove:
                continue
            # 3-3-2 parai groove
            if s in (0, 3, 6, 8, 11, 14):
                place(drums, lo, ts, 0.75 if s in (0, 8) else 0.55)
                place(tonal, bass(root, S16 * 2.5), ts, 0.28)
            if s in (2, 5, 7, 10, 13, 15):
                place(drums, hi, ts, 0.35)
            if ts >= lift and s in (1, 9):
                place(drums, hi, ts, 0.22)
            if s in (4, 12):
                place(drums, cl, ts, 0.5 if ts >= lift else 0.38)

    # lead: hook every 2 bars in the groove, higher variation after the lift
    t = g0
    k = 0
    while t < outro - 0.1:
        phrase = HOOK_B if (t >= lift and k % 2 == 1) else HOOK
        prev = phrase[0][2] - 2
        for st, ln, m in phrase:
            ts = t + st * S16
            if ts >= outro:
                break
            place(lead, lead_note(prev, m, ln * S16 * 0.95), ts, 0.11)
            prev = m
        t += 2 * BAR
        k += 1

    # intro: one slow call of the hook over the pulse
    prev = 67
    for st, ln, m in HOOK[:6]:
        place(lead, lead_note(prev, m, ln * S16 * 1.8 * 0.95), 1.2 + st * S16 * 1.8, 0.07)
        prev = m

    # riser into the groove and into the outro, impact at the outro
    place(drums, riser(1.6), g0 - 1.6, 1.0)
    place(drums, riser(1.6), outro - 1.6, 1.0)
    place(drums, impact(), outro, 0.8)
    # outro: final long note of the hook
    place(lead, lead_note(60, 62, 4.0), outro + 0.3, 0.09)

    # light reverb on lead and pads
    wet = tonal + lead
    rev = np.zeros(n)
    for d, g in [(0.089, 0.32), (0.131, 0.28), (0.197, 0.24), (0.293, 0.2), (0.411, 0.15)]:
        k_ = int(d * SR)
        rev[k_:] += wet[:-k_] * g
    mix = drums + tonal + lead + 0.5 * rev

    tt = np.arange(n) / SR
    mix *= np.clip(np.minimum(1, (dur - tt) / 2.5), 0, 1)
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)  # gentle glue
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.89
    left = mix
    right = np.roll(mix, int(0.008 * SR)) * 0.6 + mix * 0.4
    data = (np.stack([left, right], 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main():
    p1, p2, col, base = sys.argv[1:5]
    scenes = mv.build_scenes(mv.load(p1), mv.load(p2), mv.load(col))
    starts = [s for s, _ in scenes]
    if len(sys.argv) > 5 and sys.argv[5] == "--preview":
        for tt in [float(x) for x in sys.argv[6].split(",")]:
            mv.render_frame(scenes, tt).save(f"{base}_{tt:05.1f}.jpg", quality=88)
        return
    if len(sys.argv) > 5 and sys.argv[5] == "--music-only":
        make_music(base + ".wav", mv.TOTAL, dict(groove=starts[1], lift=starts[3], outro=starts[-1]))
        return

    silent = base + ".video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{mv.W}x{mv.H}", "-r", str(mv.FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-tune", "grain",
           "-pix_fmt", "yuv420p", "-profile:v", "high", silent]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(mv.TOTAL * mv.FPS)
    for i in range(nframes):
        proc.stdin.write(mv.render_frame(scenes, i / mv.FPS).tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()

    wav = base + ".wav"
    make_music(wav, mv.TOTAL, dict(groove=starts[1], lift=starts[3], outro=starts[-1]))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", base + ".mp4"], check=True)
    # silent version still carries a quiet audio track; some apps reject video-only files
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent,
                    "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo",
                    "-c:v", "copy", "-c:a", "aac", "-shortest",
                    "-movflags", "+faststart", base + "-no-music.mp4"], check=True)
    os.remove(silent)
    os.remove(wav)


if __name__ == "__main__":
    main()
