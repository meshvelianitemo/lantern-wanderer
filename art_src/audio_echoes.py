"""Sounds for the "Echoes & Home" expansion: the three Echoes (Lark's Song, The Last
Winter, Vesper), the fuller Hollow, and the new ending. Uses the same synth and
conventions as audio.py (which it imports); writes only the files listed below.

    python audio_echoes.py             # everything
    python audio_echoes.py sfx         # one group: music | ambience | sfx | voice
    python audio_echoes.py sfx carve   # single ids

Outputs (assets/audio/):
  music/echo_lark.ogg         a music-box lullaby: the Glimmerdeep tune, older and simpler (D dorian, 3/4)
  music/echo_maud.ogg         the night of the flood: handbell calls over a pulse of rising water (C minor)
  music/echo_vesper.ogg       the mountain alive: lutes, horn, chisels keeping time (D major)
  music/echo_vesper_dark.ogg  the same harmony turned to dread, for the run back up (D minor)
  music/hollow_full.ogg       the Hollow waltz with everyone home: choir, harp, drum, more voices
  music/first_page.ogg        the new ending, plays once: two wicks, one theme, D minor -> D major
  ambience/flood.ogg          rushing water in stone halls that always seems to be rising
  ambience/rootway.ogg        warm hum of a living mountain, distant chisels and voices
  sfx/  bell_ring keeper_wake memory_in memory_out keepsake fear_beat dark_rise carve supper
  voice/{lark,maud,vesper,edda,keeper,glim}_0..7.wav

The Echo tracks share a slight tape "wow" and a little dust, so they sound remembered.
"""
import sys

import numpy as np

import audio as A
import synth as S
from synth import SR, TAU, m

_n, _t = A._n, A._t


# ================================================================ helpers ===
def wow(buf, cents=5.0, cycles=24):
    """Loop-safe slow pitch wobble (like an old tape) - a whole number of cycles per loop."""
    n = buf.shape[1]
    T = n / SR
    t = np.arange(n) / SR
    depth = (2 ** (cents / 1200) - 1) * T / (TAU * cycles)
    pos = np.mod((t + depth * np.sin(TAU * cycles * t / T)) * SR, n)
    i0 = np.floor(pos).astype(int)
    frac = pos - i0
    out = np.empty_like(buf)
    for ch in range(2):
        xp = np.concatenate([buf[ch], buf[ch, :2]])
        out[ch] = xp[i0] * (1 - frac) + xp[i0 + 1] * frac
    return out


def dust(n, gain=0.004):
    """Faint loop-safe crackle, like an old recording."""
    return np.stack([S.normalize(A.crackle(n, 5, 1500, 6000, 1.0, 0.04), gain),
                     S.normalize(A.crackle(n, 5, 1500, 6000, 1.0, 0.04), gain)])


def shepard_noise(n, f_lo=180.0, octaves=3.0, bands=4, cycles=3, q=0.3):
    """Noise bands that climb forever (each fades in at the bottom, out at the top):
    the sound of water that is always rising. Loop-safe."""
    T = n / SR
    x = S.pink(n)

    def g(f, tt):
        out = np.zeros_like(f)
        for k in range(bands):
            ph = ((tt / T) * cycles + k / bands) % 1.0
            c = f_lo * 2 ** (ph * octaves)
            out += np.sin(np.pi * ph) ** 2 / (1.0 + ((f - c) / (c * q)) ** 2)
        return out
    return S.tv_filter(x, g, 2048)


def fo(x, sec=0.3):
    """Fade the end of a short note so it never stops with a click."""
    x = x.copy()
    k = min(len(x), int(sec * SR))
    x[len(x) - k:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, k))
    return x


# a diatonic third above each scale degree (semitones above the tonic -> added semitones)
THIRD_DORIAN = {0: 3, 2: 3, 3: 4, 5: 4, 7: 3, 9: 3, 10: 4}
THIRD_MINOR = {0: 3, 2: 3, 3: 4, 5: 3, 7: 3, 8: 4, 10: 4}


def thirds(seq, table):
    return [(None if o is None else o + table[o % 12], d) for o, d in seq]


def handbell(note, dur=2.2, vel=0.8):
    """A small brass handbell: bright strike, then a shimmering ring (two close
    partials beating), brighter and shorter than a church bell."""
    f = S.hz(note)
    n = int(dur * SR)
    s = (f / 784.0) ** -0.3
    x = S.additive(f, n, [1, 1.0021, 2.0, 2.51, 3.0, 4.18, 5.43, 6.8],
                   [1, 0.55, 0.32, 0.26, 0.42, 0.2, 0.12, 0.06],
                   [1.5 * s, 1.3 * s, 0.9 * s, 0.6 * s, 0.75 * s, 0.32 * s, 0.2 * s, 0.11 * s], attack=0.001)
    x[:96] += S.click(3, 2500, 9000, 0.25)[:96]   # the clapper
    return fo(x, min(0.6, dur * 0.4)) * vel


def I_bell(n, h, v):
    return handbell(n, max(1.8, h + 1.2), v)


def shaker(gain=1.0):
    k = _n(0.05)
    return S.fft_filter(S.noise(k), S.band_gain(5000, 11000)) * np.exp(-_t(k) / 0.012) * gain


def hand_drum(vel=1.0):
    return S.thump(165, 110, 0.25, vel, 0.07)


def chisel(f=3200.0, gain=1.0):
    """One chisel tap on stone: a sharp click, a short metal ring, a dull knock."""
    k = _n(0.12)
    tick = S.fft_filter(S.noise(k * 2), S.band_gain(2000, 7000))[:k] * np.exp(-_t(k) / 0.004)
    ring = A.metal_clink(f, 0.35)
    knock = S.thump(240, 160, 0.08, 0.6, 0.015)
    return A.mixdown([(0, S.normalize(tick, 0.7)), (0, ring[:_n(0.12)]), (0, knock)]) * gain


# ================================================================== music ===
LK = {  # pad voicing, harp bass, three music-box notes for the lullaby rocking
    "Dm": (["D3", "A3", "F4"], "D3", ["A4", "D5", "F5"]),
    "E/D": (["D3", "G#3", "B3"], "D3", ["G#4", "B4", "E5"]),
    "Bbmaj7": (["Bb2", "F3", "A3"], "Bb2", ["F4", "A4", "D5"]),
    "Gm": (["G2", "D3", "Bb3"], "G2", ["G4", "Bb4", "D5"]),
    "Asus": (["A2", "E3", "D4"], "A2", ["E4", "A4", "D5"]),
    "A": (["A2", "E3", "C#4"], "A2", ["E4", "A4", "C#5"]),
}


