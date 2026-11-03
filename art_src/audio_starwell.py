"""Sounds for the side chapter "Under the Lake: The Starwell", the Keeper's
Journal and the name-stones. Uses the same synth and conventions as audio.py
(which it imports); writes only the files listed below.

    python audio_starwell.py             # everything
    python audio_starwell.py sfx         # one group: music | ambience | sfx | voice
    python audio_starwell.py sfx stars   # single ids

Outputs (assets/audio/):
  music/starwell.ogg   music box over a muffled underwater pad, clockwork ticking (E, lydian colour)
  music/stars.ogg      after the Great Orrery is lit: bells, choir, harp (E major)
  ambience/underlake.ogg  deep water hum, a glass dome creaking, distant bubbles
  sfx/  shadow_on shadow_off orrery_start orrery_tick name_stone journal_open bubbles stars lamp_light
  voice/orrin_0..7.wav  Orrin the Stargazer: old, warm, creaky, absent-minded "hm"
"""
import sys

import numpy as np

import audio as A
import synth as S
from synth import SR, TAU, m

_n, _t = A._n, A._t


# ================================================================== music ===
def tick(f=3000.0, gain=1.0):
    """One soft clockwork tick: a short filtered click with a tiny metal ring."""
    n = _n(0.06)
    x = S.fft_filter(S.noise(n * 2), S.band_gain(f * 0.6, f * 1.7))[:n] * np.exp(-_t(n) / 0.0035)
    ring = A.metal_clink(f * 0.75, 0.25)[:n]
    return (S.normalize(x, 0.6) + ring * 0.6) * gain


def water_bed(n, cutoff=220.0, gain=0.08, cycles=3, phase=0.0):
    t = np.arange(n) / SR
    T = n / SR
    out = []
    for ch in range(2):
        w = S.fft_filter(S.pink(n), S.low_gain(cutoff, 2))
        sw = 0.55 + 0.45 * A.lfo(t, T, cycles, phase + ch * 1.3)
        out.append(S.normalize(w * sw, gain))
    return np.stack(out)


# chord: pad voicing (low, muffled), bass, six music-box notes for arpeggios
SW = {
    "E": (["E3", "B3", "D#4", "F#4"], "E2", ["B4", "E5", "F#5", "G#5", "B5", "D#6"]),
    "C": (["C3", "G3", "B3", "E4"], "C2", ["G4", "C5", "E5", "F#5", "B5", "E6"]),
    "A": (["A2", "E3", "G#3", "C#4"], "A1", ["E5", "G#5", "A5", "B5", "C#6", "E6"]),
    "C#m": (["C#3", "G#3", "B3", "E4"], "C#2", ["G#4", "C#5", "D#5", "E5", "G#5", "B5"]),
    "E/G#": (["G#2", "E3", "B3", "D#4"], "G#1", ["B4", "D#5", "E5", "G#5", "B5", "E6"]),
    "F#m": (["F#2", "C#3", "E3", "A3"], "F#1", ["C#5", "E5", "F#5", "G#5", "A5", "C#6"]),
    "B": (["B2", "F#3", "A3", "E4"], "B1", ["F#4", "B4", "C#5", "E5", "F#5", "A5"]),
}


