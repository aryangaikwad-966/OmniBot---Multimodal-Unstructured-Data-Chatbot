"""
Image Processor
Extracts text from image files (JPG, JPEG, PNG) using OCR via pytesseract.
"""

import os

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


def extract_text_from_image(filepath: str) -> str:
    """
    Extract text from an image using OCR (Optical Character Recognition).

    Args:
        filepath: Path to the image file.

    Returns:
        Extracted text as a string, or empty string on failure.
    """
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("[ERROR] Pillow is not installed. Run: pip install Pillow")
        return ""

    # Check if pytesseract is available
    try:
        import pytesseract
    except ImportError:
        print("[ERROR] pytesseract is not installed. Run: pip install pytesseract")
        print("[INFO] Also install Tesseract OCR engine:")
        print("       macOS  : brew install tesseract")
        print("       Ubuntu : sudo apt install tesseract-ocr")
        print("       Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return ""

    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return ""

    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"[WARNING] Unsupported image format: {ext}")
        return ""

    try:
        image = Image.open(filepath)

        # Convert to RGB if needed (handles RGBA, palette-based images, etc.)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        print("[INFO] Running OCR on image...")
        text = pytesseract.image_to_string(image).strip()

        if not text:
            print("[WARNING] OCR found no readable text in the image.")
            return ""

        print(f"[INFO] Extracted {len(text)} characters from image.")
        return text

    except pytesseract.TesseractNotFoundError:
        print("[ERROR] Tesseract OCR engine is not installed or not in PATH.")
        print("[INFO] Install Tesseract:")
        print("       macOS  : brew install tesseract")
        print("       Ubuntu : sudo apt install tesseract-ocr")
        print("       Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return ""

    except Exception as e:
        print(f"[ERROR] Image processing failed: {e}")
        return ""
