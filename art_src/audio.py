"""Every sound in Lantern Wanderer, synthesized from scratch (see synth.py).

    python audio.py              # everything
    python audio.py music        # one group: music | ambience | sfx | voice
    python audio.py music title  # single ids

Outputs (assets/audio/):
  music/<id>.ogg     stereo 32 kHz Vorbis, seamless loops (except `ending`)
                     title mossgrave hollow_cold hollow glimmerdeep drowned
                     rootdark chase hearth ending
  ambience/<id>.ogg  stereo seamless loops: forest hollow cave water roots hearth
  sfx/<id>.wav       mono 16-bit one-shots (see SFX below)
  voice/<id>_<n>.wav mono 16-bit gibberish syllables, 8 per character (see VOICES)

Every track is built around one motif, the "Wick theme" (WICK_A/B/C below):
D F A G F E D, answered by a hopeful dorian lift D F A B C B A.
"""
import math
import os
import sys

import numpy as np
import soundfile as sf

import synth as S
from synth import SR, TAU, m

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")

# ------------------------------------------------------------ the theme ---
# (semitones above the tonic, length in beats); None = rest
WICK_A = [(0, 1), (3, 1), (7, 1.5), (5, 0.5), (3, 1), (2, 1), (0, 2)]       # D F A G F E D
WICK_B = [(0, 1), (3, 1), (7, 1), (9, 1), (10, 1), (9, 1), (7, 2)]          # D F A B C B A
WICK_B_FLAT = [(0, 1), (3, 1), (7, 1), (8, 1), (10, 1), (8, 1), (7, 2)]     # D F A Bb C Bb A
WICK_C = [(7, 1), (5, 1), (3, 1.5), (2, 0.5), (0, 4)]                       # A G F E D (resolve)
WICK_MAJ = [(0, 1), (4, 1), (7, 1.5), (5, 0.5), (4, 1), (2, 1), (0, 2)]     # D F# A G F# E D
WICK_MAJ_B = [(0, 1), (4, 1), (7, 1), (9, 1), (11, 1), (9, 1), (7, 2)]
WICK_MAJ_C = [(7, 1), (5, 1), (4, 1.5), (2, 0.5), (0, 4)]


# ------------------------------------------------------------ instruments ---
def I_harp(n, h, v):
    return S.harp(n, max(2.2, h + 1.6), v)


def I_kal(n, h, v):
    return S.kalimba(n, max(1.8, h + 1.2), v)


def I_box(n, h, v):
    return S.music_box(n, max(2.2, h + 1.4), v)


def I_glass(n, h, v):
    return S.glass(n, max(3.5, h + 2.5), v)


def I_cel(n, h, v):
    return S.celesta(n, max(2.2, h + 1.4), v)


def I_piano(n, h, v):
    return S.piano(n, max(3.0, h + 1.8), v, hold=h + 0.05)


def I_lute(n, h, v):
    return S.lute(n, max(1.8, h + 1.0), v)


def I_mute(n, h, v):
    return S.lute(n, 0.55, v, mute=True)


def I_reed(n, h, v):
    return S.reed(n, h * 0.96, v)


def I_horn(n, h, v):
    return S.horn(n, h * 0.97, v)


def I_cello(n, h, v):
    return S.cello(n, h * 0.98, v)


def I_hum(n, h, v):
    return S.choir(n, h * 0.98, v, vowel="o", voices=1, attack=0.25, release=0.7)


# ------------------------------------------------------------------ song ---
class Song:
    def __init__(self, bpm, beats, loop=True, tail=0.0, sd=0):
        S.seed(sd)
        self.spb = 60.0 / bpm
        self.beats = beats
        self.loop = loop
        self.mix = S.Mix(beats * self.spb, loop=loop, tail=tail)

    def put(self, beat, mono, gain=1.0, pan=0.0, hum=0.007):
        t = beat * self.spb + (S.rand().uniform(-hum, hum) if hum else 0.0)
        if not self.loop:
            t = max(0.0, t)
        self.mix.add(t, mono, gain, pan)

    def note(self, beat, fn, note, beats=1.0, vel=0.7, gain=1.0, pan=0.0, hum=0.007):
        self.put(beat, fn(m(note), beats * self.spb, vel), gain, pan, hum)

    def line(self, beat, seq, root, fn, vel=0.7, gain=1.0, pan=0.0, scale=1.0, legato=1.0, accent=0.12):
        b = beat
        for i, (off, d) in enumerate(seq):
            d *= scale
            if off is not None:
                v = vel * (1.0 + (accent if i == 0 else 0.0)) * S.rand().uniform(0.92, 1.05)
                self.put(b, fn(m(root) + off, d * self.spb * legato, v), gain, pan)
            b += d
        return b

    def pad(self, beat, beats, notes, gain=0.25, bright=0.45, attack=1.2, release=1.8, width=0.5):
        for i, nt in enumerate(notes):
            pan = (i / max(1, len(notes) - 1) - 0.5) * 2 * width
            x = S.pad(nt, beats * self.spb, 1.0, attack=attack, release=release, bright=bright)
            self.put(beat, x, gain, pan, hum=0)

    def choir(self, beat, beats, notes, gain=0.25, vowel="u", attack=1.0, release=1.8, width=0.6):
        for i, nt in enumerate(notes):
            pan = (i / max(1, len(notes) - 1) - 0.5) * 2 * width
            x = S.choir(nt, beats * self.spb, 1.0, vowel=vowel, attack=attack, release=release)
            self.put(beat, x, gain, pan, hum=0)

    def arp(self, beat, beats, notes, fn, pattern, step=0.5, vel=0.5, gain=1.0, pan=0.0, accent=0.25):
        k = 0
        b = beat
        while b < beat + beats - 1e-6:
            idx = pattern[k % len(pattern)]
            v = vel * (1 + accent if k % int(round(4 / step)) == 0 else 1.0) * S.rand().uniform(0.85, 1.08)
            self.put(b, fn(m(notes[idx]), step * self.spb, v), gain, pan)
            b += step
            k += 1

    def render(self, ir_seconds=3.0, wet=0.35, damp=1.0, predelay=0.02, lowpass=None, peak_db=-3.0, rms_db=-21.0):
        buf = self.mix.buf
        if lowpass:
            buf = S.stereo_filter(buf, S.low_gain(lowpass, 2))
        ir = S.make_ir(ir_seconds, predelay=predelay, damp=damp)
        buf = S.reverb(buf, ir, wet=wet, loop=self.loop)
        buf = S.stereo_filter(buf, S.high_gain(28, 2))  # no DC / sub rumble
        return S.master(buf, peak_db, rms_db)


def root_of(chord):
    return chord[0]


# ================================================================== music ===
CH = {  # pad voicings around D3..A4
    "Dm": ["D3", "A3", "D4", "F4"], "Bb": ["Bb2", "F3", "D4", "F4"], "F": ["F3", "C4", "F4", "A4"],
    "C": ["C3", "G3", "E4", "G4"], "G": ["G2", "D3", "B3", "D4"], "Am": ["A2", "E3", "C4", "E4"],
    "Gm": ["G2", "D3", "Bb3", "D4"], "A": ["A2", "E3", "C#4", "E4"], "D": ["D3", "A3", "D4", "F#4"],
    "Bm": ["B2", "F#3", "D4", "F#4"], "Em": ["E3", "B3", "E4", "G4"], "D/F#": ["F#2", "A3", "D4", "F#4"],
}
BASS = {"Dm": "D2", "Bb": "Bb1", "F": "F2", "C": "C2", "G": "G1", "Am": "A1", "Gm": "G1", "A": "A1",
        "D": "D2", "Bm": "B1", "Em": "E2", "D/F#": "F#1"}