def music_starwell():
    s = A.Song(58, 96, sd=301)  # 12 chords of 8 beats, ~99 s
    prog = ["E", "C", "E", "A", "C#m", "A", "E/G#", "B", "C", "E", "F#m", "B"]
    r = S.rand()
    pats = [[0, 2, 4, 5, 3, 1], [1, 3, 5, 4, 2, 0, 2, 4], [0, 3, 1, 4, 2, 5]]
    for i, c in enumerate(prog):
        voic, bass, box = SW[c]
        b = i * 8
        # the deep, muffled pad: dark partials, slow swells
        s.pad(b, 8, voic, gain=0.15, bright=0.05, attack=3.0, release=3.5, width=0.4)
        s.pad(b, 8, [bass], gain=0.16, bright=0.0, attack=3.0, release=3.5)
        # music box arpeggios, with gaps (it is a lonely place)
        pat = pats[i % 3]
        dense = i in (3, 4, 5, 6, 9, 10)
        step = 0.5 if dense else 1.0
        k = 0
        bb = b
        while bb < b + 8 - 1e-6:
            if r.random() < (0.82 if dense else 0.7):
                nt = box[pat[k % len(pat)]]
                v = r.uniform(0.28, 0.4) * (1.2 if k % 4 == 0 else 1.0)
                s.put(bb, A.I_box(m(nt), step * s.spb, v), 0.55, pan=0.35 * np.sin(k * 0.9 + i))
            bb += step
            k += 1
    # the Wick theme, slowed to a music-box lullaby, in E
    s.line(16, A.WICK_MAJ, "E5", A.I_cel, 0.55, gain=0.7, pan=-0.1)
    s.line(32, A.WICK_A, "C#5", A.I_cel, 0.52, gain=0.68, pan=-0.1)          # C# E G# F# E D# C#
    for b, nt in ((40, "E6"), (42.5, "C#6"), (44, "B5"), (46, "G#5")):
        s.note(b, A.I_glass, nt, 2, 0.32, gain=0.45, pan=0.4)
    for b, nt in ((65, "B5"), (68, "G5"), (70.5, "E5")):                     # suspended, very sparse
        s.note(b, A.I_box, nt, 2, 0.45, gain=0.6, pan=0.25)
    s.line(72, A.WICK_MAJ, "E4", A.I_cel, 0.55, gain=0.75, pan=-0.15)
    s.line(72, A.WICK_MAJ, "E5", A.I_box, 0.28, gain=0.35, pan=0.4)
    s.line(80, A.WICK_C, "F#4", A.I_cel, 0.5, gain=0.7, pan=-0.15)           # C# B A G# F#
    for _ in range(14):  # far-off stars
        s.note(r.uniform(0, 96), A.I_glass, ["E7", "B6", "G#6", "F#7", "D#7"][r.integers(5)], 1,
               r.uniform(0.08, 0.18), gain=0.22, pan=r.uniform(-0.9, 0.9))
    # clockwork: tick-tock on every beat, falling silent for the suspended bar
    for beat in range(96):
        if 64 <= beat < 72:
            continue
        f = 3100.0 if beat % 2 == 0 else 2100.0
        s.put(beat, tick(f, 1.0), 0.05 if beat % 2 == 0 else 0.04, pan=0.3 if beat % 2 == 0 else -0.3, hum=0.003)
    for beat in (0, 32, 72):  # a soft wind-up of gears now and then
        for q in range(6):
            s.put(beat - 1.5 + q * 0.12, tick(4200 - q * 150, 1.0), 0.03, pan=0.5, hum=0)
    s.mix.buf += water_bed(s.mix.L, 240, 0.05, 3)
    return s.render(5.0, wet=0.5, damp=1.2, predelay=0.04, lowpass=7500, rms_db=-22)


ST = {  # pad voicing, bass, six harp notes
    "E": (["E3", "B3", "E4", "G#4"], "E2", ["E3", "B3", "E4", "G#4", "B4", "E5"]),
    "B/D#": (["D#3", "B3", "D#4", "F#4"], "D#2", ["D#3", "B3", "D#4", "F#4", "B4", "D#5"]),
    "C#m": (["C#3", "G#3", "C#4", "E4"], "C#2", ["C#3", "G#3", "C#4", "E4", "G#4", "C#5"]),
    "A": (["A2", "E3", "A3", "C#4"], "A1", ["A2", "E3", "A3", "C#4", "E4", "A4"]),
    "E/G#": (["G#2", "E3", "B3", "E4"], "G#1", ["G#2", "E3", "B3", "E4", "G#4", "B4"]),
    "B": (["B2", "F#3", "B3", "D#4"], "B1", ["B2", "F#3", "B3", "D#4", "F#4", "B4"]),
}


