"""
PDF Processor
Extracts text from PDF files using PyMuPDF (fitz).
"""

import os


def extract_text_from_pdf(filepath: str) -> str:
    """
    Extract all text from a PDF file.

    Args:
        filepath: Path to the PDF file.

    Returns:
        Extracted text as a string, or empty string on failure.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("[ERROR] PyMuPDF is not installed. Run: pip install pymupdf")
        return ""

    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return ""

    text_parts = []

    try:
        doc = fitz.open(filepath)
        print(f"[INFO] PDF has {len(doc)} page(s).")

        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)

        doc.close()

        full_text = "\n".join(text_parts).strip()

        if not full_text:
            print("[WARNING] No extractable text found in PDF (may be scanned/image-based).")
            return ""

        print(f"[INFO] Extracted {len(full_text)} characters from PDF.")
        return full_text

    except Exception as e:
        print(f"[ERROR] Failed to process PDF: {e}")
        return ""