def music_echo_lark():
    s = A.Song(60, 96, sd=501)  # 32 bars of 3/4, 96 s
    prog = ["Dm", "E/D", "Dm", "Bbmaj7", "Gm", "Dm", "E/D", "Asus",
            "Dm", "E/D", "Dm", "Bbmaj7", "Gm", "A", "Dm", "Dm"]
    r = S.rand()
    for i, c in enumerate(prog):
        voic, bass, rock = LK[c]
        b = i * 6
        s.pad(b, 6, voic, gain=0.09, bright=0.2, attack=2.0, release=2.6)
        for bar in range(2):
            bb = b + bar * 3
            s.note(bb, A.I_harp, bass, 3, 0.5, gain=0.5, pan=-0.2)
            # the rocking "pah-pah" of a cradle song
            for q, k in ((1, 0), (2, 1 if bar == 0 else 2)):
                s.note(bb + q, A.I_box, rock[k], 1, r.uniform(0.2, 0.26), gain=0.42, pan=0.25 - 0.1 * q)
    # the Wick theme, slowed into a lullaby (3/4: everything half as long again)
    s.line(12, A.WICK_A, "D5", A.I_box, 0.55, gain=0.62, pan=0.1, scale=1.5)
    s.line(24, A.WICK_B, "D5", A.I_box, 0.5, gain=0.58, pan=0.1, scale=1.5)
    s.line(36, A.WICK_C, "D5", A.I_box, 0.5, gain=0.58, pan=0.1, scale=1.5)
    s.line(48, A.WICK_A, "D4", A.I_cel, 0.5, gain=0.62, pan=-0.1, scale=1.5)
    s.line(48, [(None, 0.5)] + thirds(A.WICK_A, THIRD_DORIAN), "D5", A.I_box, 0.26, gain=0.34, pan=0.4,
           scale=1.5)
    s.line(60, A.WICK_B, "D4", A.I_hum, 0.4, gain=0.32, pan=-0.15, scale=1.5)
    s.line(60, A.WICK_B, "D5", A.I_box, 0.4, gain=0.48, pan=0.2, scale=1.5)
    s.line(72, A.WICK_C, "D5", A.I_box, 0.45, gain=0.55, pan=0.15, scale=1.5)
    for b, nt in ((86, "A5"), (89, "F5"), (92, "D5")):
        s.note(b, A.I_box, nt, 2, 0.32, gain=0.45, pan=0.3)
    for _ in range(12):  # a few crystals catching the light
        s.note(r.uniform(0, 96), A.I_glass, ["D7", "A6", "E7", "F6"][r.integers(4)], 1,
               r.uniform(0.08, 0.16), gain=0.22, pan=r.uniform(-0.9, 0.9))
    s.mix.buf += dust(s.mix.L, 0.004)
    out = s.render(4.5, wet=0.5, damp=1.1, predelay=0.03, lowpass=5800, rms_db=-22)
    return wow(out, 7.0, 24)


MD = {  # pad, cello root, ostinato root
    "Cm": (["C3", "G3", "Eb4", "G4"], "C2", "C3"), "Ab": (["Ab2", "Eb3", "C4", "Eb4"], "Ab1", "Ab2"),
    "Eb": (["Eb3", "Bb3", "Eb4", "G4"], "Eb2", "Eb3"), "Bb": (["Bb2", "F3", "D4", "F4"], "Bb1", "Bb2"),
    "Fm": (["F2", "C3", "Ab3", "C4"], "F2", "F2"), "G": (["G2", "D3", "B3", "D4"], "G1", "G2"),
}


def music_echo_maud():
    s = A.Song(84, 128, sd=502)  # 32 bars, ~91 s
    phrases = [["Cm", "Ab", "Eb", "Bb"], ["Cm", "Ab", "Fm", "G"], ["Cm", "Ab", "Eb", "Bb"], ["Ab", "Bb", "Cm", "G"],
               ["Fm", "Cm", "Ab", "G"], ["Fm", "Cm", "Ab", "G"], ["Cm", "Ab", "Eb", "Bb"], ["Ab", "Bb", "Cm", "Cm"]]
    r = S.rand()
    for p, phrase in enumerate(phrases):
        tender = p in (4, 5)
        for i, c in enumerate(phrase):
            voic, root, ost = MD[c]
            b = (p * 4 + i) * 4
            s.pad(b, 4, voic, gain=0.08 if tender else 0.1, bright=0.25, attack=1.0, release=1.6)
            s.note(b, A.I_cello, root.replace("1", "2"), 4, 0.42, gain=0.42, pan=-0.3)
            if tender:
                s.choir(b, 4, voic[1:], gain=0.09, vowel="o", attack=1.2, release=1.8)
            # urgent eighth-note ostinato, quieter while the music turns tender
            for k, o in enumerate([0, 12, 7, 12, 0, 12, 7, 10]):
                v = (0.42 if k % 2 == 0 else 0.32) * (0.6 if tender else 1.0)
                s.put(b + k * 0.5, A.I_mute(m(ost) + o, 0.3, v), 0.55, 0.2, hum=0.003)
            # the water's pulse: a low beat on every step, heavier at the bar
            for q in range(4):
                s.put(b + q, S.thump(56, 36, 0.4, 1.0, 0.13), 0.42 if q == 0 else 0.22, 0.0, hum=0)
    # Maud's handbell: "ring, ring" - calling everyone home
    for b in (0, 16, 64, 96):
        for k, nt in enumerate(["G5", "G5", "C6"]):
            s.note(b + 0.5 + k * 0.75, I_bell, nt, 1, 0.42 - k * 0.04, gain=0.42, pan=0.35)
    # the Wick theme rung out on the bell, in C minor
    s.line(32, A.WICK_A, "C5", I_bell, 0.46, gain=0.5, pan=0.3)
    s.line(40, A.WICK_B_FLAT, "C5", I_bell, 0.44, gain=0.48, pan=0.3)
    s.line(104, A.WICK_A, "C5", I_bell, 0.46, gain=0.5, pan=0.3)
    s.line(112, A.WICK_C, "C5", I_bell, 0.44, gain=0.5, pan=0.3)
    # tender: the theme on celesta while the ostinato softens
    s.line(68, A.WICK_C, "G4", A.I_cel, 0.5, gain=0.6, pan=-0.15, scale=2.0)
    s.line(84, A.WICK_A, "C5", A.I_cel, 0.45, gain=0.55, pan=-0.15)
    for _ in range(8):
        s.note(r.uniform(0, 128), A.I_glass, ["G6", "C7", "Eb7", "D7"][r.integers(4)], 1,
               r.uniform(0.08, 0.15), gain=0.2, pan=r.uniform(-0.9, 0.9))
    # rising water under it all, swelling every four bars
    n = s.mix.L
    t = np.arange(n) / SR
    T = n / SR
    for ch in range(2):
        rise = shepard_noise(n, 140.0, 2.5, 4, 8, 0.35)
        s.mix.buf[ch] += S.normalize(rise * (0.55 + 0.45 * A.lfo(t, T, 8, ch * 0.6)), 0.05)
    s.mix.buf += dust(n, 0.003)
    out = s.render(3.5, wet=0.45, damp=1.4, predelay=0.04, lowpass=7000, rms_db=-21)
    return wow(out, 4.0, 32)


