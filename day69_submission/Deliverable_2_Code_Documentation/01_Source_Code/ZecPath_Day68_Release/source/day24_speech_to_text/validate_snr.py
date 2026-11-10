
from pathlib import Path

import numpy as np
import soundfile as sf

AUDIO_DIR = Path(__file__).resolve().parent / "audio"

ACCENTS = ["indian", "american", "british"]

NOISE_LEVELS = {
    "low_noise": 25,
    "medium_noise": 12,
    "high_noise": 0,
}


def calculate_snr(clean, noisy):
    # Difference between noisy and original clean signal
    noise = noisy - clean

    signal_power = np.mean(clean ** 2)
    noise_power = np.mean(noise ** 2)

    if noise_power == 0:
        return float("inf")

    return 10 * np.log10(signal_power / noise_power)


print("\nACTUAL SNR VALIDATION")
print("=" * 80)

results = []

for accent in ACCENTS:
    clean_path = AUDIO_DIR / f"{accent}_clean.wav"
    clean, clean_sr = sf.read(clean_path, dtype="float64")

    for noise_level, target_snr in NOISE_LEVELS.items():
        noisy_path = AUDIO_DIR / f"{accent}_{noise_level}.wav"
        noisy, noisy_sr = sf.read(noisy_path, dtype="float64")

        if clean_sr != noisy_sr or len(clean) != len(noisy):
            print(f"ERROR: Audio mismatch for {accent} - {noise_level}")
            continue

        actual_snr = calculate_snr(clean, noisy)

        results.append({
            "accent": accent,
            "noise_level": noise_level,
            "target_snr": target_snr,
            "actual_snr": actual_snr,
        })

        print(
            f"{accent:10} | {noise_level:12} | "
            f"Target: {target_snr:5} dB | "
            f"Actual: {actual_snr:7.2f} dB"
        )

print("=" * 80)
print(f"Total SNR measurements: {len(results)}")
