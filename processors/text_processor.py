"""
Text File Processor
Reads plain text files (.txt).
"""

import os


def extract_text_from_txt(filepath: str) -> str:
    """
    Read content from a plain text file.

    Args:
        filepath: Path to the .txt file.

    Returns:
        File content as a string, or empty string on failure.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return ""

    try:
        # Try UTF-8 first, fall back to latin-1
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(filepath, "r", encoding="latin-1") as f:
                text = f.read()

        text = text.strip()

        if not text:
            print(f"[WARNING] File is empty: {filepath}")
            return ""

        print(f"[INFO] Extracted {len(text)} characters from text file.")
        return text

    except Exception as e:
        print(f"[ERROR] Failed to read text file: {e}")
        return ""