VS = {  # pad voicing, bass, six lute notes for arpeggios
    "D": (["D3", "A3", "D4", "F#4"], "D2", ["D3", "A3", "D4", "F#4", "A4", "D5"]),
    "G": (["G2", "D3", "B3", "D4"], "G2", ["G2", "D3", "G3", "B3", "D4", "G4"]),
    "Bm": (["B2", "F#3", "D4", "F#4"], "B1", ["B2", "F#3", "B3", "D4", "F#4", "B4"]),
    "A": (["A2", "E3", "C#4", "E4"], "A1", ["A2", "E3", "A3", "C#4", "E4", "A4"]),
    "Em": (["E3", "B3", "E4", "G4"], "E2", ["E3", "B3", "E4", "G4", "B4", "E5"]),
    "D/F#": (["F#2", "A3", "D4", "F#4"], "F#2", ["F#2", "D3", "A3", "D4", "F#4", "A4"]),
}
VS_PHRASES = [["D", "G", "Bm", "A"], ["D", "G", "Em", "A"], ["G", "D/F#", "Em", "A"], ["D", "G", "A", "D"],
              ["Bm", "G", "D", "A"], ["Bm", "G", "Em", "A"], ["D", "G", "Bm", "A"], ["G", "A", "D", "D"]]


def music_echo_vesper():
    s = A.Song(100, 128, sd=503)  # 32 bars, ~77 s
    r = S.rand()
    pats = [[0, 2, 4, 5, 3, 2, 4, 1], [0, 3, 1, 4, 2, 5, 3, 4]]
    for p, phrase in enumerate(VS_PHRASES):
        for i, c in enumerate(phrase):
            voic, bass, arp = VS[c]
            b = (p * 4 + i) * 4
            full = p in (2, 3, 6, 7)
            s.pad(b, 4, voic, gain=0.09 if not full else 0.11, bright=0.5, attack=0.8, release=1.4)
            s.note(b, A.I_lute, bass.replace("1", "2"), 2, 0.55, gain=0.6, pan=-0.2)
            s.note(b + 2, A.I_lute, bass.replace("1", "2"), 2, 0.4, gain=0.5, pan=-0.2)
            s.arp(b, 4, arp, A.I_lute, pats[(p + i) % 2], 0.5, vel=0.34, gain=0.5, pan=0.25)
            if full:
                s.choir(b, 4, voic[1:], gain=0.07, vowel="a", attack=0.8, release=1.4)
            # busy hands: a hand drum, a shaker, and the Keepers' chisels keeping time
            s.put(b, hand_drum(0.9), 0.3, -0.1, hum=0.002)
            s.put(b + 2, hand_drum(0.7), 0.22, -0.1, hum=0.002)
            for k in range(8):
                s.put(b + k * 0.5, shaker(1.0), 0.05 if k % 2 else 0.03, 0.45, hum=0.004)
            if (p * 4 + i) % 2 == 1:
                for o, f, g in ((1.5, 3300, 0.1), (3.0, 2900, 0.12), (3.5, 3100, 0.08)):
                    s.put(b + o, chisel(f), g, r.uniform(-0.7, -0.3), hum=0.004)
    s.line(16, A.WICK_MAJ, "D4", A.I_horn, 0.55, gain=0.62, pan=0.1)
    s.line(24, A.WICK_MAJ_B, "D4", A.I_horn, 0.55, gain=0.62, pan=0.1)
    s.line(48, A.WICK_MAJ, "D5", A.I_kal, 0.6, gain=0.62, pan=0.3)
    s.line(56, A.WICK_MAJ_C, "D5", A.I_kal, 0.58, gain=0.62, pan=0.3)
    s.line(64, [(o, d) for o, d in A.WICK_MAJ], "B4", A.I_cel, 0.5, gain=0.55, pan=-0.2)  # bridge, in B minor
    s.line(80, A.WICK_MAJ_B, "D5", A.I_cel, 0.5, gain=0.55, pan=-0.2)
    s.line(96, A.WICK_MAJ, "D4", A.I_horn, 0.6, gain=0.66, pan=0.1)
    s.line(96, A.WICK_MAJ, "D5", A.I_box, 0.32, gain=0.38, pan=0.4)
    s.line(112, A.WICK_MAJ_C, "D4", A.I_horn, 0.6, gain=0.66, pan=0.1)
    s.mix.buf += dust(s.mix.L, 0.0025)
    out = s.render(2.6, wet=0.3, damp=1.1, rms_db=-21)
    return wow(out, 3.0, 32)


VD = {  # the same chords, gone dark: pad, bass, ostinato root
    "D": (["D3", "A3", "D4", "F4"], "D2", "D2"), "G": (["G2", "D3", "Bb3", "D4"], "G1", "G2"),
    "Bm": (["Bb2", "F3", "D4", "F4"], "Bb1", "Bb1"), "A": (["A2", "E3", "C#4", "G4"], "A1", "A1"),
    "Em": (["E3", "Bb3", "D4", "G4"], "E2", "E2"), "D/F#": (["F2", "A3", "D4", "F4"], "F1", "F2"),
}


