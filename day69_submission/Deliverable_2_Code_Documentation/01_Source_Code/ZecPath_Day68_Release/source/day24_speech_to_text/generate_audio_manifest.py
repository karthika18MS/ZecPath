
import csv
from pathlib import Path

import soundfile as sf

AUDIO_DIR = Path(__file__).resolve().parent / "audio"
OUTPUT_FILE = AUDIO_DIR / "audio_manifest.csv"

TARGET_SNR = {
    "clean": None,
    "low_noise": 25,
    "medium_noise": 12,
    "high_noise": 0,
}

rows = []

for audio_file in sorted(AUDIO_DIR.glob("*.wav")):
    parts = audio_file.stem.split("_")
    accent = parts[0]
    noise_level = "_".join(parts[1:])

    info = sf.info(str(audio_file))

    rows.append({
        "filename": audio_file.name,
        "accent": accent,
        "noise_level": noise_level,
        "sample_rate": info.samplerate,
        "duration_seconds": round(info.duration, 2),
        "target_snr_db": TARGET_SNR.get(noise_level),
        "format": info.format,
        "subtype": info.subtype,
    })

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Audio manifest created:", OUTPUT_FILE)
print("Total audio records:", len(rows))
print("MANIFEST GENERATION SUCCESSFUL")
