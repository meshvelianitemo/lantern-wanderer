"""Small numpy synthesizer shared by the audio generator (audio.py).

Everything is rendered offline, the same way the art is drawn by code:
  instruments    additive / formant synthesis -> mono float arrays
  Mix            stereo buffer; in loop mode every note that runs past the end
                 wraps around to the start, so loops are seamless by design
  reverb()       circular FFT convolution with a synthetic impulse response
                 (also wraps, so reverb tails carry across the loop point)
  fft_filter()   static filters on a whole buffer (circular, seam-safe)
  tv_filter()    time-varying filters (whooshes, wind) via overlap-add
"""
import math

import numpy as np

SR = 32000
TAU = 2.0 * np.pi
_rng = np.random.default_rng(1)


def seed(n):
    global _rng
    _rng = np.random.default_rng(n)


def rand():
    return _rng


# --------------------------------------------------------------- pitches ---
_NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def m(name):
    """'D4' -> 62, 'F#3' -> 54, 'Bb2' -> 46. Integers pass through."""
    if isinstance(name, (int, float)):
        return name
    n = _NAMES[name[0]]
    i = 1
    while i < len(name) and name[i] in "#b":
        n += 1 if name[i] == "#" else -1
        i += 1
    return n + 12 * (int(name[i:]) + 1)


def hz(note):
    return 440.0 * 2.0 ** ((m(note) - 69) / 12.0)


