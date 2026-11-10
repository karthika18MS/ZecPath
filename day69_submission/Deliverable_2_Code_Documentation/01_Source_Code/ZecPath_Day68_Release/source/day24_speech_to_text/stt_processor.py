from faster_whisper import WhisperModel


class SpeechToTextProcessor:
    """
    Converts audio input into text using the Faster-Whisper model.
    """

    def __init__(self, model_size="base"):
        """
        Initialize the Faster-Whisper model.

        Args:
            model_size (str): Whisper model size.
                              Examples: tiny, base, small
        """

        self.model_size = model_size

        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path):
        """
        Transcribe an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            dict: Structured transcription result.
        """

        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5
        )

        transcript_parts = []
        segment_data = []

        for segment in segments:

            text = segment.text.strip()

            if text:

                transcript_parts.append(text)

                segment_data.append({
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": text
                })

        full_transcript = " ".join(
            transcript_parts
        )

        return {
            "language": info.language,
            "language_probability": round(
                info.language_probability,
                4
            ),
            "text": full_transcript,
            "segments": segment_data
        }