def music_echo_vesper_dark():
    s = A.Song(112, 128, sd=504)  # 32 bars, ~69 s
    r = S.rand()
    for p, phrase in enumerate(VS_PHRASES):
        for i, c in enumerate(phrase):
            voic, bass, ost = VD[c]
            b = (p * 4 + i) * 4
            grow = 0.8 + 0.2 * (p % 4) / 3
            s.pad(b, 4, voic, gain=0.09 * grow, bright=0.2, attack=0.5, release=1.0)
            s.note(b, A.I_cello, bass.replace("1", "2"), 4, 0.5, gain=0.5, pan=-0.3)
            for k, o in enumerate([0, 1, 0, 12, 0, 1, 0, 7]):  # the semitone above: dread
                s.put(b + k * 0.5, A.I_mute(m(ost) + 12 + o, 0.28, 0.48 if k % 2 == 0 else 0.36), 0.6, 0.15,
                      hum=0.002)
            for q in range(4):
                s.put(b + q, S.thump(60, 38, 0.35, 1.0, 0.11), (0.5 if q == 0 else 0.28) * grow, 0.0, hum=0)
            if i == 0:
                s.choir(b, 4, ["D3", "Eb3", "A3"] if p % 2 == 0 else ["Bb2", "B2", "F3"], gain=0.07, vowel="u",
                        attack=1.2, release=1.6)
        # every phrase ends with the dark breathing in, landing on the next downbeat
        b_end = (p + 1) * 16
        sw = A.sweep_noise(1.6, 120, 900, 0.5, 0.95, 0.05)
        s.put(b_end - 1.6 / s.spb, S.normalize(sw, 0.5), 0.12, r.uniform(-0.4, 0.4), hum=0)
    s.line(16, A.WICK_A, "D3", A.I_horn, 0.55, gain=0.55, pan=0.1, scale=2.0)
    s.line(48, A.WICK_B_FLAT, "D3", A.I_horn, 0.55, gain=0.55, pan=0.1, scale=2.0)
    s.line(96, A.WICK_A, "D4", A.I_horn, 0.58, gain=0.55, pan=0.1)
    s.line(104, A.WICK_C, "D4", A.I_horn, 0.58, gain=0.55, pan=0.1)
    for _ in range(18):  # thin cold glass, a semitone apart
        b = r.uniform(0, 128)
        nt = ["D6", "Eb6", "A6", "Bb6"][r.integers(4)]
        s.note(b, A.I_glass, nt, 1, r.uniform(0.1, 0.18), gain=0.22, pan=r.uniform(-0.9, 0.9))
    for _ in range(6):
        s.put(r.uniform(0, 128), A.whisper(r.uniform(0.8, 1.4)), 0.035, r.uniform(-1, 1), hum=0)
    s.mix.buf += dust(s.mix.L, 0.003)
    out = s.render(3.0, wet=0.36, damp=1.3, lowpass=6000, rms_db=-20)
    return wow(out, 5.0, 32)


