
import io
import os
from pathlib import Path

import numpy as np
import soundfile as sf
from gtts import gTTS

# Define project-based output directory
PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Utterance for testing
TEXT = (
    "I have three years of experience in backend development. "
    "I have worked with Python, Django, FastAPI, Docker and PostgreSQL."
)

# Accent mapping supported by Google TTS
ACCENTS = {
    "indian": {"tld": "co.in", "lang": "en"},
    "american": {"tld": "us", "lang": "en"},
    "british": {"tld": "co.uk", "lang": "en"},
}

# Target Signal-to-Noise Ratio (SNR) in dB
NOISE_LEVELS = {
    "clean": None,
    "low_noise": 25,
    "medium_noise": 12,
    "high_noise": 0,
}


def add_noise(signal: np.ndarray, target_snr_db: float) -> np.ndarray:
    signal_power = np.mean(signal ** 2)

    if signal_power == 0:
        return signal.copy()

    snr_linear = 10 ** (target_snr_db / 10)
    noise_power = signal_power / snr_linear
    noise = np.random.normal(0, np.sqrt(noise_power), signal.shape)

    mixed = signal + noise
    max_val = np.max(np.abs(mixed))

    if max_val > 1.0:
        mixed = mixed / max_val

    return mixed


for accent_name, config in ACCENTS.items():
    print(f"Synthesizing {accent_name}...")

    # Fetch MP3 stream from gTTS
    tts = gTTS(
        text=TEXT,
        lang=config["lang"],
        tld=config["tld"],
        slow=False
    )

    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Decode MP3
    samples, sample_rate = sf.read(mp3_fp, dtype="float32")

    if samples.ndim > 1:
        samples = samples.mean(axis=1)

    # Save clean and noisy variants
    for noise_name, snr_db in NOISE_LEVELS.items():
        filename = f"{accent_name}_{noise_name}.wav"
        filepath = OUTPUT_DIR / filename

        if snr_db is None:
            output_data = samples
        else:
            output_data = add_noise(samples, snr_db)

        sf.write(
            str(filepath),
            output_data,
            sample_rate,
            subtype="PCM_16"
        )

        print(f"  -> Saved: {filepath}")

print(f"\nCompleted! All 12 files saved inside: {OUTPUT_DIR}")
