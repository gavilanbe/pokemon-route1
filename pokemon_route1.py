#!/usr/bin/env python3
"""
Pokemon Red/Blue - Route 1 Theme
Multi-channel Game Boy style synthesis
4 channels: Pulse1 (melody), Pulse2 (harmony), Wave (bass), Noise (percussion)
"""

import numpy as np
import wave
import struct
import subprocess
import sys

SAMPLE_RATE = 44100
BPM = 127
# Each step in the notation = 1/8 beat
STEP = 60.0 / BPM / 2  # ~0.236s per step... too slow
# Actually each char seems to be a 16th note
STEP = 60.0 / BPM / 4  # ~0.118s per step

# --- Note frequencies ---
NOTE_FREQ = {
    # Octave 3
    'D3': 146.83, 'E3': 164.81, 'F#3': 185.00, 'G3': 196.00,
    'A3': 220.00, 'B3': 246.94, 'C#3': 138.59,
    # Octave 4
    'D4': 293.66, 'E4': 329.63, 'F#4': 369.99, 'G4': 392.00,
    'A4': 440.00, 'B4': 493.88, 'C#4': 277.18,
    # Octave 5
    'D5': 587.33, 'E5': 659.26, 'F#5': 739.99, 'G5': 783.99,
    'A5': 880.00, 'B5': 987.77, 'C#5': 554.37,
    'C#6': 1108.73,
}