def music_hollow_full():
    """The Hollow waltz (audio.music_hollow) with everyone home: the same tune,
    plus a choir, a harp, a frame drum and tambourine, a cello, and humming."""
    s = A.Song(96, 144, sd=104)  # 48 bars of 3/4, same length and key as `hollow`
    verse = ["Dm", "Gm", "C", "F", "Bb", "Gm", "A7", "Dm"]
    bridge = ["F", "C", "Dm", "A", "Bb", "F", "Gm", "A"]
    form = [verse, verse, verse, bridge, verse, verse]
    bass = {"Dm": "D3", "Gm": "G2", "C": "C3", "F": "F2", "Bb": "Bb2", "A7": "A2", "A": "A2"}
    tri = {"Dm": ["F3", "A3", "D4"], "Gm": ["G3", "Bb3", "D4"], "C": ["G3", "C4", "E4"], "F": ["F3", "A3", "C4"],
           "Bb": ["F3", "Bb3", "D4"], "A7": ["G3", "C#4", "E4"], "A": ["E3", "A3", "C#4"]}
    harp = {"Dm": ["D3", "A3", "D4", "F4", "A4", "D5"], "Gm": ["G2", "D3", "G3", "Bb3", "D4", "G4"],
            "C": ["C3", "G3", "C4", "E4", "G4", "C5"], "F": ["F2", "C3", "F3", "A3", "C4", "F4"],
            "Bb": ["Bb2", "F3", "Bb3", "D4", "F4", "Bb4"], "A7": ["A2", "E3", "G3", "C#4", "E4", "G4"],
            "A": ["A2", "E3", "A3", "C#4", "E4", "A4"]}
    mel = [[("D5", 1), ("F5", 1), ("A5", 1)], [("G5", 2), ("F5", 1)], [("E5", 2), ("G5", 1)], [("F5", 3)],
           [("D5", 1), ("F5", 1), ("Bb5", 1)], [("A5", 2), ("G5", 1)], [("E5", 1), ("G5", 1), ("C#5", 1)],
           [("D5", 3)]]
    bmel = [[("A4", 3)], [("G4", 3)], [("F4", 3)], [("E4", 3)], [("D5", 2), ("C5", 1)], [("A4", 3)],
            [("Bb4", 2), ("A4", 1)], [("A4", 1), ("C#5", 1), ("E5", 1)]]
    r = S.rand()
    sung = {}

    def choir_bar(b, c, gain, vowel):
        if (c, vowel) not in sung:  # the same chord sung once, reused every bar it comes round
            sung[(c, vowel)] = [S.choir(nt, 3 * s.spb, 1.0, vowel=vowel, attack=0.7, release=1.2) for nt in tri[c]]
        for k, x in enumerate(sung[(c, vowel)]):
            s.put(b, x, gain, (k - 1) * 0.6, hum=0)

    for sec, prog in enumerate(form):
        for i, c in enumerate(prog):
            bar = sec * 8 + i
            b = bar * 3
            soft = 0.75 if sec in (0, 5) else 1.0
            s.note(b, A.I_lute, bass[c], 1, 0.62 * soft, gain=0.72, pan=-0.15)
            for beat in (1, 2):
                for k, nt in enumerate(tri[c]):
                    s.put(b + beat + k * 0.03, A.I_lute(m(nt), 0.5 * s.spb, 0.36 * soft), 0.55, 0.1 + k * 0.08,
                          hum=0.004)
            # more voices round the fire
            choir_bar(b, c, 0.045 if sec in (0, 5) else 0.065, "a" if sec % 2 else "o")
            if sec in (1, 2, 3, 4):
                for k, nt in enumerate(tri[c]):
                    s.put(b, S.reed(m(nt), 3 * s.spb, 0.3), 0.34, -0.4 + k * 0.4, hum=0)
                s.put(b, S.thump(110, 70, 0.3, 0.9, 0.08), 0.22, -0.05, hum=0.002)   # frame drum
                for beat in (1, 2):
                    s.put(b + beat, shaker(1.0), 0.06, 0.5, hum=0.004)                 # tambourine
            if sec in (2, 3):
                s.arp(b, 3, harp[c], A.I_harp, [0, 2, 4, 5, 4, 2], 0.5, vel=0.3, gain=0.4, pan=-0.35)
            if sec in (3, 4):
                s.note(b, A.I_cello, bass[c].replace("3", "2"), 3, 0.38, gain=0.35, pan=-0.3)
            if sec in (1, 4):
                bb = b
                for nt, d in mel[i]:
                    s.note(bb, A.I_reed, nt, d, 0.62, gain=0.6, pan=0.2)
                    s.note(bb, A.I_reed, m(nt) - (4 if nt[0] in "AEB" else 3), d, 0.38, gain=0.36, pan=-0.25)
                    if sec == 4:
                        s.note(bb, A.I_box, m(nt) + 12, d, 0.38, gain=0.4, pan=0.45)
                        s.note(bb, A.I_hum, nt, d, 0.4, gain=0.3, pan=-0.1)      # everyone humming along
                    bb += d
            elif sec == 2:
                bb = b
                for nt, d in mel[i]:
                    s.note(bb, A.I_box, m(nt) + 12, d, 0.5, gain=0.52, pan=0.35)
                    s.note(bb, A.I_reed, m(nt) - (4 if nt[0] in "AEB" else 3), d, 0.4, gain=0.4, pan=-0.2)
                    bb += d
            elif sec == 3:
                bb = b
                for nt, d in bmel[i]:
                    s.note(bb, A.I_reed, nt, d, 0.55, gain=0.58, pan=0.2)
                    s.note(bb, A.I_glass, m(nt) + 12, d, 0.18, gain=0.25, pan=0.5)
                    bb += d
            elif sec == 5 and i in (0, 2, 4, 6):
                s.note(b, A.I_box, ["F5", "E5", "D5", "C#5"][i // 2], 3, 0.4, gain=0.45, pan=0.35)
    for _ in range(14):  # lamps in every window
        s.note(r.uniform(0, 144), A.I_box, ["D7", "A6", "F6", "E7"][r.integers(4)], 1, r.uniform(0.1, 0.2),
               gain=0.2, pan=r.uniform(-0.9, 0.9))
    return s.render(1.8, wet=0.3, damp=1.2)


FP = {  # pad voicing, bass, harp arpeggio
    "Dm": (["D3", "A3", "D4", "F4"], "D2", ["D3", "A3", "D4", "F4", "A4", "D5"]),
    "Bb": (["Bb2", "F3", "D4", "F4"], "Bb1", ["Bb2", "F3", "Bb3", "D4", "F4", "Bb4"]),
    "F": (["F3", "C4", "F4", "A4"], "F2", ["F2", "C3", "F3", "A3", "C4", "F4"]),
    "Gm": (["G2", "D3", "Bb3", "D4"], "G1", ["G2", "D3", "G3", "Bb3", "D4", "G4"]),
    "A": (["A2", "E3", "C#4", "E4"], "A1", ["A2", "E3", "A3", "C#4", "E4", "A4"]),
    "D": (["D3", "A3", "D4", "F#4"], "D2", ["D3", "A3", "D4", "F#4", "A4", "D5"]),
    "G": (["G2", "D3", "B3", "D4"], "G1", ["G2", "D3", "G3", "B3", "D4", "G4"]),
    "Bm": (["B2", "F#3", "D4", "F#4"], "B1", ["B2", "F#3", "B3", "D4", "F#4", "B4"]),
    "D/F#": (["F#2", "A3", "D4", "F#4"], "F#1", ["F#2", "D3", "A3", "D4", "F#4", "A4"]),
    "Em": (["E3", "B3", "E4", "G4"], "E2", ["E3", "B3", "E4", "G4", "B4", "E5"]),
}


def music_first_page():
    """Two wicks, one theme. Plays once: alone in D minor, joined, then home in D major."""
    s = A.Song(66, 84, loop=False, tail=9.0, sd=505)
    plan = [["Dm", "Dm", "Bb", "A"], ["Dm", "Bb", "F", "A"], ["D", "G", "Bm", "A"], ["G", "D/F#", "Em", "A"],
            ["D", "G", "A", "D"]]
    for sec, prog in enumerate(plan):
        for i, c in enumerate(prog):
            voic, bass, arp = FP[c]
            b = sec * 16 + i * 4
            s.pad(b, 4, voic, gain=0.07 + 0.03 * sec, bright=0.3 + 0.06 * sec, attack=1.8, release=3.0)
            if sec >= 1:
                s.note(b, A.I_piano, bass.replace("1", "2"), 4, 0.4, gain=0.48, pan=-0.2)
            if sec >= 2:
                s.arp(b, 4, arp, A.I_harp, [0, 1, 2, 3, 4, 5, 4, 2], 0.5, vel=0.3, gain=0.42, pan=-0.3)
                s.choir(b, 4, voic[1:], gain=0.05 + 0.025 * sec, vowel="a", attack=1.6, release=3.0)
    s.pad(80, 4, FP["D"][0], gain=0.2, bright=0.55, attack=1.0, release=6.0)
    # one wick, alone
    s.line(0, A.WICK_A, "D5", A.I_box, 0.55, gain=0.65, pan=0.15)
    s.line(8, A.WICK_C, "D5", A.I_box, 0.5, gain=0.6, pan=0.15)
    # a second wick answers, a third above, a beat behind
    s.line(16, A.WICK_A, "D5", A.I_box, 0.5, gain=0.6, pan=0.25)
    s.line(17, thirds(A.WICK_A, THIRD_MINOR), "D5", A.I_cel, 0.42, gain=0.5, pan=-0.25)
    s.line(24, A.WICK_B, "D5", A.I_box, 0.5, gain=0.6, pan=0.25)
    s.line(24, A.WICK_B, "D4", A.I_cel, 0.42, gain=0.5, pan=-0.25)
    # home: the theme turns major
    s.line(32, A.WICK_MAJ, "D4", A.I_horn, 0.58, gain=0.68, pan=0.1)
    s.line(32, A.WICK_MAJ, "D5", A.I_hum, 0.35, gain=0.3, pan=-0.2)
    s.line(40, A.WICK_MAJ_B, "D4", A.I_horn, 0.58, gain=0.68, pan=0.1)
    s.line(48, A.WICK_MAJ, "D5", A.I_box, 0.5, gain=0.58, pan=0.3)
    s.line(48, A.WICK_MAJ, "D4", A.I_horn, 0.55, gain=0.62, pan=0.0)
    s.line(56, A.WICK_MAJ_B, "D5", A.I_box, 0.48, gain=0.56, pan=0.3)
    s.line(64, A.WICK_MAJ_C, "D5", A.I_box, 0.5, gain=0.58, pan=0.25)
    s.line(64, A.WICK_MAJ_C, "D4", A.I_piano, 0.48, gain=0.62, pan=-0.15)
    s.line(72, [(7, 2), (4, 2), (2, 2), (0, 2)], "D5", A.I_cel, 0.45, gain=0.55, pan=0.2)
    for k, nt in enumerate(["D3", "A3", "D4", "F#4", "A4", "D5", "F#5", "A5"]):
        s.note(80 + k * 0.18, A.I_harp, nt, 6, 0.5, gain=0.5, pan=-0.4 + k * 0.1)
    for b, nt in ((81, "D6"), (82.5, "A5"), (84, "F#5")):
        s.note(b, A.I_glass, nt, 2, 0.35, gain=0.45, pan=0.3)
    s.note(80, lambda n, h, v: S.church_bell(n, 9.0, v), "D3", 1, 0.6, gain=0.18, pan=-0.3)
    out = s.render(3.4, wet=0.45, rms_db=-20)
    n = out.shape[1]
    fade = int(7.0 * SR)
    out[:, n - fade:] *= np.linspace(1, 0, fade) ** 2
    return out


MUSIC = {"echo_lark": music_echo_lark, "echo_maud": music_echo_maud, "echo_vesper": music_echo_vesper,
         "echo_vesper_dark": music_echo_vesper_dark, "hollow_full": music_hollow_full,
         "first_page": music_first_page}


# =============================================================== ambience ===
def gurgle(gain=1.0):
    r = S.rand()
    parts = []
    for _ in range(r.integers(3, 7)):
        k = _n(r.uniform(0.02, 0.05))
        f = r.uniform(160, 420) * (1 + 1.6 * _t(k) / (k / SR))
        parts.append((r.uniform(0, 0.35), np.sin(TAU * np.cumsum(f) / SR) * np.hanning(k) * r.uniform(0.4, 1.0)))
    return S.fft_filter(np.pad(A.mixdown(parts), (0, 256)), S.low_gain(1500, 2)) * gain


def amb_flood():
    S.seed(601)
    T = 32.0
    mx = S.Mix(T)
    n = mx.L
    t = np.arange(n) / SR
    for ch in range(2):
        rush = S.fft_filter(S.noise(n), S.band_gain(120, 1600))
        turb = 0.55 + 0.45 * S.normalize(S.fft_filter(S.noise(n), S.low_gain(1.5, 1)), 1.0)
        mx.buf[ch] += S.normalize(rush * turb, 0.06)
        roar = S.fft_filter(S.noise(n), S.low_gain(180, 2)) * (0.6 + 0.4 * A.lfo(t, T, 4, ch))
        mx.buf[ch] += S.normalize(roar, 0.07)
        mx.buf[ch] += S.normalize(shepard_noise(n, 220.0, 3.0, 4, 4, 0.3), 0.045)   # always rising
    r = S.rand()
    for _ in range(12):
        mx.add(r.uniform(0, T), gurgle(), r.uniform(0.05, 0.1), r.uniform(-0.9, 0.9))
    for _ in range(8):
        mx.add(r.uniform(0, T), A.drip(r.uniform(350, 800)), r.uniform(0.05, 0.1), r.uniform(-0.9, 0.9))
    for _ in range(3):  # stone groaning under the weight of the water
        mx.add(r.uniform(0, T), A.creak(r.uniform(0.8, 1.4), r.uniform(60, 95)), 0.04, r.uniform(-0.8, 0.8))
    buf = S.reverb(mx.buf, S.make_ir(4.0, damp=1.4, predelay=0.04), wet=0.5)
    buf = S.stereo_filter(buf, S.high_gain(30, 2))
    return S.master(buf, -6, -25)


def amb_rootway():
    S.seed(602)
    T = 32.0
    mx = S.Mix(T)
    n = mx.L
    t = np.arange(n) / SR
    hum = (np.sin(TAU * 55 * t) * (0.6 + 0.4 * A.lfo(t, T, 2)) + 0.5 * np.sin(TAU * 82.5 * t + 0.4)
           * A.lfo(t, T, 3, 1.0) + 0.25 * np.sin(TAU * 110 * t + 1.1) * A.lfo(t, T, 4, 2.0))
    mx.add(0, S.normalize(hum, 0.04), 1.0, 0.0)
    warm = np.stack([S.fft_filter(S.pink(n), S.band_gain(60, 500)), S.fft_filter(S.pink(n), S.band_gain(60, 500))])
    mx.buf += warm / np.abs(warm).max() * 0.025
    mx.buf += np.stack([S.normalize(A.crackle(n, 3, 700, 3500, 1.0, 0.08), 0.05),
                        S.normalize(A.crackle(n, 3, 700, 3500, 1.0, 0.08), 0.05)])   # lamps burning
    r = S.rand()
    far = S.low_gain(2600, 2)
    t0 = 0.4
    while t0 < T - 0.5:  # Keepers at work, somewhere down the corridor
        pan = r.uniform(-0.9, 0.9)
        g = r.uniform(0.04, 0.08)
        for k in range(int(r.integers(2, 5))):
            tap = S.fft_filter(np.pad(chisel(r.uniform(2600, 3600)), (0, 256)), far)
            mx.add(t0 + k * r.uniform(0.32, 0.42), tap, g, pan)
        t0 += r.uniform(2.2, 4.0)
    for _ in range(5):  # distant voices: a word, a laugh
        start = r.uniform(0, T)
        pan = r.uniform(-0.8, 0.8)
        for k in range(int(r.integers(3, 7))):
            syl = A.syllable(KEEPER if r.random() < 0.6 else EDDA, int(r.integers(8)))
            syl = S.fft_filter(np.pad(syl, (0, 256)), S.low_gain(1800, 2))
            mx.add(start + k * r.uniform(0.09, 0.14), syl, 0.03, pan)
    for _ in range(3):
        mx.add(r.uniform(0, T), S.thump(90, 55, 0.4, 1.0, 0.1), 0.04, r.uniform(-0.6, 0.6))   # a mallet, far off
    buf = S.reverb(mx.buf, S.make_ir(3.2, damp=1.2, predelay=0.03), wet=0.5)
    buf = S.stereo_filter(buf, S.high_gain(30, 2))
    return S.master(buf, -6, -26)


# ==================================================================== sfx ===
def sfx_bell_ring():
    x = A.mixdown([(0, handbell("G5", 1.7, 0.9)), (0.004, handbell("G6", 0.6, 0.15))])
    return S.normalize(A.with_reverb(x, 1.2, 0.3), 0.42)


def sfx_keeper_wake():
    hn = _n(0.24)
    ks = np.arange(1, 9)
    rise = 1 + 0.22 * (_t(hn) / 0.24) ** 2    # "mm?" - a hum that lifts into a question
    hum = S.additive(330, hn, ks, S.formant_gain(ks * 330.0, S.VOWELS["u"], 1.3) / ks ** 1.2, [None] * 8,
                     attack=0.01, vib=rise)
    hum *= S.ramp_env(hn, 0.03, 0.07)
    ding = A.mixdown([(0, fo(S.music_box(m("B5"), 0.9, 0.5))), (0.07, fo(S.music_box(m("E6"), 1.0, 0.45)))])
    x = A.mixdown([(0, S.normalize(hum, 0.5)), (0.2, ding * 0.7)])
    return S.normalize(A.with_reverb(x, 0.8, 0.25), 0.32)


def sfx_memory_in():
    ch = A.mixdown([(0, fo(S.glass(m(nt), 1.3, 0.5), 0.5)) for nt in ("D5", "A5", "E6", "F6")])
    rev = A.with_reverb(ch, 0.6, 0.6)[::-1].copy()                    # the past arriving backwards
    sw = S.normalize(A.sweep_noise(2.0, 500, 5000, 0.5, 0.85, 0.15), 0.18)
    pad = sum(S.pad(nt, 1.6, 0.5, attack=1.3, release=0.6, bright=0.4) for nt in ("D4", "A4", "E5"))
    bloom = A.mixdown([(0, fo(S.glass(m("D6"), 1.4, 0.5), 0.6)), (0.05, fo(S.music_box(m("A6"), 1.2, 0.35)))])
    x = A.mixdown([(0, S.normalize(rev, 0.45)), (0, sw), (0, S.normalize(pad, 0.3)), (len(rev) / SR - 0.05, bloom)])
    return S.normalize(A.with_reverb(x, 1.6, 0.35), 0.42)


def sfx_memory_out():
    bloom = A.mixdown([(0, fo(S.glass(m("A5"), 2.0, 0.5), 0.8)), (0.04, fo(S.glass(m("E6"), 1.8, 0.35), 0.8))])
    fall = A.mixdown([(0.25 + k * 0.16, fo(S.glass(m(nt), 1.4, 0.35 - k * 0.05), 0.6))
                      for k, nt in enumerate(["F6", "E6", "A5", "D5"])])
    sw = S.normalize(A.sweep_noise(1.6, 4500, 400, 0.5, 0.1, 0.85), 0.18)
    pad = sum(S.pad(nt, 0.4, 0.5, attack=0.1, release=1.4, bright=0.35) for nt in ("D4", "A4"))
    x = A.mixdown([(0, bloom), (0, fall), (0.05, sw), (0, S.normalize(pad, 0.25))])
    return S.normalize(A.with_reverb(x, 1.6, 0.35), 0.38)


def sfx_keepsake():
    pad = sum(S.pad(nt, 0.9, 0.5, attack=0.25, release=1.0, bright=0.4) for nt in ("D3", "A3", "F#4"))
    bell = fo(S.church_bell("D4", 2.4, 0.5), 1.0)
    mot = A.mixdown([(0.12 + k * 0.2, fo(S.celesta(m(nt), 1.6, 0.55 - k * 0.06), 0.5))
                     for k, nt in enumerate(["A5", "F#5", "D5"])])
    sh = A.mixdown([(0.7, fo(S.glass(m("A6"), 1.6, 0.25), 0.7))])
    x = A.mixdown([(0, S.normalize(pad, 0.4)), (0, S.normalize(bell, 0.3)), (0, mot), (0, sh)])
    return S.normalize(A.with_reverb(x, 2.0, 0.35), 0.45)


def sfx_fear_beat():
    lub = S.thump(64, 38, 0.32, 1.0, 0.07)
    dub = S.thump(58, 36, 0.32, 0.7, 0.06)
    x = A.mixdown([(0, lub), (0.24, dub)])
    x = S.fft_filter(np.pad(x, (0, 512)), S.low_gain(160, 2))     # muffled, from inside
    return S.normalize(A.with_reverb(x, 0.6, 0.15, 1.6), 0.45)


def sfx_dark_rise():
    n = _n(1.5)
    sw = S.normalize(A.sweep_noise(1.5, 140, 650, 0.45, 0.55, 0.4), 0.55)
    drone = (np.sin(TAU * 44 * _t(n)) + 0.6 * np.sin(TAU * 46.5 * _t(n))) * S.ramp_env(n, 0.6, 0.6)
    wh = A.whisper(1.4)
    wh = S.fft_filter(wh, S.band_gain(300, 3000)) * S.ramp_env(len(wh), 0.4, 0.6)
    x = A.mixdown([(0, sw), (0, S.normalize(drone, 0.35)), (0.05, S.normalize(wh, 0.12))])
    return S.normalize(A.with_reverb(x, 1.6, 0.4, 1.4), 0.45)


def sfx_carve():
    r = S.rand()
    parts = []
    for k, o in enumerate((0.0, 0.28, 0.5)):
        parts.append((o, chisel(r.uniform(2900, 3500), 1.0 if k < 2 else 1.15)))
    n = _n(0.9)
    grit = S.fft_filter(S.noise(n), S.band_gain(2500, 8000)) * np.exp(-_t(n) / 0.25)   # stone dust
    parts.append((0.52, S.normalize(grit, 0.06)))
    return S.normalize(A.with_reverb(A.mixdown(parts), 0.9, 0.25), 0.5)


def sfx_supper():
    pad = sum(S.pad(nt, 0.7, 0.5, attack=0.2, release=1.0, bright=0.35) for nt in ("D3", "F#3", "A3", "D4"))
    roll = A.mixdown([(k * 0.06, fo(S.harp(m(nt), 1.6, 0.45), 0.6)) for k, nt in enumerate(["D4", "F#4", "A4", "D5"])])
    clink = A.mixdown([(0.0, A.metal_clink(3700, 0.6)), (0.09, A.metal_clink(4300, 0.45))])
    x = A.mixdown([(0, S.normalize(pad, 0.35)), (0.02, S.normalize(roll, 0.4)), (0.45, clink * 0.5)])
    return S.normalize(A.with_reverb(x, 1.2, 0.25), 0.48)


SFX = {k[4:]: v for k, v in globals().items() if k.startswith("sfx_") and callable(v)}


# ================================================================= voices ===
# same fields as audio.VOICES
LARK = dict(f0=196, k=1.1, tilt=1.05, dur=(0.075, 0.1), vib=(5.0, 0.01), breath=0.35, glide=0.06,
            vowels="ae@io", cons=["", "h", "t", "m"], fx=None, peak=0.38, attack=0.012)
MAUD = dict(f0=222, k=1.12, tilt=1.1, dur=(0.09, 0.12), vib=(5.0, 0.016), breath=0.16, glide=0.04,
            vowels="oae@", cons=["m", "", "h", "t"], fx=None, peak=0.4)
VESPER = dict(f0=262, k=1.24, tilt=1.3, dur=(0.07, 0.1), vib=(0, 0), breath=0.5, glide=-0.07,
              vowels="e@io", cons=["", "h", "", "s"], fx=None, peak=0.34, attack=0.02)
EDDA = dict(f0=168, k=1.07, tilt=1.15, dur=(0.11, 0.15), vib=(5.5, 0.035), breath=0.3, glide=-0.03,
            vowels="o@ae", cons=["h", "m", "", "t"], fx=None, peak=0.4)
KEEPER = dict(f0=380, k=1.4, tilt=1.1, dur=(0.05, 0.07), vib=(0, 0), breath=0.12, glide=0.14,
              vowels="ieao", cons=["t", "p", "", "k"], fx=None, peak=0.34)
GLIM = dict(f0=340, k=1.36, tilt=1.5, dur=(0.09, 0.12), vib=(4.5, 0.015), breath=0.16, glide=0.1,
            vowels="oua", cons=["", "m", "b"], fx="singsong", peak=0.34)


def lark_syllable(idx):
    return A.syllable(LARK, idx)


def maud_syllable(idx):
    x = A.syllable(MAUD, idx)
    # warmth: a little chest resonance, the edge taken off
    body = S.fft_filter(np.pad(x, (0, 128)), S.band_gain(180, 700))
    x = S.fft_filter(np.pad(x, (0, 128)), S.low_gain(4200, 1)) + 0.35 * body
    return S.normalize(x, MAUD["peak"])


def vesper_syllable(idx):
    x = A.syllable(VESPER, idx)
    if idx in (1, 4, 6):
        # hesitant: a tiny false start before the word ("h- hello")
        k = min(len(x) // 3, _n(0.028))
        start = x[:k] * np.linspace(1.0, 0.0, k) ** 2 * 0.6
        x = np.concatenate([start, np.zeros(_n(0.04)), x])
    return S.normalize(S.fft_filter(np.pad(x, (0, 128)), S.low_gain(5000, 1)), VESPER["peak"])


def edda_syllable(idx):
    r = S.rand()
    x = A.syllable(EDDA, idx)
    n = len(x)
    t = _t(n)
    # an old voice: a light creak at the end of some syllables
    jit = S.normalize(S.fft_filter(r.standard_normal(n), S.low_gain(30, 1)), 1.0)
    ph = TAU * np.cumsum(r.uniform(40, 55) * (1 + 0.3 * jit)) / SR
    pulses = (0.5 + 0.5 * np.cos(ph)) ** 4
    w = np.clip((t / (n / SR) - 0.55) / 0.45, 0, 1) * (0.6 if idx % 2 == 0 else 0.25)
    x = x * (1 - 0.5 * w + 0.5 * w * pulses)
    return S.normalize(S.fft_filter(np.pad(x, (0, 128)), S.low_gain(4200, 1)), EDDA["peak"])


def keeper_syllable(idx):
    return A.syllable(KEEPER, idx)


def glim_syllable(idx):
    r = S.rand()
    x = A.syllable(GLIM, idx)
    y = np.concatenate([x, np.zeros(_n(0.05))])
    for _ in range(int(r.integers(1, 3))):  # a soft bubble or two
        p = _n(r.uniform(0.0, len(x) / SR))
        bn = _n(0.022)
        f = r.uniform(420, 760) * (1 + 1.8 * _t(bn) / 0.022)
        bub = np.sin(TAU * np.cumsum(f) / SR) * np.hanning(bn) * np.abs(x).max() * 0.35
        y[p:p + bn] += bub[:len(y[p:p + bn])]
    return S.normalize(S.fft_filter(y, S.low_gain(3600, 2)), GLIM["peak"])


VOICES = {"lark": lark_syllable, "maud": maud_syllable, "vesper": vesper_syllable, "edda": edda_syllable,
          "keeper": keeper_syllable, "glim": glim_syllable}


# ================================================================= output ===
def main(argv):
    groups = {"music": MUSIC, "ambience": {"flood": amb_flood, "rootway": amb_rootway}, "sfx": SFX,
              "voice": VOICES}
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
            print("wrote", rows[-1][0], flush=True)
    print(f"{'id':28s} {'sec':>7s} {'peak dB':>8s} {'rms dB':>7s} {'seam':>6s} {'KB':>7s}")
    for name, path in rows:
        sec, peak, rms, seam, size = A.stats(path)
        print(f"{name:28s} {sec:7.2f} {S.db(peak):8.1f} {S.db(rms):7.1f} {seam:6.2f} {size / 1024:7.0f}")


if __name__ == "__main__":
    main(sys.argv[1:])