def music_stars():
    s = A.Song(64, 80, sd=302)  # 10 chords of 8 beats, 75 s
    prog = ["E", "B/D#", "C#m", "A", "E/G#", "A", "B", "C#m", "A", "B"]
    r = S.rand()
    for i, c in enumerate(prog):
        voic, bass, harp = ST[c]
        b = i * 8
        rise = 0.75 + 0.25 * min(1.0, i / 5)
        s.pad(b, 8, voic, gain=0.12 * rise, bright=0.45, attack=2.0, release=2.8)
        s.choir(b, 8, voic[1:], gain=0.1 * rise, vowel="a" if i % 2 else "o", attack=2.2, release=2.8)
        s.note(b, A.I_cello, bass if not bass.endswith("1") else bass.replace("1", "2"), 8, 0.4,
               gain=0.42, pan=-0.25)
        if i >= 2:
            s.arp(b, 8, harp, A.I_harp, [0, 1, 2, 3, 4, 5, 4, 2], 0.5, vel=0.3, gain=0.45, pan=-0.3)
    s.line(0, A.WICK_MAJ, "E5", A.I_cel, 0.55, gain=0.7, pan=0.15)
    s.line(8, A.WICK_MAJ_B, "B4", A.I_cel, 0.52, gain=0.7, pan=0.15)
    s.line(32, A.WICK_MAJ, "E5", A.I_glass, 0.5, gain=0.6, pan=0.2)
    s.line(32, A.WICK_MAJ, "E4", A.I_hum, 0.35, gain=0.3, pan=-0.2)
    s.line(40, A.WICK_MAJ_B, "A4", A.I_glass, 0.5, gain=0.6, pan=0.2)
    s.line(48, A.WICK_MAJ_C, "E5", A.I_glass, 0.5, gain=0.6, pan=0.2)
    s.line(64, A.WICK_MAJ, "E5", A.I_box, 0.45, gain=0.55, pan=0.3)
    s.line(72, [(7, 2), (4, 2), (2, 2), (0, 2)], "E5", A.I_box, 0.42, gain=0.5, pan=0.3)
    for b, nt, g in ((0, "E3", 0.22), (32, "E3", 0.2), (64, "B2", 0.16)):
        s.note(b, lambda n, h, v: S.church_bell(n, 9.0, v), nt, 1, 0.7, gain=g, pan=-0.3)
    penta = ["E6", "F#6", "G#6", "B6", "C#7", "E7"]
    for _ in range(34):  # the dome full of stars
        s.note(r.uniform(0, 80), A.I_glass, penta[r.integers(len(penta))], 1, r.uniform(0.12, 0.26),
               gain=0.3, pan=r.uniform(-0.9, 0.9))
    return s.render(4.0, wet=0.48, damp=0.9, predelay=0.03, rms_db=-21)


MUSIC = {"starwell": music_starwell, "stars": music_stars}


# =============================================================== ambience ===
def bubble(f0=None, gain=1.0):
    r = S.rand()
    n = _n(r.uniform(0.018, 0.04))
    f = (f0 or r.uniform(240, 600)) * (1 + 2.2 * _t(n) / (n / SR))
    return np.sin(TAU * np.cumsum(f) / SR) * np.hanning(n) * gain


def bubble_burst(count, spread=0.6, lowpass=1800):
    r = S.rand()
    parts = [(r.uniform(0, spread), bubble(None, r.uniform(0.4, 1.0))) for _ in range(count)]
    x = A.mixdown(parts)
    return S.fft_filter(np.pad(x, (0, 256)), S.low_gain(lowpass, 2))