# ------------------------------------------------------------- envelopes ---
def ramp_env(n, attack, release, sr=SR):
    """Flat envelope with raised-cosine attack and release (seconds)."""
    e = np.ones(n)
    a = min(n, int(attack * sr))
    r = min(n - a, int(release * sr))
    if a > 0:
        e[:a] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    if r > 0:
        e[n - r:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return e


def attack_ramp(x, seconds, sr=SR):
    k = min(len(x), max(1, int(seconds * sr)))
    x[:k] *= np.linspace(0.0, 1.0, k)
    return x


def damp_after(x, hold, release=0.15, sr=SR):
    """Let a ringing note sound for `hold` seconds, then damp it quickly."""
    h = int(hold * sr)
    if h < len(x):
        t = np.arange(len(x) - h) / sr
        x[h:] *= np.exp(-t / (release / 4.0))
    return x


# ------------------------------------------------------------- additive ---
def additive(freq, n, ratios, amps, decays, attack=0.004, vib=None, sr=SR, phase=None):
    """Sum of sine partials, each with its own exponential decay (None = sustain).
    `vib` is an optional per-sample frequency multiplier (vibrato / glide)."""
    t = np.arange(n) / sr
    if vib is not None:
        base = TAU * np.cumsum(freq * vib) / sr
    else:
        base = TAU * freq * t
    out = np.zeros(n)
    for r, a, d in zip(ratios, amps, decays):
        if a == 0 or freq * r >= sr * 0.45:
            continue
        ph = _rng.uniform(0, TAU) if phase is None else phase
        part = a * np.sin(base * r + ph)
        if d:
            part *= np.exp(-t / d)
        out += part
    if attack:
        attack_ramp(out, attack, sr)
    return out


def click(n_ms=3.0, lo=1500, hi=6000, gain=0.3):
    n = max(8, int(n_ms / 1000 * SR))
    x = fft_filter(_rng.standard_normal(n * 4), band_gain(lo, hi))[:n]
    x *= np.exp(-np.arange(n) / (n / 4))
    return x / (np.abs(x).max() + 1e-9) * gain


# ----------------------------------------------------------- instruments ---
def harp(note, dur=3.0, vel=0.8, bright=1.0):
    f = hz(note)
    n = int(dur * SR)
    ks = np.arange(1, 13)
    base = 2.4 * (f / 220.0) ** -0.45
    amps = (1.0 / ks ** 1.35) * np.abs(np.sin(np.pi * ks * 0.27)) ** 0.5
    amps *= np.exp(-(ks - 1) * 0.42 / max(0.2, vel * bright))
    x = additive(f, n, ks, amps, base / ks ** 0.75, attack=0.002)
    x[:96] += click(3, 2000, 7000, 0.08 * vel)[:96] if n > 96 else 0
    return x * vel


def kalimba(note, dur=2.2, vel=0.8):
    f = hz(note)
    n = int(dur * SR)
    d = 1.1 * (f / 440.0) ** -0.35
    x = additive(f, n, [1, 2.0, 5.95, 9.1], [1, 0.05, 0.32 * vel, 0.06], [d, d * 0.4, 0.07, 0.03], attack=0.0015)
    x[:64] += click(2, 1500, 5000, 0.12 * vel)[:64]
    return x * vel


def music_box(note, dur=2.6, vel=0.8):
    f = hz(note)
    n = int(dur * SR)
    s = (f / 880.0) ** -0.3
    x = additive(f, n, [1, 2.0, 3.97, 6.8, 10.2], [1, 0.07, 0.28, 0.11, 0.04],
                 [1.7 * s, 0.8 * s, 0.42 * s, 0.18 * s, 0.08 * s], attack=0.0012)
    x[:48] += click(1.5, 3000, 9000, 0.1 * vel)[:48]
    return x * vel


def glass(note, dur=4.5, vel=0.8):
    """Glass / crystal bell with a slow shimmer between two close partials."""
    f = hz(note)
    n = int(dur * SR)
    s = (f / 880.0) ** -0.3
    x = additive(f, n, [1, 1.0016, 2.32, 4.25, 6.63, 9.38], [0.7, 0.45, 0.5, 0.26, 0.12, 0.05],
                 [3.4 * s, 3.0 * s, 1.6 * s, 0.75 * s, 0.38 * s, 0.18 * s], attack=0.002)
    return x * vel


def celesta(note, dur=2.8, vel=0.8):
    f = hz(note)
    n = int(dur * SR)
    s = (f / 880.0) ** -0.25
    x = additive(f, n, [1, 2.0, 2.76, 5.40, 8.9], [1, 0.06, 0.35 * vel, 0.18 * vel, 0.05],
                 [1.9 * s, 0.9 * s, 0.16, 0.06, 0.03], attack=0.0015)
    return x * vel


def church_bell(note, dur=9.0, vel=0.8):
    f = hz(note)
    n = int(dur * SR)
    x = additive(f, n, [0.5, 1, 1.19, 1.5, 2.0, 2.003, 2.52, 2.66, 3.01, 4.17],
                 [0.5, 1, 0.6, 0.32, 0.4, 0.25, 0.22, 0.16, 0.12, 0.06],
                 [10, 7, 5, 3.4, 3, 2.6, 2, 1.6, 1.2, 0.7], attack=0.002)
    x[:128] += click(4, 800, 4000, 0.15)[:128]
    return x * vel


def piano(note, dur=4.0, vel=0.7, hold=None):
    f = hz(note)
    n = int(dur * SR)
    t = np.arange(n) / SR
    ks = np.arange(1, 15)
    amps = 1.0 / ks ** (1.75 - 0.6 * vel) * (0.6 + 0.4 * np.abs(np.sin(np.pi * ks / 7.3)))
    base = 4.0 * (f / 262.0) ** -0.6
    out = np.zeros(n)
    for detune, g in ((1.0, 1.0), (1.0004, 0.55)):
        for k, a in zip(ks, amps):
            fk = f * detune * k * math.sqrt(1 + 0.0002 * k * k)
            if fk > SR * 0.45:
                continue
            d = base / k ** 0.8
            env = 0.55 * np.exp(-t / (d * 0.22)) + 0.45 * np.exp(-t / d)
            out += g * a * np.sin(TAU * fk * t + _rng.uniform(0, TAU)) * env
    attack_ramp(out, 0.003)
    if hold is not None:
        damp_after(out, hold, 0.25)
    return out * vel * 0.7


def lute(note, dur=2.4, vel=0.8, mute=False, pos=0.16):
    """Plucked gut string (guitar / lute), slightly inharmonic."""
    f = hz(note)
    n = int(dur * SR)
    ks = np.arange(1, 17)
    amps = np.abs(np.sin(np.pi * ks * pos)) / ks ** 0.95 * np.exp(-(ks - 1) * 0.1 / max(0.2, vel))
    d = 1.7 * (f / 196.0) ** -0.5 * (0.18 if mute else 1.0)
    ratios = ks * np.sqrt(1 + 0.00008 * ks * ks)
    x = additive(f, n, ratios, amps, d / ks ** 0.85, attack=0.0018)
    x[:96] += click(3, 1200, 5000, 0.1 * vel)[:96]
    return x * vel


def pad(note, hold, vel=0.5, attack=1.5, release=2.0, bright=0.5, voices=3, detune=7.0, vib=0.003):
    """Warm detuned pad. Total length = hold + release."""
    f = hz(note)
    n = int((hold + release) * SR)
    t = np.arange(n) / SR
    ks = np.arange(1, 11)
    amps = 1.0 / ks ** (2.3 - bright)
    out = np.zeros(n)
    for v in range(voices):
        c = (v - (voices - 1) / 2) * detune * 2 / max(1, voices - 1) if voices > 1 else 0
        lfo = 1 + vib * np.sin(TAU * _rng.uniform(0.12, 0.3) * t + _rng.uniform(0, TAU))
        out += additive(f * 2 ** (c / 1200), n, ks, amps, [None] * 10, attack=0, vib=lfo)
    out *= ramp_env(n, attack, release) / voices
    return out * vel


def reed(note, hold, vel=0.5, release=0.25, attack=0.06):
    """Accordion / harmonium reed with a musette (detuned second reed)."""
    f = hz(note)
    n = int((hold + release) * SR)
    ks = np.arange(1, 15)
    amps = 1.0 / ks ** 1.15 * np.where(ks % 2 == 1, 1.0, 0.55)
    x = additive(f, n, ks, amps, [None] * 14, attack=0)
    x += 0.5 * additive(f * 2 ** (13 / 1200), n, ks, amps, [None] * 14, attack=0)
    swell = 0.85 + 0.15 * np.sin(np.linspace(0, np.pi, n))
    return x * ramp_env(n, attack, release) * swell * vel * 0.5


VOWELS = {
    "a": [(730, 90, 1.0), (1090, 110, 0.5), (2440, 160, 0.22)],
    "e": [(530, 70, 1.0), (1840, 100, 0.42), (2480, 150, 0.28)],
    "i": [(300, 60, 1.0), (2290, 110, 0.32), (3010, 160, 0.22)],
    "o": [(570, 80, 1.0), (840, 90, 0.6), (2410, 150, 0.14)],
    "u": [(310, 60, 1.0), (870, 90, 0.33), (2240, 140, 0.09)],
    "@": [(500, 80, 1.0), (1500, 110, 0.4), (2500, 160, 0.2)],
}


def formant_gain(f, formants, scale=1.0):
    f = np.asarray(f, dtype=float)
    g = np.zeros_like(f)
    for F, B, a in formants:
        F *= scale
        B *= scale
        g += a / (1.0 + ((f - F) / (B / 2.0)) ** 2)
    return g


def choir(note, hold, vel=0.5, vowel="u", attack=0.9, release=1.6, voices=4, vib_depth=0.006):
    f = hz(note)
    n = int((hold + release) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    nk = int(min(4200, SR * 0.4) // f)
    ks = np.arange(1, max(2, nk) + 1)
    for v in range(voices):
        fv = f * 2 ** (_rng.uniform(-9, 9) / 1200)
        amps = formant_gain(ks * fv, VOWELS[vowel]) / ks ** 0.6
        vr = _rng.uniform(4.4, 5.6)
        onset = np.clip((t - _rng.uniform(0.2, 0.6)) / 0.8, 0, 1)
        lfo = 1 + vib_depth * onset * np.sin(TAU * vr * t + _rng.uniform(0, TAU))
        out += additive(fv, n, ks, amps, [None] * len(ks), attack=0, vib=lfo)
    breath = fft_filter(_rng.standard_normal(n), lambda fr: formant_gain(fr, VOWELS[vowel])) * 0.04
    out = (out / voices + breath) * ramp_env(n, attack, release)
    return out * vel


def horn(note, hold, vel=0.6, attack=0.14, release=0.45):
    f = hz(note)
    n = int((hold + release) * SR)
    t = np.arange(n) / SR
    ks = np.arange(1, 13)
    env = ramp_env(n, attack, release)
    lfo = 1 + 0.004 * np.clip((t - 0.4) / 0.6, 0, 1) * np.sin(TAU * 5.0 * t)
    soft = additive(f, n, ks, 1.0 / ks ** 2.6, [None] * 12, attack=0, vib=lfo)
    bright = additive(f, n, ks, 1.0 / ks ** 1.4, [None] * 12, attack=0, vib=lfo)
    return (soft * env + 0.35 * bright * env ** 2.2) * vel * 0.6


BODY = [(280, 120, 1.0), (520, 200, 0.7), (1100, 300, 0.45), (2600, 600, 0.2)]


def cello(note, hold, vel=0.6, attack=0.3, release=0.6):
    f = hz(note)
    n = int((hold + release) * SR)
    t = np.arange(n) / SR
    nk = int(min(5000, SR * 0.4) // f)
    ks = np.arange(1, max(2, nk) + 1)
    amps = (1.0 / ks) * (0.25 + formant_gain(ks * f, BODY))
    lfo = 1 + 0.005 * np.clip((t - 0.35) / 0.5, 0, 1) * np.sin(TAU * 5.2 * t)
    x = additive(f, n, ks, amps, [None] * len(ks), attack=0, vib=lfo)
    bow = fft_filter(_rng.standard_normal(n), band_gain(800, 4000)) * 0.03
    return (x * 0.5 + bow) * ramp_env(n, attack, release) * vel


def thump(f0=62.0, f1=38.0, dur=0.45, vel=0.8, decay=0.16):
    """Soft low drum / heartbeat thump with a pitch drop."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = f1 + (f0 - f1) * np.exp(-t / 0.05)
    x = np.sin(TAU * np.cumsum(freq) / SR) * np.exp(-t / decay)
    x[:64] += click(2, 200, 1500, 0.15)[:64]
    return attack_ramp(x, 0.003) * vel


# ----------------------------------------------------------------- noise ---
def noise(n):
    return _rng.standard_normal(n)


def fft_filter(x, gain_fn, sr=SR):
    """Static filter in the frequency domain (circular: seam-safe on loops)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    return np.fft.irfft(X * gain_fn(f), len(x))


def low_gain(fc, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (f / fc) ** (2 * order))


def high_gain(fc, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (fc / np.maximum(f, 1e-3)) ** (2 * order))


def band_gain(lo, hi, order=2):
    lo_g, hi_g = high_gain(lo, order), low_gain(hi, order)
    return lambda f: lo_g(f) * hi_g(f)


def pink(n):
    return fft_filter(noise(n), lambda f: 1.0 / np.sqrt(np.maximum(f, 20.0) / 20.0))


def tv_filter(x, gain_fn_t, block=1024, sr=SR):
    """Time-varying filter: gain_fn_t(freqs, t_seconds) -> gains, overlap-add.
    Circular (wraps at the end) so it is safe on loops."""
    n = len(x)
    hop = block // 2
    win = np.hanning(block + 1)[:-1]
    f = np.fft.rfftfreq(block, 1.0 / sr)
    out = np.zeros(n)
    xx = np.concatenate([x, x[:block]])
    for s in range(0, n, hop):
        seg = xx[s:s + block] * win
        y = np.fft.irfft(np.fft.rfft(seg) * gain_fn_t(f, (s + hop) / sr), block)
        idx = (s + np.arange(block)) % n
        out[idx] += y
    return out


# ------------------------------------------------------------------- mix ---
class Mix:
    """Stereo buffer. In loop mode notes wrap around the end (seamless loops)."""

    def __init__(self, seconds, loop=True, tail=0.0):
        self.L = int(round(seconds * SR))
        self.loop = loop
        self.n = self.L if loop else self.L + int(tail * SR)
        self.buf = np.zeros((2, self.n))

    def add(self, t, mono, gain=1.0, pan=0.0):
        """Constant-power panned mono sound starting at t seconds."""
        a = (pan + 1.0) * math.pi / 4.0
        start = int(round(t * SR))
        self._place(0, start, mono * (math.cos(a) * gain * math.sqrt(2)))
        self._place(1, start, mono * (math.sin(a) * gain * math.sqrt(2)))

    def add_stereo(self, t, st, gain=1.0):
        start = int(round(t * SR))
        self._place(0, start, st[0] * gain)
        self._place(1, start, st[1] * gain)

    def _place(self, ch, start, x):
        if self.loop:
            start %= self.L
            if len(x) > self.L:  # fold very long sounds onto one period
                k = math.ceil(len(x) / self.L)
                x = np.pad(x, (0, k * self.L - len(x))).reshape(k, self.L).sum(axis=0)
            first = min(len(x), self.L - start)
            self.buf[ch, start:start + first] += x[:first]
            rest = len(x) - first
            if rest > 0:
                self.buf[ch, :rest] += x[first:]
        else:
            end = min(self.n, start + len(x))
            if end > start:
                self.buf[ch, start:end] += x[:end - start]


def make_ir(seconds=3.0, predelay=0.02, damp=1.0, early=6, sd=11):
    """Synthetic stereo reverb impulse response with frequency-dependent decay."""
    r = np.random.default_rng(sd)
    n = int(seconds * 1.15 * SR)
    t = np.arange(n) / SR
    f = np.fft.rfftfreq(n, 1.0 / SR)
    bands = [(0, 400, 1.15), (400, 1800, 1.0), (1800, 5000, 0.6 / damp), (5000, SR, 0.3 / damp)]
    ir = np.zeros((2, n))
    for ch in range(2):
        X = np.fft.rfft(r.standard_normal(n))
        for lo, hi, k in bands:
            mask = ((f >= lo) & (f < hi)).astype(float)
            band = np.fft.irfft(X * mask, n)
            ir[ch] += band * 10.0 ** (-3.0 * t / (seconds * k))
        ir[ch] *= np.clip(t / 0.012, 0, 1)
        pd = int(predelay * SR)
        ir[ch] = np.concatenate([np.zeros(pd), ir[ch][:n - pd]])
        for _ in range(early):
            d = int(r.uniform(0.004, 0.045) * SR) + pd // 2
            ir[ch, d] += r.uniform(0.3, 0.8) * r.choice((-1, 1)) * 6.0
        ir[ch] /= np.sqrt(np.sum(ir[ch] ** 2))
    return ir


def reverb(buf, ir, wet=0.3, dry=1.0, loop=True):
    n = buf.shape[1]
    mono = buf.mean(axis=0)
    N = n if loop else n + ir.shape[1]
    if loop and ir.shape[1] > n:
        ir = ir[:, :n]
    X = np.fft.rfft(mono, N)
    out = buf * dry
    for ch in range(2):
        w = np.fft.irfft(X * np.fft.rfft(ir[ch], N), N)[:n]
        out[ch] += w * wet
    return out


def stereo_filter(buf, gain_fn):
    return np.stack([fft_filter(buf[0], gain_fn), fft_filter(buf[1], gain_fn)])


def master(buf, peak_db=-3.0, rms_db=-21.0):
    peak = np.abs(buf).max() + 1e-12
    rms = np.sqrt(np.mean(buf ** 2)) + 1e-12
    g = min(10 ** (peak_db / 20) / peak, 10 ** (rms_db / 20) / rms)
    return buf * g


def normalize(x, peak=0.5):
    return x / (np.abs(x).max() + 1e-12) * peak


def db(x):
    return 20 * math.log10(max(1e-9, x))
