"""
Audio Processor
Transcribes audio files (WAV, MP3, M4A) to text using OpenAI Whisper (local model).
Falls back to SpeechRecognition + Google API if Whisper is not installed.
"""

import os

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}


def _transcribe_with_whisper(filepath: str) -> str:
    """Transcribe audio using the local Whisper model."""
    import whisper  # type: ignore

    print("[INFO] Loading Whisper model (base) – first run may take a moment...")
    model = whisper.load_model("base")
    print("[INFO] Transcribing audio with Whisper...")
    result = model.transcribe(filepath)
    return result.get("text", "").strip()


def _transcribe_with_speechrecognition(filepath: str) -> str:
    """
    Fallback transcription using SpeechRecognition library.
    Supports only WAV natively; converts other formats via pydub if available.
    """
    import speech_recognition as sr  # type: ignore

    recognizer = sr.Recognizer()

    # If not WAV, try to convert using pydub
    ext = os.path.splitext(filepath)[1].lower()
    wav_path = filepath

    if ext != ".wav":
        try:
            from pydub import AudioSegment  # type: ignore
            print(f"[INFO] Converting {ext} to WAV using pydub...")
            audio = AudioSegment.from_file(filepath)
            wav_path = filepath.rsplit(".", 1)[0] + "_converted.wav"
            audio.export(wav_path, format="wav")
        except ImportError:
            print("[WARNING] pydub not installed. Only WAV files are supported without pydub.")
            return ""
        except Exception as conv_err:
            print(f"[ERROR] Audio conversion failed: {conv_err}")
            return ""

    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        print("[INFO] Transcribing with Google Speech Recognition (requires internet)...")
        text = recognizer.recognize_google(audio_data)
        return text.strip()

    except sr.UnknownValueError:
        print("[WARNING] Speech could not be understood.")
        return ""
    except sr.RequestError as e:
        print(f"[ERROR] Speech recognition service error: {e}")
        return ""
    finally:
        # Clean up temp WAV file
        if wav_path != filepath and os.path.exists(wav_path):
            os.remove(wav_path)


def extract_text_from_audio(filepath: str) -> str:
    """
    Transcribe audio to text.
    Tries Whisper first (local, offline). Falls back to SpeechRecognition.

    Args:
        filepath: Path to the audio file.

    Returns:
        Transcribed text, or empty string on failure.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return ""

    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"[WARNING] Unsupported audio format: {ext}")
        return ""

    # --- Try Whisper (preferred: local, no API needed) ---
    try:
        text = _transcribe_with_whisper(filepath)
        if text:
            print(f"[INFO] Extracted {len(text)} characters from audio (Whisper).")
            return text
        else:
            print("[WARNING] Whisper returned empty transcript.")
    except ImportError:
        print("[INFO] Whisper not installed. Trying SpeechRecognition fallback...")
        print("[TIP]  Install Whisper for better results: pip install openai-whisper")
    except Exception as e:
        print(f"[WARNING] Whisper transcription error: {e}. Trying fallback...")

    # --- Fallback: SpeechRecognition ---
    try:
        text = _transcribe_with_speechrecognition(filepath)
        if text:
            print(f"[INFO] Extracted {len(text)} characters from audio (SpeechRecognition).")
            return text
    except ImportError:
        print("[ERROR] SpeechRecognition not installed. Run: pip install SpeechRecognition")
    except Exception as e:
        print(f"[ERROR] Audio transcription failed: {e}")

    return ""