def glass_groan(dur=1.6, f0=380.0):
    """The dome flexing under the weight of the lake: a slow resonant moan."""
    r = S.rand()
    n = _n(dur)
    t = _t(n)
    glide = 1 + 0.035 * np.sin(np.pi * t / dur + r.uniform(-0.5, 0.5)) + 0.008 * np.sin(TAU * 2.3 * t)
    x = S.additive(f0, n, [1, 2.31, 4.07, 6.1], [1, 0.45, 0.22, 0.08], [None] * 4, attack=0, vib=glide)
    fric = S.fft_filter(S.noise(n), S.band_gain(f0 * 0.8, f0 * 3)) * 0.25
    stick = 0.7 + 0.3 * np.sign(np.sin(TAU * np.cumsum(r.uniform(9, 16) * glide) / SR))
    x = (x * stick + fric) * S.ramp_env(n, dur * 0.35, dur * 0.45)
    return S.normalize(S.fft_filter(x, S.low_gain(2400, 2)), 0.5)


def amb_underlake():
    S.seed(401)
    T = 40.0
    mx = S.Mix(T)
    n = mx.L
    t = np.arange(n) / SR
    mx.buf += water_bed(n, 170, 0.09, 3)
    mx.buf += water_bed(n, 520, 0.018, 5, 2.0)
    hum = np.sin(TAU * 44 * t) * (0.6 + 0.4 * A.lfo(t, T, 2)) + 0.45 * np.sin(TAU * 66 * t + 0.5) * A.lfo(t, T, 3, 1.0)
    mx.add(0, S.normalize(hum, 0.035), 1.0, 0.0)
    r = S.rand()
    for _ in range(5):
        mx.add(r.uniform(0, T), glass_groan(r.uniform(1.2, 2.2), r.uniform(280, 520)), r.uniform(0.035, 0.06),
               r.uniform(-0.8, 0.8))
    for _ in range(4):
        mx.add(r.uniform(0, T), A.creak(r.uniform(0.7, 1.3), r.uniform(70, 120)), r.uniform(0.03, 0.05),
               r.uniform(-0.9, 0.9))
    for _ in range(8):
        mx.add(r.uniform(0, T), bubble_burst(int(r.integers(3, 8)), r.uniform(0.4, 0.9)), r.uniform(0.04, 0.08),
               r.uniform(-0.9, 0.9))
    buf = S.reverb(mx.buf, S.make_ir(5.0, damp=1.5, predelay=0.05), wet=0.55)
    buf = S.stereo_filter(buf, S.high_gain(25, 2))
    return S.master(buf, -6, -27)


AMBIENCE = {"underlake": amb_underlake}


# ==================================================================== sfx ===
def sfx_shadow_on():
    th = S.thump(95, 52, 0.5, 1.0, 0.12)
    gl = A.mixdown([(0, S.glass(m("E4"), 1.2, 0.6)), (0.01, S.glass(m("B4"), 1.0, 0.25))])
    gl = S.fft_filter(np.pad(gl, (0, 256)), S.low_gain(2200, 2))
    n = _n(0.35)
    air = S.fft_filter(S.noise(n), S.band_gain(200, 900)) * S.ramp_env(n, 0.12, 0.2)
    x = A.mixdown([(0, th * 0.8), (0, S.normalize(gl, 0.5)), (0, S.normalize(air, 0.12))])
    return S.normalize(A.with_reverb(x, 1.0, 0.3, 1.3), 0.38)


def sfx_shadow_off():
    wh = A.sweep_noise(0.55, 1400, 260, 0.6, 0.08, 0.75)
    gl = S.glass(m("E4"), 0.5, 0.3)
    gl *= np.exp(-_t(len(gl)) / 0.12)
    x = A.mixdown([(0, S.normalize(wh, 0.6)), (0, S.normalize(gl, 0.15))])
    return S.normalize(A.with_reverb(x, 0.9, 0.3), 0.24)