def square_wave(freq, duration, duty=0.5, volume=0.25):
    """Generate a square/pulse wave like Game Boy channels 1 & 2."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    if freq == 0:
        return np.zeros_like(t)
    phase = (t * freq) % 1.0
    wave = np.where(phase < duty, volume, -volume)
    # Apply small fade in/out to reduce clicks
    fade_samples = min(int(SAMPLE_RATE * 0.005), len(wave) // 4)
    if fade_samples > 0:
        wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    return wave


def wave_channel(freq, duration, volume=0.20):
    """Game Boy wave channel - softer triangle-ish wave for bass."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    if freq == 0:
        return np.zeros_like(t)
    # Quantized triangle (4-bit like GB wave channel)
    phase = (t * freq) % 1.0
    tri = 2.0 * np.abs(2.0 * phase - 1.0) - 1.0
    # Quantize to 4-bit (16 levels)
    tri = np.round(tri * 7.5) / 7.5
    out = tri * volume
    fade_samples = min(int(SAMPLE_RATE * 0.005), len(out) // 4)
    if fade_samples > 0:
        out[:fade_samples] *= np.linspace(0, 1, fade_samples)
        out[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    return out


def noise_channel(duration, volume=0.08):
    """Game Boy noise channel for percussion."""
    samples = int(SAMPLE_RATE * duration)
    noise = np.random.choice([-volume, volume], size=samples)
    # Envelope decay
    env = np.exp(-np.linspace(0, 8, samples))
    return noise * env


def parse_melody(notation, note_map):
    """
    Parse notation string into [(freq, duration_in_steps), ...]
    Letters = notes, - = sustain, . = rest
    """
    notes = []
    current_note = None
    current_dur = 0

    for ch in notation:
        if ch == '-':
            current_dur += 1
        elif ch == '.':
            # Flush previous
            if current_note is not None:
                notes.append((current_note, current_dur))
            current_note = 0  # rest
            current_dur = 1
        else:
            if current_note is not None:
                notes.append((current_note, current_dur))
            freq = note_map.get(ch, 0)
            current_note = freq
            current_dur = 1

    if current_note is not None:
        notes.append((current_note, current_dur))

    return notes


def render_channel(notes, synth_func, **kwargs):
    """Render a list of (freq, steps) into audio samples."""
    audio = np.array([], dtype=np.float64)
    for freq, steps in notes:
        dur = steps * STEP
        if freq == 0:
            audio = np.append(audio, np.zeros(int(SAMPLE_RATE * dur)))
        else:
            audio = np.append(audio, synth_func(freq, dur, **kwargs))
    return audio


# =============================================================
# CHANNEL 1 - MELODY (Pulse wave, 50% duty)
# =============================================================
# Notation: lowercase=natural, UPPERCASE=sharp (in D major)
# d=D5, e=E5, F=F#5, g=G5, a=A5, b=B5, C=C#5
ch1_map = {
    'd': NOTE_FREQ['D5'], 'e': NOTE_FREQ['E5'], 'F': NOTE_FREQ['F#5'],
    'g': NOTE_FREQ['G5'], 'a': NOTE_FREQ['A5'], 'b': NOTE_FREQ['B5'],
    'C': NOTE_FREQ['C#5'],
}

ch1_notation = (
    "deF-F-F-deF-F-F-deF-F-g--F"
    "e-----Cde-e-e-Cde-e-e-Cde-"
    "e-FeeFd---F-deF-F-F-deF-F-"
    "F-deF-F-g--Fe-----Cde-g-F-"
    "e-d-C---C-a---e---F-----eF"
    "a-a-F-d-----b---a-F-d-F-e-"
    "----eFa-a-F-d-----b-Fga---"
    "deF-F-g--Fe-----Cde-e-e-Cd"
    "e-e-e-Cde-e-FeeFd---F-deF-"
    "F-F-deF-F-F-deF-F-g--Fe---"
    "--Cde-g-F-e-d-C---C-a---e-"
    "--F-----eFa-a-F-d-----b---"
    "a-F-d-F-e-----eFa-a-F-d---"
)

# =============================================================
# CHANNEL 2 - HARMONY (Pulse wave, 25% duty for thinner sound)
# =============================================================
# Simplified counter-melody / harmony in octave 4
ch2_map = {
    'd': NOTE_FREQ['D4'], 'e': NOTE_FREQ['E4'], 'F': NOTE_FREQ['F#4'],
    'g': NOTE_FREQ['G4'], 'a': NOTE_FREQ['A4'], 'b': NOTE_FREQ['B4'],
    'C': NOTE_FREQ['C#4'],
    # Higher octave variants
    'D': NOTE_FREQ['D5'], 'E': NOTE_FREQ['E5'], 'H': NOTE_FREQ['F#5'],
}

ch2_notation = (
    "a---F---a---F---a---F---g---"
    "e-------a---g---a---g---a---"
    "g-F-e-F-d-------F---a---F---"
    "a---F---a---g---e-------a-g-"
    "F-d-a-------F---C---d-------"
    "F---d---b-------g---d-F-e---"
    "----F---d---b-------g-a-d---"
    "a---F---g---e-------a---g-a-"
    "g---a---g-F-e-F-d-------F---"
    "a---F---a---F---a---g---e---"
    "----a-g-F-d-a-------F---C---"
    "d-------F---d---b-------g---"
    "d-F-e-------F---d---b-------"
)

# =============================================================
# CHANNEL 3 - BASS (Wave channel, octave 3)
# =============================================================
ch3_map = {
    'd': NOTE_FREQ['D3'], 'e': NOTE_FREQ['E3'], 'F': NOTE_FREQ['F#3'],
    'g': NOTE_FREQ['G3'], 'a': NOTE_FREQ['A3'], 'b': NOTE_FREQ['B3'],
    'C': NOTE_FREQ['C#3'],
}

# Bass follows chord roots: D - A - Bm - F#m - G - D - G - A pattern
ch3_notation = (
    "d---d---d---d---d---d---g---"
    "a-------a---a---a---a---a---"
    "g---F---d-------d---d---d---"
    "d---d---d---g---a-------a-a-"
    "F-d-a-------F---C---d-------"
    "d---d---b-------g---g-a-a---"
    "....F---d---b-------b-a-d---"
    "d---d---g---a-------a---a-a-"
    "a---a---g---F---d-------d---"
    "d---d---d---d---d---g---a---"
    "----a-a-F-d-a-------F---C---"
    "d-------d---d---b-------g---"
    "g-a-a-------d---d---b-------"
)

# =============================================================
# CHANNEL 4 - NOISE (Percussion hits on beats)
# =============================================================
# Simple hi-hat pattern: x on beat, . off
ch4_pattern = "x...x...x...x..." * 26  # repeat for full length


def main():
    print("🎮 Pokemon Red - Route 1 (Multi-channel Game Boy style)")
    print("   Ch1: Pulse 50% (melody)")
    print("   Ch2: Pulse 25% (harmony)")
    print("   Ch3: Wave (bass)")
    print("   Ch4: Noise (percussion)")
    print()

    # Render each channel
    print("Rendering channels...")

    ch1_notes = parse_melody(ch1_notation, ch1_map)
    ch1_audio = render_channel(ch1_notes, square_wave, duty=0.5, volume=0.20)

    ch2_notes = parse_melody(ch2_notation, ch2_map)
    ch2_audio = render_channel(ch2_notes, square_wave, duty=0.25, volume=0.12)

    ch3_notes = parse_melody(ch3_notation, ch3_map)
    ch3_audio = render_channel(ch3_notes, wave_channel, volume=0.15)

    # Noise channel
    ch4_audio = np.array([], dtype=np.float64)
    for ch in ch4_pattern:
        dur = STEP
        if ch == 'x':
            ch4_audio = np.append(ch4_audio, noise_channel(dur, volume=0.06))
        else:
            ch4_audio = np.append(ch4_audio, np.zeros(int(SAMPLE_RATE * dur)))

    # Match lengths
    max_len = max(len(ch1_audio), len(ch2_audio), len(ch3_audio), len(ch4_audio))
    ch1_audio = np.pad(ch1_audio, (0, max_len - len(ch1_audio)))
    ch2_audio = np.pad(ch2_audio, (0, max_len - len(ch2_audio)))
    ch3_audio = np.pad(ch3_audio, (0, max_len - len(ch3_audio)))
    ch4_audio = np.pad(ch4_audio, (0, max_len - len(ch4_audio)))

    # Mix all channels
    mixed = ch1_audio + ch2_audio + ch3_audio + ch4_audio

    # Normalize to prevent clipping
    peak = np.max(np.abs(mixed))
    if peak > 0:
        mixed = mixed / peak * 0.85

    # Convert to 16-bit PCM
    mixed_16bit = np.clip(mixed * 32767, -32768, 32767).astype(np.int16)

    # Write WAV file
    output_file = "/tmp/pokemon_route1.wav"
    with wave.open(output_file, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(mixed_16bit.tobytes())

    duration = max_len / SAMPLE_RATE
    print(f"Generated {duration:.1f}s of audio -> {output_file}")
    print("Playing...")
    print()

    # Play with afplay (macOS)
    subprocess.run(["afplay", output_file])
    print("\nDone!")


if __name__ == "__main__":
    main()
