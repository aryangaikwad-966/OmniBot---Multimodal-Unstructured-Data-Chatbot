"""
Video Processor
Extracts audio from video files and transcribes it to text.
Uses moviepy to extract audio, then passes it to the audio processor.
"""

import os
import tempfile

SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"}


def extract_text_from_video(filepath: str) -> str:
    """
    Extract audio from a video file and transcribe it to text.

    Pipeline:
        Video file  →  Extract audio (WAV)  →  Transcribe audio  →  Text

    Args:
        filepath: Path to the video file.

    Returns:
        Transcribed text, or empty string on failure.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return ""

    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"[WARNING] Unsupported video format: {ext}")
        return ""

    # Try moviepy
    try:
        from moviepy import VideoFileClip  # type: ignore
    except ImportError:
        try:
            from moviepy.editor import VideoFileClip  # type: ignore
        except ImportError:
            print("[ERROR] moviepy is not installed. Run: pip install moviepy")
            print("[INFO] Also ensure FFmpeg is installed:")
            print("       macOS  : brew install ffmpeg")
            print("       Ubuntu : sudo apt install ffmpeg")
            print("       Windows: https://ffmpeg.org/download.html")
            return ""

    # Create a temp file for the extracted audio
    temp_audio_path = None
    try:
        print("[INFO] Extracting audio from video...")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_audio_path = tmp.name

        clip = VideoFileClip(filepath)

        if clip.audio is None:
            print("[WARNING] Video has no audio track.")
            clip.close()
            return ""

        clip.audio.write_audiofile(temp_audio_path, logger=None)
        clip.close()

        print("[INFO] Audio extracted. Now transcribing...")

        # Import here to avoid circular imports
        from processors.audio_processor import extract_text_from_audio
        text = extract_text_from_audio(temp_audio_path)

        return text

    except Exception as e:
        print(f"[ERROR] Video processing failed: {e}")
        return ""

    finally:
        # Always clean up the temp audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