def sfx_orrery_start():
    r = S.rand()
    parts = []
    # the key turning: a ratchet that speeds up
    tt = 0.0
    gap = 0.11
    for k in range(9):
        parts.append((tt, tick(r.uniform(2600, 3400), 0.8)))
        tt += gap
        gap *= 0.86
    parts.append((0.05, S.normalize(A.sweep_noise(0.75, 400, 1600, 0.5, 0.6, 0.3), 0.18)))
    # gears engaging
    parts.append((0.82, S.thump(140, 70, 0.3, 0.9, 0.06) * 0.6))
    parts.append((0.82, A.metal_clink(1900, 0.6)))
    parts.append((0.86, A.metal_clink(2700, 0.35)))
    for q in range(4):
        parts.append((1.0 + q * 0.16, tick(3000 if q % 2 == 0 else 2100, 0.55)))
    parts.append((0.9, S.glass(m("E6"), 1.2, 0.18)))
    parts.append((1.05, S.glass(m("B6"), 1.0, 0.12)))
    return S.normalize(A.with_reverb(A.mixdown(parts), 1.0, 0.25), 0.45)


def sfx_orrery_tick():
    x = tick(2900, 1.0)
    return S.normalize(A.with_reverb(x, 0.25, 0.15), 0.2)


def sfx_name_stone():
    ch = A.mixdown([(0, S.glass(m("E6"), 1.4, 0.6)), (0.09, S.glass(m("B6"), 1.2, 0.4)),
                    (0.18, S.music_box(m("G#6"), 1.0, 0.35))])
    wh = A.whisper(0.7)
    wh = S.fft_filter(wh, S.band_gain(400, 5000)) * S.ramp_env(len(wh), 0.2, 0.35)
    x = A.mixdown([(0, ch), (0.05, S.normalize(wh, 0.18))])
    return S.normalize(A.with_reverb(x, 1.4, 0.35), 0.4)


def sfx_journal_open():
    th = S.thump(150, 90, 0.15, 0.6, 0.03)
    n = _n(0.5)
    sw = S.fft_filter(S.noise(n), S.band_gain(1200, 6500)) * np.sin(np.linspace(0, np.pi, n)) ** 2
    cr = A.crackle(n, 40, 2000, 7000, 1.0) * np.sin(np.linspace(0, np.pi, n))
    x = A.mixdown([(0, th), (0.04, S.normalize(sw, 0.45)), (0.04, S.normalize(cr, 0.3))])
    return S.normalize(A.with_reverb(x, 0.6, 0.15), 0.32)


def sfx_bubbles():
    r = S.rand()
    parts = [(r.uniform(0, 0.55) ** 1.2, bubble(r.uniform(260, 700), r.uniform(0.5, 1.0))) for _ in range(9)]
    x = S.fft_filter(np.pad(A.mixdown(parts), (0, 256)), S.low_gain(2600, 2))
    return S.normalize(A.with_reverb(x, 0.8, 0.3), 0.32)


def sfx_stars():
    r = S.rand()
    notes = ["E6", "G#6", "B6", "C#7", "E7", "F#7", "B5", "G#5"]
    parts = []
    for k in range(16):
        parts.append((k * 0.075 + r.uniform(0, 0.03), S.glass(m(notes[k % len(notes)]), 2.0, r.uniform(0.25, 0.5))))
    sw = sum(S.pad(nt, 1.2, 0.5, attack=0.6, release=1.2, bright=0.45) for nt in ("E4", "G#4", "B4"))
    parts.append((0, S.normalize(sw, 0.3)))
    parts.append((0, S.normalize(A.sweep_noise(1.2, 1500, 6000, 0.6, 0.5, 0.5), 0.06)))
    return S.normalize(A.with_reverb(A.mixdown(parts), 2.0, 0.4), 0.45)