def music_title():
    s = Song(66, 80, sd=101)
    prog = ["Dm", "Bb"] + ["Dm", "Bb", "F", "C"] + ["Dm", "G", "Am", "C"] + ["Bb", "F", "Gm", "A"] \
        + ["Dm", "Bb", "Gm", "A"] + ["Dm", "Dm"]
    for i, c in enumerate(prog):
        s.pad(i * 4, 4, CH[c], gain=0.16, bright=0.35, attack=1.6, release=2.2)
        s.note(i * 4, I_piano, BASS[c].replace("1", "2") if c != "Bb" else "Bb1", 4, 0.45, gain=0.5)
    for b, nt in ((2, "A5"), (4, "D6"), (6, "F5")):
        s.note(b, I_box, nt, 2, 0.5, gain=0.55, pan=0.2)
    s.line(8, WICK_A, "D5", I_box, 0.62, gain=0.7, pan=0.15)
    s.line(16, WICK_B, "D5", I_box, 0.58, gain=0.7, pan=0.15)
    s.line(24, WICK_A, "D4", I_piano, 0.55, gain=0.8, pan=-0.15)
    s.line(32, WICK_B, "D5", I_box, 0.55, gain=0.65, pan=0.2)
    fall = {"Bb": ["F6", "D6", "Bb5", "F5"], "F": ["C6", "A5", "F5", "C5"], "Gm": ["D6", "Bb5", "G5", "D5"],
            "A": ["E6", "C#6", "A5", "E5"]}
    for i, c in enumerate(["Bb", "F", "Gm", "A"]):
        for k, nt in enumerate(fall[c]):
            s.note(40 + i * 4 + k, I_box, nt, 1, 0.42 - k * 0.05, gain=0.6, pan=0.25)
    s.line(56, WICK_A, "D5", I_box, 0.55, gain=0.55, pan=0.25)
    s.line(56, WICK_A, "D4", I_piano, 0.5, gain=0.7, pan=-0.2)
    s.line(64, WICK_C, "D5", I_box, 0.55, gain=0.55, pan=0.25)
    s.line(64, WICK_C, "D4", I_piano, 0.48, gain=0.7, pan=-0.2)
    for b, nt in ((72, "D6"), (74, "A5"), (76, "F5"), (78, "D5")):
        s.note(b, I_box, nt, 2, 0.45, gain=0.55, pan=0.2)
    return s.render(3.2, wet=0.45)


def music_mossgrave():
    s = Song(70, 96, sd=102)
    p1, p2 = ["Dm", "G", "Dm", "C"], ["Bb", "C", "Am", "Dm"]
    prog = p1 + p1 + p2 + p1 + p2 + p1
    voic = {"Dm": ["D3", "A3", "D4", "E4", "F4", "A4"], "G": ["G2", "D3", "B3", "D4", "E4", "G4"],
            "C": ["C3", "G3", "C4", "D4", "E4", "G4"], "Bb": ["Bb2", "F3", "Bb3", "C4", "D4", "F4"],
            "Am": ["A2", "E3", "A3", "B3", "C4", "E4"]}
    for i, c in enumerate(prog):
        b = i * 4
        s.pad(b, 4, CH[c], gain=0.11, bright=0.4, attack=1.4, release=2.0)
        s.arp(b, 4, voic[c], I_harp, [0, 1, 2, 3, 4, 5, 4, 2], 0.5, vel=0.42, gain=0.55, pan=-0.25)
        s.note(b, I_harp, BASS[c].replace("1", "2"), 4, 0.6, gain=0.5, pan=-0.1)
    s.line(16, WICK_A, "D5", I_kal, 0.7, gain=0.75, pan=0.3)
    s.line(24, WICK_B, "D5", I_kal, 0.66, gain=0.75, pan=0.3)
    s.line(48, WICK_A, "D5", I_kal, 0.66, gain=0.72, pan=0.32)
    s.line(48, WICK_A, "D6", I_box, 0.3, gain=0.35, pan=0.5)
    s.line(56, WICK_C, "D5", I_kal, 0.62, gain=0.72, pan=0.32)
    for b, nt in ((80, "D5"), (82, "F5"), (84, "A5"), (86.5, "G5")):
        s.note(b, I_kal, nt, 1.5, 0.55, gain=0.7, pan=0.3)
    r = S.rand()
    tw = ["D6", "E6", "F6", "A6", "C7", "D7"]
    for _ in range(16):  # fireflies
        s.note(r.uniform(0, 96), I_box, tw[r.integers(len(tw))], 1, r.uniform(0.15, 0.3), gain=0.35,
               pan=r.uniform(-0.8, 0.8))
    return s.render(2.8, wet=0.38)


def music_hollow_cold():
    s = Song(60, 64, sd=103)
    chords = [["D3", "A3", "E4", "F4"], ["Bb2", "F3", "A3", "D4"], ["G2", "D3", "A3", "Bb3"], ["A2", "E3", "A3", "D4"]]
    for i, c in enumerate(chords):
        s.pad(i * 16, 16, c, gain=0.13, bright=0.15, attack=4.0, release=4.0)
    # cold wind bed
    n = s.mix.L
    t = np.arange(n) / SR
    T = n / SR
    for ch in range(2):
        w = S.pink(n)
        center = 650 + 260 * np.sin(TAU * 3 * t / T + ch) + 120 * np.sin(TAU * 7 * t / T)
        w = S.tv_filter(w, lambda f, tt: 1.0 / (1.0 + ((f - np.interp(tt % T, t, center)) / 260.0) ** 2), 2048)
        amp = 0.55 + 0.45 * (0.5 + 0.5 * np.sin(TAU * 2 * t / T + 1.3 + ch))
        s.mix.buf[ch] += S.normalize(w * amp, 0.06)
    plucks = [(2, "A4"), (5, "D5"), (9, "F5"), (12, "E5"), (14.5, "D5"), (20, "Bb4"), (23, "F5"), (28, "A5"),
              (30, "G5"), (36, "D5"), (38.5, "F5"), (40, "A5"), (44, "G5"), (47, "E5"), (52, "C#5"),
              (56, "E5"), (60, "A4")]
    for b, nt in plucks:
        s.note(b, I_harp, nt, 2, 0.5, gain=0.6, pan=S.rand().uniform(-0.4, 0.4))
    s.note(32, I_glass, "D6", 4, 0.3, gain=0.4, pan=0.5)
    return s.render(4.0, wet=0.5, rms_db=-24)


