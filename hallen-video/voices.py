"""Make Tamil voice clips with word timings. Hallen = child voice, Jesus = calm adult male.
Clips are cached in voice_cache/ so the video can be rebuilt without the network."""
import asyncio, hashlib, json, os, subprocess

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voice_cache')
VOICES = {
    'kid':   dict(voice='ta-IN-PallaviNeural', rate='-22%', pitch='+18Hz', shift=1.14),
    'jesus': dict(voice='ta-IN-ValluvarNeural', rate='-24%', pitch='-4Hz', shift=1.0),
}
SR = 44100


def key(who, text):
    v = VOICES[who]
    return hashlib.sha1(json.dumps([v, text], ensure_ascii=False).encode()).hexdigest()[:16]


async def _make(who, text, mp3):
    import edge_tts
    v = VOICES[who]
    c = edge_tts.Communicate(text, v['voice'], rate=v['rate'], pitch=v['pitch'],
                             boundary='WordBoundary', proxy=os.environ.get('HTTPS_PROXY'))
    words = []
    with open(mp3, 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append(ch['offset'] / 1e7)
    return words


def clip(who, text):
    """Returns (wav path, duration seconds, list of word start times)."""
    os.makedirs(CACHE, exist_ok=True)
    k = key(who, text)
    wav, meta = os.path.join(CACHE, k + '.wav'), os.path.join(CACHE, k + '.json')
    if not os.path.exists(meta):
        mp3 = os.path.join(CACHE, k + '.mp3')
        words = asyncio.run(_make(who, text, mp3))
        s = VOICES[who]['shift']
        # a child voice: raise pitch and formants a little, keep the speed the same
        af = f'asetrate={int(24000 * s)},aresample={SR},atempo={1 / s:.4f}' if s != 1.0 else f'aresample={SR}'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af', af + ',silenceremove=start_periods=1:start_threshold=-50dB',
                        '-ac', '1', wav], check=True)
        os.remove(mp3)
        dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                             '-of', 'csv=p=0', wav]).decode().strip())
        lead = words[0] if words else 0.0
        words = [max(0.0, w - lead) for w in words]
        json.dump(dict(dur=dur, words=words, text=text, who=who), open(meta, 'w'), ensure_ascii=False)
    m = json.load(open(meta))
    return wav, m['dur'], m['words']


if __name__ == '__main__':
    import sys
    print(clip(sys.argv[1], sys.argv[2]))