def sfx_lamp_light():
    n = _n(0.35)
    whoomph = S.fft_filter(S.noise(n), S.low_gain(600, 2)) * S.ramp_env(n, 0.05, 0.25)
    wh = A.sweep_noise(0.3, 300, 1500, 0.6, 0.3, 0.6)
    ting = A.mixdown([(0, S.glass(m("B6"), 0.9, 0.5)), (0.02, S.music_box(m("E7"), 0.7, 0.25))])
    x = A.mixdown([(0, S.normalize(whoomph, 0.5)), (0, S.normalize(wh, 0.25)), (0.14, ting)])
    return S.normalize(A.with_reverb(x, 0.9, 0.25), 0.38)


SFX = {k[4:]: v for k, v in globals().items() if k.startswith("sfx_") and callable(v)}


# ================================================================= voices ===
ORRIN = dict(f0=126, k=1.04, tilt=1.05, dur=(0.1, 0.14), vib=(6.0, 0.03), breath=0.24, glide=-0.06,
             vowels="o@uoea", cons=["h", "m", "", "b", "m", "h"], fx=None, peak=0.42, attack=0.012)


def orrin_syllable(idx):
    r = S.rand()
    x = A.syllable(ORRIN, idx)
    n = len(x)
    t = _t(n)
    # creak: irregular glottal pulses (vocal fry) taking over toward the end of the syllable
    jit = S.normalize(S.fft_filter(r.standard_normal(n), S.low_gain(30, 1)), 1.0)
    ph = TAU * np.cumsum(r.uniform(36, 50) * (1 + 0.3 * jit)) / SR
    pulses = (0.5 + 0.5 * np.cos(ph)) ** 5
    w = np.clip((t / (n / SR) - 0.4) / 0.6, 0, 1)
    x = x * (1 - 0.5 * w + 0.5 * w * pulses)
    # an absent-minded "hm" trailing off some syllables
    if idx in (1, 4, 6):
        hn = _n(0.075)
        ks = np.arange(1, 8)
        hum = S.additive(ORRIN["f0"] * 0.92, hn, ks, 1.0 / ks ** 2.4, [None] * 7, attack=0.01,
                         vib=1 - 0.04 * _t(hn) / 0.075)
        hum = S.fft_filter(hum, S.low_gain(900, 2)) * S.ramp_env(hn, 0.015, 0.045)
        hum = S.normalize(hum, np.abs(x).max() * 0.45)
        ov = _n(0.012)
        out = np.zeros(n + hn - ov)
        out[:n] += x
        out[n - ov:] += hum
        x = out
    x = S.fft_filter(np.pad(x, (0, 128)), S.low_gain(3800, 1))
    return S.normalize(x, ORRIN["peak"])


VOICES = {"orrin": orrin_syllable}


# ================================================================= output ===
def main(argv):
    groups = {"music": MUSIC, "ambience": AMBIENCE, "sfx": SFX, "voice": VOICES}
    want = argv[0] if argv else "all"
    ids = set(argv[1:])
    rows = []
    for g, table in groups.items():
        if want not in ("all", g):
            continue
        for key, fn in table.items():
            if ids and key not in ids:
                continue
            if g in ("music", "ambience"):
                path = A.write_ogg(f"{g}/{key}.ogg", fn())
                rows.append((f"{g}/{key}", path))
            elif g == "sfx":
                S.seed(sum(map(ord, key)) * 7)
                path = A.write_wav(f"sfx/{key}.wav", fn())
                rows.append((f"sfx/{key}", path))
            else:
                S.seed(sum(map(ord, key)))
                for i in range(8):
                    path = A.write_wav(f"voice/{key}_{i}.wav", fn(i))
                rows.append((f"voice/{key}_0..7", path))
    print(f"{'id':28s} {'sec':>7s} {'peak dB':>8s} {'rms dB':>7s} {'seam':>6s} {'KB':>7s}")
    for name, path in rows:
        sec, peak, rms, seam, size = A.stats(path)
        print(f"{name:28s} {sec:7.2f} {S.db(peak):8.1f} {S.db(rms):7.1f} {seam:6.2f} {size / 1024:7.0f}")


if __name__ == "__main__":
    main(sys.argv[1:])