def music_hollow():
    s = Song(96, 144, sd=104)  # 48 bars of 3/4
    verse = ["Dm", "Gm", "C", "F", "Bb", "Gm", "A7", "Dm"]
    bridge = ["F", "C", "Dm", "A", "Bb", "F", "Gm", "A"]
    form = [verse, verse, verse, bridge, verse, verse]
    bass = {"Dm": "D3", "Gm": "G2", "C": "C3", "F": "F2", "Bb": "Bb2", "A7": "A2", "A": "A2"}
    tri = {"Dm": ["F3", "A3", "D4"], "Gm": ["G3", "Bb3", "D4"], "C": ["G3", "C4", "E4"], "F": ["F3", "A3", "C4"],
           "Bb": ["F3", "Bb3", "D4"], "A7": ["G3", "C#4", "E4"], "A": ["E3", "A3", "C#4"]}
    mel = [[("D5", 1), ("F5", 1), ("A5", 1)], [("G5", 2), ("F5", 1)], [("E5", 2), ("G5", 1)], [("F5", 3)],
           [("D5", 1), ("F5", 1), ("Bb5", 1)], [("A5", 2), ("G5", 1)], [("E5", 1), ("G5", 1), ("C#5", 1)],
           [("D5", 3)]]
    bmel = [[("A4", 3)], [("G4", 3)], [("F4", 3)], [("E4", 3)], [("D5", 2), ("C5", 1)], [("A4", 3)],
            [("Bb4", 2), ("A4", 1)], [("A4", 1), ("C#5", 1), ("E5", 1)]]
    for sec, prog in enumerate(form):
        for i, c in enumerate(prog):
            bar = sec * 8 + i
            b = bar * 3
            soft = 0.75 if sec in (0, 5) else 1.0
            s.note(b, I_lute, bass[c], 1, 0.62 * soft, gain=0.75, pan=-0.15)
            for beat in (1, 2):
                for k, nt in enumerate(tri[c]):
                    s.put(b + beat + k * 0.03, I_lute(m(nt), 0.5 * s.spb, 0.36 * soft), 0.6, 0.1 + k * 0.08, hum=0.004)
            if sec in (1, 2, 3, 4):
                for k, nt in enumerate(tri[c]):
                    s.put(b, S.reed(m(nt), 3 * s.spb, 0.32), 0.38, -0.4 + k * 0.4, hum=0)
            if sec in (1, 4):
                bb = b
                for nt, d in mel[i]:
                    s.note(bb, I_reed, nt, d, 0.62, gain=0.62, pan=0.2)
                    if sec == 4:
                        s.note(bb, I_box, m(nt) + 12, d, 0.38, gain=0.4, pan=0.45)
                    bb += d
            elif sec == 2:
                bb = b
                for nt, d in mel[i]:
                    s.note(bb, I_box, m(nt) + 12, d, 0.5, gain=0.55, pan=0.35)
                    s.note(bb, I_reed, m(nt) - (4 if nt[0] in "AEB" else 3), d, 0.4, gain=0.4, pan=-0.2)
                    bb += d
            elif sec == 3:
                bb = b
                for nt, d in bmel[i]:
                    s.note(bb, I_reed, nt, d, 0.55, gain=0.6, pan=0.2)
                    bb += d
            elif sec == 5 and i in (0, 2, 4, 6):
                s.note(b, I_box, ["F5", "E5", "D5", "C#5"][i // 2], 3, 0.4, gain=0.45, pan=0.35)
    return s.render(1.8, wet=0.28, damp=1.2)


def music_glimmerdeep():
    s = Song(54, 64, sd=105)
    chords = [("Dm9", ["D3", "A3", "E4", "F4"], ["A5", "E6", "F5", "D6", "C6"]),
              ("E/D", ["D3", "G#3", "B3", "E4"], ["G#5", "B5", "E6", "D6", "F#6"]),
              ("Dm9", ["D3", "A3", "E4", "F4"], ["E6", "A5", "D6", "F6", "C6"]),
              ("Bbmaj7", ["Bb2", "F3", "A3", "E4"], ["A5", "D6", "E6", "F6", "Bb5"]),
              ("Dm9", ["D3", "A3", "E4", "F4"], ["D6", "F6", "A5", "E6", "C6"]),
              ("E/D", ["D3", "G#3", "B3", "E4"], ["E6", "G#6", "B5", "D6", "F#6"]),
              ("Gm9", ["G2", "D3", "A3", "Bb3"], ["Bb5", "D6", "A5", "F6", "G5"]),
              ("Asus", ["A2", "E3", "A3", "D4"], ["E6", "A5", "D6", "B5", "E5"])]
    for i, (_, voic, bells) in enumerate(chords):
        b = i * 8
        s.pad(b, 8, voic, gain=0.13, bright=0.25, attack=3.0, release=3.5)
        s.pad(b, 8, [voic[0]], gain=0.12, bright=0.0, attack=3.0, release=3.5)
        offs = [0, 1.5, 3, 4.5, 6] if i % 2 == 0 else [0.5, 2, 3.5, 5.5]
        for k, o in enumerate(offs):
            if i in (4, 6) and o >= 3:
                continue  # leave room for the celesta theme
            s.note(b + o, I_glass, bells[k % len(bells)], 2, S.rand().uniform(0.3, 0.45), gain=0.5,
                   pan=S.rand().uniform(-0.6, 0.6))
    s.line(32, WICK_A, "D5", I_cel, 0.6, gain=0.7, pan=0.1)
    s.line(48, [(0, 1), (3, 1), (7, 2), (5, 4)], "D5", I_cel, 0.55, gain=0.65, pan=-0.1)
    r = S.rand()
    for _ in range(24):
        s.note(r.uniform(0, 64), I_glass, ["D7", "E7", "A6", "F6", "C7"][r.integers(5)], 1,
               r.uniform(0.1, 0.22), gain=0.25, pan=r.uniform(-0.9, 0.9))
    return s.render(5.5, wet=0.6, damp=0.9, predelay=0.04, rms_db=-22)


def music_drowned():
    s = Song(50, 64, sd=106)
    chords = [["C3", "G3", "Eb4", "G4"], ["Ab2", "Eb3", "C4", "Eb4"], ["F2", "C3", "Ab3", "C4"],
              ["G2", "D3", "C4", "D4"], ["C3", "G3", "Eb4", "G4"], ["Ab2", "Eb3", "C4", "Eb4"],
              ["Bb2", "F3", "D4", "F4"], ["G2", "D3", "B3", "D4"]]
    for i, c in enumerate(chords):
        s.choir(i * 8, 8, c, gain=0.2, vowel="u" if i % 2 == 0 else "o", attack=2.4, release=3.0)
    s.pad(0, 32, ["C2"], gain=0.2, bright=0.0, attack=6, release=6)
    s.pad(32, 32, ["C2"], gain=0.2, bright=0.0, attack=6, release=6)
    for b, nt, g in ((0, "C3", 0.4), (16, "G3", 0.22), (32, "C3", 0.4), (48, "G3", 0.22), (56, "Eb4", 0.12)):
        s.note(b, lambda n, h, v: S.church_bell(n, 9.0, v), nt, 1, 0.8, gain=g, pan=-0.3)
    s.line(16, WICK_A, "C4", I_hum, 0.6, gain=0.55, pan=0.15)
    s.line(36, [(0, 1), (3, 1), (7, 1), (9, 1), (10, 1), (9, 1), (7, 2)], "C4", I_hum, 0.55, gain=0.5, pan=0.15)
    r = S.rand()
    for _ in range(9):
        s.note(r.uniform(0, 64), I_box, ["G5", "C6", "Eb6", "D6", "Bb5"][r.integers(5)], 1, 0.25, gain=0.35,
               pan=r.uniform(-0.7, 0.7))
    return s.render(6.0, wet=0.55, damp=1.6, predelay=0.05, lowpass=1600, rms_db=-22)


def creak(dur=0.9, f0=140.0, gain=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    r = S.rand()
    wob = 1 + 0.12 * np.sin(TAU * r.uniform(0.6, 1.4) * t + r.uniform(0, TAU)) + 0.05 * np.sin(TAU * 3.1 * t)
    ks = np.arange(1, 16)
    x = S.additive(f0, n, ks, 1.0 / ks, [None] * 15, attack=0, vib=wob)
    stick = 0.5 + 0.5 * np.sign(np.sin(TAU * np.cumsum(r.uniform(18, 32) * wob) / SR))
    x = S.fft_filter(x * stick, S.band_gain(250, 1800))
    return S.normalize(x * S.ramp_env(n, 0.12, 0.25), 0.5) * gain


def music_rootdark():
    s = Song(56, 64, sd=107)
    for b in (0, 16, 32, 48):
        s.pad(b - 2, 20, ["A1", "E2"], gain=0.3, bright=0.1, attack=4.0, release=4.0, width=0.3)
    s.pad(0, 32, ["A3", "C4", "E4", "B4"], gain=0.05, bright=0.3, attack=6, release=6)
    s.pad(32, 32, ["A3", "C4", "E4", "B4"], gain=0.05, bright=0.3, attack=6, release=6)
    for k in range(32):
        b = k * 2
        g = 0.55 if b < 48 else 0.32
        s.put(b, S.thump(58, 36, 0.5, 1.0), g, 0.0, hum=0)
        s.put(b + 0.3 / s.spb, S.thump(52, 34, 0.45, 0.6), g, 0.0, hum=0)
    r = S.rand()
    for _ in range(8):
        s.put(r.uniform(0, 64), creak(r.uniform(0.6, 1.2), r.uniform(110, 190)), 0.12, r.uniform(-0.8, 0.8), hum=0)
    s.line(16, WICK_A, "A2", I_cello, 0.62, gain=0.75, pan=-0.1, scale=2.0, legato=0.98)
    s.line(44, [(0, 1), (3, 1), (7, 1), (9, 1), (10, 1), (9, 1), (7, 2)], "A2", I_cello, 0.55, gain=0.7,
           pan=-0.1, scale=1.25)
    return s.render(4.5, wet=0.42, damp=1.3, lowpass=6000, rms_db=-21)


def music_chase():
    s = Song(92, 96, sd=108)
    prog = ["Dm", "Bb", "Gm", "A"] * 6
    roots = {"Dm": "D3", "Bb": "Bb2", "Gm": "G2", "A": "A2"}
    pat = [0, 7, 12, 7, 0, 7, 12, 14]
    for i, c in enumerate(prog):
        b = i * 4
        phrase = (i % 4)
        s.pad(b, 4, CH[c], gain=0.1 + 0.03 * phrase, bright=0.45 + 0.1 * phrase, attack=0.6, release=1.0)
        for k, o in enumerate(pat):
            s.put(b + k * 0.5, I_mute(m(roots[c]) + o, 0.3, 0.55 if k % 2 == 0 else 0.42), 0.7, -0.2, hum=0.003)
        for q in range(4):
            s.put(b + q, S.thump(64, 40, 0.35, 1.0, 0.12), 0.45 if q == 0 else 0.25, 0.0, hum=0)
            sh = S.fft_filter(S.noise(int(0.04 * SR)), S.high_gain(5000)) * np.exp(-np.arange(int(0.04 * SR)) / (0.008 * SR))
            s.put(b + q + 0.5, sh, 0.05, 0.4, hum=0)
        if 32 <= b < 64:
            s.note(b, I_cello, BASS[c].replace("1", "2"), 4, 0.5, gain=0.45, pan=-0.3)
    s.line(32, [(o, 1) for o, _ in WICK_A], "D5", I_glass, 0.5, gain=0.5, pan=0.3)
    s.line(64, [(o, 1) for o, _ in WICK_A], "D6", I_glass, 0.35, gain=0.4, pan=0.4)
    s.line(72, [(o, 1) for o, _ in WICK_B_FLAT], "D6", I_glass, 0.35, gain=0.4, pan=0.4)
    return s.render(2.4, wet=0.25, rms_db=-20)


def crackle(n, rate=6.0, lo=1000, hi=5000, gain=1.0, pops=0.06):
    r = S.rand()
    x = np.zeros(n)
    count = int(rate * n / SR)
    for _ in range(count):
        p = r.integers(n)
        ln = int(r.uniform(0.001, 0.006) * SR)
        burst = r.standard_normal(ln) * np.exp(-np.arange(ln) / (ln / 3)) * r.exponential(0.5)
        if r.random() < pops:
            burst *= 3.0
        idx = (p + np.arange(ln)) % n
        x[idx] += burst
    return S.fft_filter(x, S.band_gain(lo, hi)) * gain


def music_hearth():
    s = Song(60, 80, sd=109)
    prog = ["Dm", "Bb", "Gm", "A", "F", "C", "Bb", "A", "Dm", "D"]
    for i, c in enumerate(prog):
        b = i * 8
        rise = 0.7 + 0.3 * (i / 9)
        s.pad(b, 8, CH[c], gain=0.13 * rise, bright=0.55, attack=2.0, release=2.6)
        s.choir(b, 8, CH[c][1:], gain=0.12 * rise, vowel="a" if i % 2 else "o", attack=2.0, release=2.6)
        s.note(b, I_cello, BASS[c].replace("1", "2"), 8, 0.5, gain=0.5, pan=-0.25)
    s.line(0, WICK_A, "D4", I_horn, 0.55, gain=0.7, pan=0.15)
    s.line(8, WICK_B_FLAT, "D4", I_horn, 0.55, gain=0.7, pan=0.15)
    s.line(32, WICK_A, "F4", I_horn, 0.6, gain=0.7, pan=0.15)
    s.line(56, WICK_C, "D4", I_horn, 0.6, gain=0.72, pan=0.15)
    s.line(64, WICK_A, "D5", I_horn, 0.55, gain=0.6, pan=0.15)
    s.line(72, WICK_MAJ, "D4", I_horn, 0.62, gain=0.75, pan=0.15)
    for start in (30, 62):
        for k in range(16):
            s.put(start + k * 0.125, S.thump(70, 50, 0.3, 1.0, 0.09), 0.08 + 0.02 * k, 0.0, hum=0)
    s.mix.buf += np.stack([crackle(s.mix.L, 4, 800, 4000, 0.05), crackle(s.mix.L, 4, 800, 4000, 0.05)])
    return s.render(4.0, wet=0.42, rms_db=-20)


def music_ending():
    s = Song(66, 96, loop=False, tail=9.0, sd=110)
    plan = [["Dm", "Bb", "F", "C"], ["Dm", "Bb", "Gm", "A"], ["Dm", "Bb", "F", "C"], ["D", "G", "Bm", "A"],
            ["G", "D/F#", "Em", "A"], ["D", "D", "D", "D"]]
    harp_v = {"Dm": ["D3", "A3", "D4", "F4", "A4", "D5"], "Bb": ["Bb2", "F3", "Bb3", "D4", "F4", "Bb4"],
              "Gm": ["G2", "D3", "G3", "Bb3", "D4", "G4"], "A": ["A2", "E3", "A3", "C#4", "E4", "A4"],
              "F": ["F2", "C3", "F3", "A3", "C4", "F4"], "C": ["C3", "G3", "C4", "E4", "G4", "C5"],
              "D": ["D3", "A3", "D4", "F#4", "A4", "D5"], "G": ["G2", "D3", "G3", "B3", "D4", "G4"],
              "Bm": ["B2", "F#3", "B3", "D4", "F#4", "B4"], "Em": ["E3", "B3", "E4", "G4", "B4", "E5"],
              "D/F#": ["F#2", "D3", "A3", "D4", "F#4", "A4"]}
    for sec, prog in enumerate(plan):
        for i, c in enumerate(prog):
            b = sec * 16 + i * 4
            if sec == 5 and i > 0:
                continue
            hold = 16 if sec == 5 else 4
            s.pad(b, hold, CH[c], gain=0.14 if sec < 3 else 0.18, bright=0.4 + 0.05 * sec, attack=1.6, release=3.0)
            if sec >= 1:
                s.note(b, I_piano, BASS[c].replace("1", "2"), 4, 0.45, gain=0.5, pan=-0.2)
            if sec in (1, 3, 4):
                s.arp(b, 4, harp_v[c], I_harp, [0, 1, 2, 3, 4, 5, 4, 2], 0.5, vel=0.35, gain=0.45, pan=-0.3)
            if sec >= 2:
                s.choir(b, hold, CH[c][1:], gain=0.08 + 0.02 * sec, vowel="a", attack=1.5, release=3.0)
    s.line(0, WICK_A, "D5", I_box, 0.6, gain=0.7, pan=0.2)
    s.line(8, WICK_B, "D5", I_box, 0.55, gain=0.7, pan=0.2)
    s.line(16, WICK_A, "D4", I_piano, 0.55, gain=0.8, pan=-0.1)
    s.line(24, WICK_C, "D4", I_piano, 0.55, gain=0.8, pan=-0.1)
    s.line(32, WICK_A, "D4", I_horn, 0.55, gain=0.65, pan=0.1)
    s.line(40, WICK_B_FLAT, "D4", I_horn, 0.55, gain=0.65, pan=0.1)
    s.line(32, [(None, 2), (12, 2), (7, 2), (3, 2), (5, 4), (2, 4)], "D5", I_box, 0.35, gain=0.45, pan=0.4)
    s.line(48, WICK_MAJ, "D4", I_horn, 0.62, gain=0.75, pan=0.1)
    s.line(48, WICK_MAJ, "D5", I_hum, 0.4, gain=0.35, pan=-0.2)
    s.line(56, WICK_MAJ_B, "D4", I_horn, 0.6, gain=0.75, pan=0.1)
    s.line(64, WICK_MAJ, "D5", I_box, 0.5, gain=0.6, pan=0.25)
    s.line(64, WICK_MAJ, "D4", I_piano, 0.48, gain=0.65, pan=-0.15)
    s.line(72, WICK_MAJ_C, "D5", I_box, 0.5, gain=0.6, pan=0.25)
    s.line(72, WICK_MAJ_C, "D4", I_piano, 0.48, gain=0.65, pan=-0.15)
    for k, nt in enumerate(["D3", "A3", "D4", "F#4", "A4", "D5", "F#5", "A5"]):
        s.note(80 + k * 0.18, I_harp, nt, 6, 0.5, gain=0.5, pan=-0.4 + k * 0.1)
    for b, nt in ((81, "D6"), (83, "A5"), (85, "F#5"), (87, "D5")):
        s.note(b, I_box, nt, 2, 0.4, gain=0.5, pan=0.3)
    out = s.render(3.4, wet=0.45, rms_db=-20)
    n = out.shape[1]
    fade = int(7.0 * SR)
    out[:, n - fade:] *= np.linspace(1, 0, fade) ** 2
    return out


MUSIC = {
    "title": music_title, "mossgrave": music_mossgrave, "hollow_cold": music_hollow_cold,
    "hollow": music_hollow, "glimmerdeep": music_glimmerdeep, "drowned": music_drowned,
    "rootdark": music_rootdark, "chase": music_chase, "hearth": music_hearth, "ending": music_ending,
}


# =============================================================== ambience ===
def lfo(t, T, cycles, phase=0.0):
    return 0.5 + 0.5 * np.sin(TAU * cycles * t / T + phase)


def wind(n, lo, hi, swell_cycles=(2, 5), gain=0.06, seed_phase=0.0):
    t = np.arange(n) / SR
    T = n / SR
    out = []
    for ch in range(2):
        w = S.pink(n)
        c = (lo + hi) / 2
        center = c + (hi - lo) * 0.35 * (np.sin(TAU * swell_cycles[0] * t / T + ch + seed_phase)
                                         + 0.5 * np.sin(TAU * swell_cycles[1] * t / T))
        bw = (hi - lo) * 0.4
        w = S.tv_filter(w, lambda f, tt: 1.0 / (1.0 + ((f - np.interp(tt % T, t, center)) / bw) ** 2), 2048)
        amp = 0.45 + 0.55 * lfo(t, T, swell_cycles[0], 0.7 + ch * 0.5 + seed_phase)
        out.append(S.normalize(w * amp, gain))
    return np.stack(out)


def drip(f0, gain=1.0):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 1.2 * (1 - np.exp(-t / 0.012)))
    x = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-t / 0.035)
    return S.attack_ramp(x, 0.001) * gain


def owl():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for start, dur in ((0.0, 0.42), (0.75, 0.2), (1.02, 0.36)):
        k0, k1 = int(start * SR), int((start + dur) * SR)
        tt = t[k0:k1] - start
        f = 395 * (1 - 0.06 * tt / dur)
        seg = S.additive(395, k1 - k0, [1, 2, 3], [1, 0.18, 0.05], [None] * 3, attack=0, vib=f / 395)
        x[k0:k1] += seg * S.ramp_env(k1 - k0, 0.06, 0.12)
    return x


def whisper(dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    r = S.rand()
    vowels = list(S.VOWELS.keys())
    out = np.zeros(n)
    seg = int(0.15 * SR)
    for k in range(0, n, seg):
        v = vowels[r.integers(len(vowels))]
        ln = min(seg, n - k)
        x = S.fft_filter(S.noise(ln * 2), lambda f: S.formant_gain(f, S.VOWELS[v], 1.1))[:ln]
        out[k:k + ln] += x * S.ramp_env(ln, 0.03, 0.05)
    return S.normalize(out * S.ramp_env(n, 0.2, 0.3), 0.5)


def amb_forest():
    S.seed(201)
    T = 32.0
    mx = S.Mix(T)
    n = mx.L
    mx.buf += wind(n, 250, 1300, (2, 5), 0.07)
    r = S.rand()
    for cr, (freq, pan, period) in enumerate(((4300, -0.6, 0.72), (4720, 0.55, 0.86), (3980, 0.1, 1.1))):
        t0 = r.uniform(0, 1)
        while t0 < T:
            if r.random() < 0.85:
                for p in range(3):
                    ln = int(0.016 * SR)
                    tone = np.sin(TAU * freq * np.arange(ln) / SR) * np.hanning(ln)
                    mx.add(t0 + p * 0.032, tone, 0.012 * r.uniform(0.6, 1.0), pan)
            t0 += period * r.uniform(0.9, 1.15)
    mx.add(13.0, owl(), 0.05, -0.5)
    buf = S.reverb(mx.buf, S.make_ir(1.8, damp=1.2), wet=0.3)
    return S.master(buf, -6, -27)


def amb_hollow():
    S.seed(202)
    T = 30.0
    mx = S.Mix(T)
    n = mx.L
    t = np.arange(n) / SR
    mx.buf += wind(n, 150, 700, (2, 3), 0.04, 1.0)
    roar = S.fft_filter(S.noise(n), S.low_gain(260, 2))
    flick = S.fft_filter(S.noise(n), S.low_gain(3, 1))
    roar *= 0.6 + 0.4 * S.normalize(flick, 1.0)
    mx.add(0, S.normalize(roar, 0.05), 1.0, 0.2)
    mx.add(0, S.normalize(crackle(n, 7, 1000, 5000, 1.0, 0.08), 0.22), 1.0, 0.25)
    mx.add(0, S.normalize(crackle(n, 3, 600, 2500, 1.0, 0.1), 0.12), 1.0, 0.1)
    buf = S.reverb(mx.buf, S.make_ir(1.2, damp=1.3), wet=0.22)
    return S.master(buf, -6, -27)


def amb_cave():
    S.seed(203)
    T = 30.0
    mx = S.Mix(T)
    n = mx.L
    t = np.arange(n) / SR
    hum = np.sin(TAU * 55 * t) * (0.6 + 0.4 * lfo(t, T, 3)) + 0.5 * np.sin(TAU * 82.5 * t) * lfo(t, T, 2, 1)
    mx.add(0, S.normalize(hum, 0.03), 1.0, 0.0)
    air = np.stack([S.fft_filter(S.pink(n), S.low_gain(900)), S.fft_filter(S.pink(n), S.low_gain(900))])
    mx.buf += air / np.abs(air).max() * 0.02
    r = S.rand()
    for _ in range(16):
        mx.add(r.uniform(0, T), drip(r.uniform(650, 1500)), r.uniform(0.05, 0.14), r.uniform(-0.9, 0.9))
    buf = S.reverb(mx.buf, S.make_ir(4.2, damp=1.0, predelay=0.03), wet=0.65)
    return S.master(buf, -6, -28)


def amb_water():
    S.seed(204)
    T = 30.0
    mx = S.Mix(T)
    n = mx.L
    t = np.arange(n) / SR
    for ch in range(2):
        lap = S.fft_filter(S.noise(n), S.band_gain(180, 900))
        sw = lfo(t, T, 10, ch * 1.7) ** 3 * (0.6 + 0.4 * lfo(t, T, 3, ch))
        mx.buf[ch] += S.normalize(lap * (0.25 + sw), 0.05)
    r = S.rand()
    for _ in range(9):
        mx.add(r.uniform(0, T), drip(r.uniform(380, 750)), r.uniform(0.06, 0.12), r.uniform(-0.8, 0.8))
    mx.add(0, S.normalize(np.sin(TAU * 49 * t) * lfo(t, T, 2), 0.02), 1.0, 0.0)
    buf = S.reverb(mx.buf, S.make_ir(5.0, damp=1.4, predelay=0.05), wet=0.6)
    return S.master(buf, -6, -27)


def amb_roots():
    S.seed(205)
    T = 32.0
    mx = S.Mix(T)
    n = mx.L
    mx.buf += wind(n, 90, 420, (2, 3), 0.05, 2.0)
    r = S.rand()
    for _ in range(6):
        mx.add(r.uniform(0, T), creak(r.uniform(0.6, 1.3), r.uniform(100, 180)), r.uniform(0.04, 0.07),
               r.uniform(-0.9, 0.9))
    for _ in range(4):
        mx.add(r.uniform(0, T), whisper(r.uniform(0.8, 1.6)), 0.018, r.uniform(-1, 1))
    buf = S.reverb(mx.buf, S.make_ir(3.0, damp=1.3), wet=0.45)
    return S.master(buf, -6, -27)


def amb_hearth():
    S.seed(206)
    T = 30.0
    mx = S.Mix(T)
    n = mx.L
    t = np.arange(n) / SR
    rumble = S.fft_filter(S.noise(n), S.low_gain(110, 2)) * (0.6 + 0.4 * lfo(t, T, 2))
    mx.add(0, S.normalize(rumble, 0.08), 1.0, 0.0)
    mx.add(0, S.normalize(np.sin(TAU * 41 * t) * lfo(t, T, 3, 0.4), 0.04), 1.0, 0.0)
    mx.add(0, S.normalize(crackle(n, 4, 500, 3000, 1.0, 0.12), 0.18), 1.0, -0.2)
    mx.add(0, S.normalize(crackle(n, 3, 900, 4500, 1.0, 0.1), 0.12), 1.0, 0.3)
    buf = S.reverb(mx.buf, S.make_ir(3.0, damp=1.2), wet=0.35)
    return S.master(buf, -6, -25)


AMBIENCE = {"forest": amb_forest, "hollow": amb_hollow, "cave": amb_cave, "water": amb_water,
            "roots": amb_roots, "hearth": amb_hearth}


# ==================================================================== sfx ===
def _n(sec):
    return int(sec * SR)


def _t(n):
    return np.arange(n) / SR


def sweep_noise(dur, f_from, f_to, q=0.35, attack=0.3, release=0.5):
    """Noise through a band that sweeps from f_from to f_to (a whoosh)."""
    n = _n(dur)
    x = S.noise(n + 2048)

    def g(f, tt):
        c = f_from * (f_to / f_from) ** min(1.0, tt / dur)
        return 1.0 / (1.0 + ((f - c) / (c * q)) ** 2)
    y = S.tv_filter(x, g, 512)[:n]
    return y * S.ramp_env(n, dur * attack, dur * release)


def with_reverb(x, seconds=1.2, wet=0.25, damp=1.0):
    """Mono sound + its reverb tail (the buffer is extended to hold the tail)."""
    full = np.concatenate([x, np.zeros(int(seconds * SR))])
    st = np.stack([full, full])
    out2 = S.reverb(st, S.make_ir(seconds, damp=damp, predelay=0.01), wet=wet, loop=False).mean(axis=0)
    k = len(out2)
    fade = min(k // 3, int(0.3 * SR))
    out2[k - fade:] *= np.linspace(1, 0, fade)
    return out2


def mixdown(parts):
    n = max(len(p) + int(o * SR) for o, p in parts)
    out = np.zeros(n)
    for o, p in parts:
        k = int(o * SR)
        out[k:k + len(p)] += p
    return out


def sfx_jump():
    w = sweep_noise(0.13, 700, 2600, 0.5, 0.2, 0.7)
    n = _n(0.09)
    f = 380 + 300 * _t(n) / 0.09
    blip = np.sin(TAU * np.cumsum(f) / SR) * np.exp(-_t(n) / 0.03)
    return S.normalize(mixdown([(0, S.normalize(w, 1.0)), (0, blip * 0.15)]), 0.32)


def sfx_land():
    th = S.thump(120, 60, 0.12, 1.0, 0.035)
    nz = S.fft_filter(S.noise(_n(0.1)), S.low_gain(500, 2)) * np.exp(-_t(_n(0.1)) / 0.02)
    return S.normalize(mixdown([(0, th), (0, S.normalize(nz, 0.6))]), 0.4)


def sfx_step():
    n = _n(0.04)
    x = S.fft_filter(S.noise(n), S.band_gain(300, 2500)) * np.exp(-_t(n) / 0.008)
    return S.normalize(x, 0.14)


def sfx_ember():
    a = S.music_box(m("A5"), 0.9, 0.8)
    b = S.music_box(m("E6"), 0.9, 0.8)
    c = S.glass(m("A6"), 0.9, 0.4)
    return S.normalize(with_reverb(mixdown([(0, a), (0.07, b), (0.14, c * 0.5)]), 1.0, 0.25), 0.45)


def sfx_ember_lost():
    parts = [(i * 0.09, S.glass(m(nt), 1.0, 0.6 - i * 0.1)) for i, nt in enumerate(["E6", "C6", "A5", "F5"])]
    return S.normalize(with_reverb(mixdown(parts), 1.4, 0.35), 0.4)


def sfx_give():
    sw = sum(S.pad(nt, 0.45, 0.5, attack=0.35, release=0.6, bright=0.5) for nt in ("D4", "F#4", "A4"))
    ch = mixdown([(0.35 + i * 0.09, S.music_box(m(nt), 1.4, 0.6)) for i, nt in enumerate(["D6", "F#6", "A6"])])
    wh = sweep_noise(0.6, 400, 1800, 0.6, 0.6, 0.4)
    x = mixdown([(0, S.normalize(sw, 0.6)), (0, ch * 0.6), (0, S.normalize(wh, 0.12))])
    return S.normalize(with_reverb(x, 1.8, 0.35), 0.5)


def sfx_shrine():
    wh = S.normalize(sweep_noise(0.45, 300, 2200, 0.6, 0.5, 0.4), 0.5)
    n = _n(1.0)
    roar = S.fft_filter(S.noise(n), S.low_gain(400, 2)) * S.ramp_env(n, 0.15, 0.6)
    cr = crackle(n, 30, 1000, 5000, 1.0, 0.2) * np.exp(-_t(n) / 0.35)
    x = mixdown([(0, wh), (0.3, S.normalize(roar, 0.4)), (0.3, S.normalize(cr, 0.5))])
    return S.normalize(with_reverb(x, 1.0, 0.2), 0.5)


def sfx_hearth():
    wh = S.normalize(sweep_noise(0.7, 200, 1600, 0.6, 0.5, 0.4), 0.5)
    boom = S.thump(70, 40, 1.0, 1.0, 0.35)
    n = _n(1.6)
    roar = S.fft_filter(S.noise(n), S.low_gain(300, 2)) * S.ramp_env(n, 0.3, 0.9)
    cr = crackle(n, 40, 900, 4500, 1.0, 0.25) * np.exp(-_t(n) / 0.6)
    chord = sum(S.pad(nt, 0.8, 0.5, attack=0.5, release=0.8, bright=0.4) for nt in ("D3", "A3", "F#4"))
    x = mixdown([(0, wh), (0.45, boom * 0.6), (0.45, S.normalize(roar, 0.5)), (0.45, S.normalize(cr, 0.5)),
                 (0.4, S.normalize(chord, 0.25))])
    return S.normalize(with_reverb(x, 1.6, 0.25), 0.55)


def sfx_shade_near():
    w = whisper(0.9)
    n = len(w)
    low = np.sin(TAU * 110 * _t(n)) + np.sin(TAU * 113.5 * _t(n))
    return S.normalize(with_reverb(w + 0.15 * low * S.ramp_env(n, 0.3, 0.4), 1.5, 0.4), 0.3)


def sfx_shade_hit():
    n = _n(0.45)
    hiss = S.fft_filter(S.noise(n), S.high_gain(3000)) * np.exp(-_t(n) / 0.09)
    crack = S.additive(1870, _n(0.3), [1, 1.73, 2.61, 3.9], [1, 0.7, 0.5, 0.3], [0.05, 0.04, 0.03, 0.02], 0.0005)
    th = S.thump(90, 45, 0.25, 0.8, 0.06)
    return S.normalize(with_reverb(mixdown([(0, S.normalize(hiss, 0.6)), (0.01, crack * 0.5), (0, th * 0.5)]),
                                   1.0, 0.3), 0.5)


def sfx_shade_poof():
    wh = sweep_noise(0.7, 2000, 300, 0.7, 0.15, 0.7)
    return S.normalize(with_reverb(wh, 1.2, 0.35), 0.35)


def sfx_glimmer_on():
    x = mixdown([(0, S.glass(m("E6"), 0.9, 0.7)), (0.03, S.glass(m("B6"), 0.7, 0.3))])
    return S.normalize(with_reverb(x, 1.4, 0.35), 0.32)


def sfx_glimmer_off():
    x = S.glass(m("B5"), 0.6, 0.5)
    n = len(x)
    x *= np.linspace(0.2, 1.0, n) ** 2 * np.exp(-_t(n) / 0.18)
    return S.normalize(with_reverb(x, 1.0, 0.3), 0.2)


def metal_clink(f=2400.0, gain=1.0):
    return S.additive(f, _n(0.18), [1, 1.48, 2.32, 3.1], [1, 0.6, 0.4, 0.2], [0.05, 0.04, 0.03, 0.02], 0.0005) * gain


def sfx_wickway():
    r = S.rand()
    parts = []
    for k in range(18):
        parts.append((k * 0.09 + r.uniform(0, 0.03), metal_clink(r.uniform(1800, 3200), r.uniform(0.2, 0.45))))
    for k in range(10):
        parts.append((0.2 + k * 0.16, S.normalize(S.fft_filter(S.noise(_n(0.02)), S.band_gain(300, 1500)), 0.3)))
    parts.append((0.3, S.normalize(sweep_noise(1.6, 250, 1800, 0.5, 0.5, 0.4), 0.35)))
    return S.normalize(with_reverb(mixdown(parts), 1.4, 0.3), 0.5)


def sfx_door():
    return S.normalize(with_reverb(sweep_noise(0.6, 350, 1400, 0.5, 0.4, 0.5), 1.0, 0.3), 0.3)


def sfx_ui_move():
    n = _n(0.03)
    return S.normalize(np.sin(TAU * 1760 * _t(n)) * np.exp(-_t(n) / 0.006), 0.22)


def sfx_ui_select():
    return S.normalize(mixdown([(0, S.harp(m("A5"), 0.5, 0.7)), (0.04, S.harp(m("E6"), 0.5, 0.6))]), 0.35)


def sfx_title_card():
    x = mixdown([(0, S.glass(m("D6"), 3.0, 0.7)), (0.18, S.glass(m("A5"), 3.0, 0.5)),
                 (0.0, S.pad("D4", 1.0, 0.3, attack=0.4, release=1.4, bright=0.3))])
    return S.normalize(with_reverb(x, 2.4, 0.4), 0.4)


def sfx_respawn():
    x = mixdown([(0, S.glass(m("A5"), 1.0, 0.6)), (0, S.glass(m("E6"), 1.0, 0.4))])[::-1].copy()
    wh = sweep_noise(1.0, 300, 2500, 0.6, 0.85, 0.05)
    return S.normalize(with_reverb(mixdown([(0, x), (0, S.normalize(wh, 0.4))]), 1.0, 0.25), 0.4)


def sfx_hook():
    th = S.thump(180, 120, 0.15, 0.6, 0.03)
    return S.normalize(with_reverb(mixdown([(0, metal_clink(2600, 1.0)), (0.06, metal_clink(3100, 0.5)),
                                            (0.12, th)]), 0.8, 0.2), 0.4)


def sfx_flare():
    boom = S.normalize(S.fft_filter(S.noise(_n(0.6)), S.low_gain(400)) * np.exp(-_t(_n(0.6)) / 0.12), 0.7)
    wh = S.normalize(sweep_noise(0.5, 300, 3000, 0.6, 0.05, 0.8), 0.5)
    cr = S.normalize(crackle(_n(0.8), 40, 1000, 5000, 1.0) * np.exp(-_t(_n(0.8)) / 0.25), 0.4)
    th = S.thump(80, 45, 0.5, 1.0, 0.12)
    return S.normalize(with_reverb(mixdown([(0, boom), (0, wh), (0, th * 0.6), (0.08, cr)]), 1.4, 0.3), 0.55)


def sfx_thorn_burn():
    n = _n(1.2)
    cr = crackle(n, 60, 800, 5000, 1.0, 0.25) * S.ramp_env(n, 0.05, 0.7)
    hiss = S.fft_filter(S.noise(n), S.high_gain(2500)) * S.ramp_env(n, 0.1, 0.9) * 0.3
    return S.normalize(with_reverb(cr + S.normalize(hiss, np.abs(cr).max() * 0.3), 0.8, 0.2), 0.45)


def sfx_gate_open():
    n = _n(1.6)
    r = S.rand()
    grind = S.fft_filter(S.noise(n), S.band_gain(80, 900))
    rough = S.fft_filter(r.standard_normal(n), S.low_gain(25, 1))
    grind *= 0.4 + np.abs(S.normalize(rough, 1.0))
    rumble = S.fft_filter(S.noise(n), S.low_gain(90, 2))
    x = (S.normalize(grind, 0.6) + S.normalize(rumble, 0.4)) * S.ramp_env(n, 0.15, 0.4)
    x = mixdown([(0, x), (1.45, S.thump(90, 50, 0.4, 0.8, 0.1))])
    return S.normalize(with_reverb(x, 1.5, 0.3), 0.5)


def sfx_splash():
    n = _n(0.7)
    body = S.fft_filter(S.noise(n), S.band_gain(200, 3500)) * np.exp(-_t(n) / 0.12)
    r = S.rand()
    parts = [(0, S.normalize(body, 0.6))]
    for _ in range(7):
        parts.append((r.uniform(0.05, 0.4), drip(r.uniform(300, 900), r.uniform(0.15, 0.3))))
    return S.normalize(with_reverb(mixdown(parts), 1.5, 0.3), 0.5)


def sfx_page():
    n = _n(0.35)
    sw = S.fft_filter(S.noise(n), S.band_gain(1500, 7000)) * np.sin(np.linspace(0, np.pi, n)) ** 2
    cr = crackle(n, 30, 2000, 7000, 1.0) * np.sin(np.linspace(0, np.pi, n))
    return S.normalize(S.normalize(sw, 0.5) + S.normalize(cr, 0.3), 0.3)


def sfx_lamp():
    wh = S.normalize(sweep_noise(0.25, 500, 2000, 0.6, 0.4, 0.5), 0.3)
    return S.normalize(with_reverb(mixdown([(0, wh), (0.12, S.music_box(m("A6"), 0.8, 0.5))]), 1.0, 0.25), 0.35)


def sfx_bark():
    parts = []
    for k, (a, b) in enumerate(((1400, 2000), (1600, 2300))):
        n = _n(0.045)
        f = a + (b - a) * _t(n) / 0.045
        parts.append((k * 0.06, np.sin(TAU * np.cumsum(f) / SR) * np.hanning(n)))
    return S.normalize(mixdown(parts), 0.22)


SFX = {k[4:]: v for k, v in globals().items() if k.startswith("sfx_") and callable(v)}


# ================================================================= voices ===
# f0 Hz, formant scale, spectral tilt, syllable length range, vibrato (rate, depth), breath 0..1,
# glide (relative pitch change over a syllable), vowels, consonant onsets, extra effect, peak
VOICES = {
    "mossback":   dict(f0=74, k=0.82, tilt=0.9, dur=(0.13, 0.17), vib=(3.5, 0.012), breath=0.1, glide=0.05,
                       vowels="ouao@", cons=["", "m", "b", "h"], fx="hollow", peak=0.5),
    "tallow":     dict(f0=240, k=1.17, tilt=1.0, dur=(0.085, 0.115), vib=(6.0, 0.03), breath=0.12, glide=0.08,
                       vowels="aeio@", cons=["", "t", "m", "s", "h"], fx=None, peak=0.42),
    "pell":       dict(f0=640, k=1.7, tilt=0.75, dur=(0.045, 0.065), vib=(0, 0), breath=0.1, glide=0.15,
                       vowels="ie@a", cons=["", "t", "p", "s"], fx="flutter", peak=0.36),
    "burrow":     dict(f0=108, k=0.95, tilt=1.05, dur=(0.055, 0.085), vib=(0, 0), breath=0.3, glide=-0.12,
                       vowels="a@ou", cons=["k", "t", "h", ""], fx="rasp", peak=0.48),
    "wisp":       dict(f0=520, k=1.55, tilt=1.4, dur=(0.08, 0.11), vib=(5.0, 0.012), breath=0.15, glide=0.18,
                       vowels="iea", cons=["", "m", "h"], fx="singsong", peak=0.36),
    "ash":        dict(f0=150, k=1.05, tilt=1.2, dur=(0.09, 0.13), vib=(0, 0), breath=0.85, glide=-0.05,
                       vowels="a@oe", cons=["h", "s", "", ""], fx=None, peak=0.38, attack=0.02),
    "archivist":  dict(f0=185, k=1.0, tilt=1.2, dur=(0.1, 0.13), vib=(4.0, 0.01), breath=0.45, glide=0.0,
                       vowels="o@ae", cons=["", "h", "s", "t"], fx="echo", peak=0.4),
    "bell":       dict(f0=430, k=1.45, tilt=1.3, dur=(0.08, 0.1), vib=(5.5, 0.01), breath=0.15, glide=0.1,
                       vowels="ieao", cons=["", "t", ""], fx="bell", peak=0.36),
    "gudgeon":    dict(f0=60, k=0.74, tilt=0.9, dur=(0.16, 0.2), vib=(2.5, 0.015), breath=0.1, glide=-0.08,
                       vowels="ou@", cons=["b", "m", ""], fx="bubbles", peak=0.5),
    "rootmother": dict(f0=98, k=0.9, tilt=1.0, dur=(0.17, 0.22), vib=(4.5, 0.008), breath=0.15, glide=0.0,
                       vowels="oa@u", cons=["", "m", "h"], fx="choral", peak=0.48),
    "sprig":      dict(f0=800, k=1.95, tilt=1.3, dur=(0.05, 0.075), vib=(0, 0), breath=0.2, glide=0.2,
                       vowels="ie", cons=["", "t", "s"], fx="rustle", peak=0.32),
    "hollow_one": dict(f0=84, k=0.9, tilt=1.1, dur=(0.13, 0.17), vib=(3.0, 0.01), breath=0.6, glide=-0.1,
                       vowels="o@ua", cons=["h", "s", ""], fx="reverse", peak=0.45),
}


def consonant(kind, k, f0):
    r = S.rand()
    if kind == "":
        return np.zeros(0)
    if kind in ("p", "b"):
        n = _n(0.012)
        x = S.fft_filter(S.noise(n * 2), S.low_gain(900 * k))[:n] * np.exp(-_t(n) / 0.003)
        return S.normalize(x, 0.5 if kind == "p" else 0.35)
    if kind == "t":
        n = _n(0.014)
        x = S.fft_filter(S.noise(n * 2), S.band_gain(2800 * k, 7000))[:n] * np.exp(-_t(n) / 0.004)
        return S.normalize(x, 0.4)
    if kind == "k":
        n = _n(0.018)
        x = S.fft_filter(S.noise(n * 2), S.band_gain(1300 * k, 3200 * k))[:n] * np.exp(-_t(n) / 0.005)
        return S.normalize(x, 0.45)
    if kind == "s":
        n = _n(r.uniform(0.03, 0.05))
        x = S.fft_filter(S.noise(n * 2), S.band_gain(4000, 9000))[:n] * S.ramp_env(n, 0.01, 0.01)
        return S.normalize(x, 0.22)
    if kind == "h":
        n = _n(0.025)
        x = S.fft_filter(S.noise(n * 2), lambda f: S.formant_gain(f, S.VOWELS["@"], k))[:n]
        return S.normalize(x * S.ramp_env(n, 0.01, 0.005), 0.18)
    if kind == "m":
        n = _n(0.035)
        ks = np.arange(1, 8)
        x = S.additive(f0, n, ks, 1.0 / ks ** 2.5, [None] * 7, attack=0.005)
        return S.normalize(x * S.ramp_env(n, 0.008, 0.004), 0.3)
    return np.zeros(0)


def syllable(cfg, idx):
    r = S.rand()
    k = cfg["k"]
    dur = r.uniform(*cfg["dur"])
    n = _n(dur)
    t = _t(n)
    f0 = cfg["f0"] * r.uniform(0.94, 1.08)
    glide = cfg["glide"] * r.uniform(0.5, 1.2)
    if cfg["fx"] == "singsong":
        glide = cfg["glide"] * (1 if idx % 2 == 0 else -1)
        f0 *= 1.0 + (0.1 if idx % 2 == 0 else -0.04)
    contour = (1 + glide * t / dur)
    rate, depth = cfg["vib"]
    if depth:
        contour = contour * (1 + depth * np.sin(TAU * rate * t + r.uniform(0, TAU)))
    if cfg["fx"] == "rasp":
        jit = S.fft_filter(r.standard_normal(n), S.low_gain(70, 1))
        contour = contour * (1 + 0.06 * S.normalize(jit, 1.0))
    vowel = cfg["vowels"][idx % len(cfg["vowels"])]
    form = S.VOWELS[vowel]
    nk = max(2, int(min(5500, SR * 0.42) // (f0 * max(1.0, 1 + glide))))
    ks = np.arange(1, nk + 1)
    amps = S.formant_gain(ks * f0, form, k) / ks ** cfg["tilt"] + 0.02 / ks
    voiced = S.additive(f0, n, ks, amps, [None] * nk, attack=0, vib=contour)
    voices = [voiced]
    if cfg["fx"] == "choral":
        for ratio in (1.5, 1.003, 0.997):
            voices.append(0.6 * S.additive(f0 * ratio, n, ks, S.formant_gain(ks * f0 * ratio, form, k)
                                           / ks ** cfg["tilt"], [None] * nk, attack=0, vib=contour))
    voiced = sum(voices)
    voiced /= np.sqrt(np.mean(voiced ** 2)) + 1e-9
    breath = S.fft_filter(S.noise(n), lambda f: S.formant_gain(f, form, k))
    breath /= np.sqrt(np.mean(breath ** 2)) + 1e-9
    b = cfg["breath"]
    x = voiced * (1 - b) + breath * b * 0.8
    if cfg["fx"] == "flutter":
        x *= 0.45 + 0.55 * (0.5 + 0.5 * np.sin(TAU * 38 * t))
    x *= S.ramp_env(n, cfg.get("attack", 0.008), min(0.04, dur * 0.35))
    cons = consonant(cfg["cons"][idx % len(cfg["cons"])], k, f0)
    if len(cons):
        cons = cons * np.abs(x).max() * 1.2
        ov = min(len(cons) // 3, n // 4)
        out = np.zeros(len(cons) + n - ov)
        out[:len(cons)] += cons
        out[len(cons) - ov:] += x
        x = out
    fx = cfg["fx"]
    if fx == "hollow":
        d = _n(0.0045)
        y = x.copy()
        y[d:] += 0.6 * x[:-d]
        y[2 * d:] += 0.3 * x[:-2 * d]
        x = S.fft_filter(np.pad(y, (0, 256)), S.low_gain(1800, 2))
    elif fx == "echo":
        y = np.concatenate([x, np.zeros(_n(0.3))])
        for delay, g in ((0.085, 0.45), (0.17, 0.22), (0.26, 0.1)):
            d = _n(delay)
            y[d:d + len(x)] += g * x
        x = y
    elif fx == "bell":
        nt = [m("A6"), m("C7"), m("D7"), m("E7"), m("G6")][idx % 5]
        bell = S.glass(nt, 0.35, 0.25)
        out = np.zeros(max(len(x), len(bell)))
        out[:len(x)] += x
        out[:len(bell)] += bell * np.abs(x).max()
        x = out
    elif fx == "bubbles":
        y = np.concatenate([x, np.zeros(_n(0.06))])
        for _ in range(r.integers(2, 4)):
            p = _n(r.uniform(0.0, len(x) / SR))
            bn = _n(0.025)
            f = r.uniform(250, 450) * (1 + 2.0 * _t(bn) / 0.025)
            bub = np.sin(TAU * np.cumsum(f) / SR) * np.hanning(bn) * np.abs(x).max() * 0.5
            y[p:p + bn] += bub[:len(y[p:p + bn])]
        x = S.fft_filter(y, S.low_gain(2200, 2))
    elif fx == "rustle":
        rn = len(x)
        rus = S.fft_filter(S.noise(rn), S.band_gain(3000, 8000)) * S.ramp_env(rn, 0.005, 0.02)
        x = x + S.normalize(rus, np.abs(x).max() * 0.35)
    elif fx == "reverse":
        # reversed envelope (swells up, ends abruptly), then a smeared backwards tail
        swell = np.linspace(0.35, 1.0, len(x)) ** 1.5
        smear = with_reverb(x, 0.2, 0.7)[::-1][:_n(0.14)]
        smear *= np.linspace(1.0, 0.0, len(smear)) ** 2
        x = np.concatenate([x * swell, S.normalize(smear, np.abs(x).max() * 0.35)])
    return S.normalize(x, cfg["peak"])


def narration_tick(idx):
    r = S.rand()
    n = _n(0.012)
    lo = 1800 + idx * 220
    x = S.fft_filter(S.noise(n * 3), S.band_gain(lo, lo * 2.2))[:n] * np.exp(-_t(n) / r.uniform(0.0015, 0.003))
    return S.normalize(x, 0.06)


# ================================================================= output ===
def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def write_ogg(rel, buf):
    path = os.path.join(OUT, rel)
    ensure(path)
    data = np.ascontiguousarray(np.clip(buf, -1.0, 1.0).T.astype(np.float32))
    # libsndfile's Vorbis encoder overflows the stack on huge single writes: stream in blocks
    with sf.SoundFile(path, "w", SR, 2, format="OGG", subtype="VORBIS") as f:
        for i in range(0, len(data), 4096):
            f.write(data[i:i + 4096])
    return path


def write_wav(rel, x):
    path = os.path.join(OUT, rel)
    ensure(path)
    x = np.clip(x, -1.0, 1.0)
    k = min(len(x) // 4, int(0.006 * SR))
    if k > 1:
        x = x.copy()
        x[-k:] *= np.linspace(1.0, 0.0, k)  # always end on silence (no click)
    sf.write(path, x.astype(np.float32), SR, subtype="PCM_16")
    return path


def stats(path):
    data, sr = sf.read(path, always_2d=True)
    peak = np.abs(data).max()
    rms = np.sqrt(np.mean(data ** 2))
    d = np.abs(np.diff(data, axis=0))
    seam = np.abs(data[0] - data[-1]).max() / (np.percentile(d, 99) + 1e-9)
    return len(data) / sr, peak, rms, seam, os.path.getsize(path)


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
            if g == "music":
                path = write_ogg(f"music/{key}.ogg", fn())
                rows.append((f"music/{key}", path))
            elif g == "ambience":
                path = write_ogg(f"ambience/{key}.ogg", fn())
                rows.append((f"ambience/{key}", path))
            elif g == "sfx":
                S.seed(sum(map(ord, key)) * 7)
                path = write_wav(f"sfx/{key}.wav", fn())
                rows.append((f"sfx/{key}", path))
            else:
                S.seed(sum(map(ord, key)))
                for i in range(8):
                    path = write_wav(f"voice/{key}_{i}.wav", syllable(fn, i))
                rows.append((f"voice/{key}_0..7", path))
        if g == "voice" and (not ids or "narration" in ids):
            S.seed(77)
            for i in range(8):
                path = write_wav(f"voice/narration_{i}.wav", narration_tick(i))
            rows.append(("voice/narration_0..7", path))
    print(f"{'id':28s} {'sec':>7s} {'peak dB':>8s} {'rms dB':>7s} {'seam':>6s} {'KB':>7s}")
    for name, path in rows:
        sec, peak, rms, seam, size = stats(path)
        print(f"{name:28s} {sec:7.2f} {S.db(peak):8.1f} {S.db(rms):7.1f} {seam:6.2f} {size / 1024:7.0f}")
    total = 0
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            if not f.endswith(".import"):
                total += os.path.getsize(os.path.join(dp, f))
    print(f"assets/audio total: {total / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main(sys.argv[1:])
