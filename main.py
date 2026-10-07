"""
main.py – Multimodal Unstructured Data Chatbot
DS Lab Experiment 12 – Mini Project

Pipeline:
    User provides file paths
    → File type detected
    → Text extracted per file type (PDF/TXT/Image/Audio/Video)
    → Text chunked with metadata
    → TF-IDF index built over all chunks
    → User asks questions
    → Cosine similarity retrieval
    → Extractive answer displayed with source
"""

import os
import sys

# Ensure processors and retrieval modules are importable
# regardless of where the script is run from.
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from processors.pdf_processor   import extract_text_from_pdf
from processors.text_processor  import extract_text_from_txt
from processors.image_processor import extract_text_from_image
from processors.audio_processor import extract_text_from_audio
from processors.video_processor import extract_text_from_video
from retrieval.tfidf_retriever  import TFIDFRetriever, chunk_text


# ─────────────────────────────────────────────
# File Type Detection
# ─────────────────────────────────────────────

# Map file extensions → (display_name, processor_function, file_type_tag)
EXTENSION_MAP = {
    # PDF
    ".pdf": ("PDF", extract_text_from_pdf, "pdf"),

    # Plain text
    ".txt": ("TXT", extract_text_from_txt, "txt"),

    # Images
    ".jpg":  ("IMAGE", extract_text_from_image, "image"),
    ".jpeg": ("IMAGE", extract_text_from_image, "image"),
    ".png":  ("IMAGE", extract_text_from_image, "image"),
    ".bmp":  ("IMAGE", extract_text_from_image, "image"),
    ".tiff": ("IMAGE", extract_text_from_image, "image"),

    # Audio
    ".wav":  ("AUDIO", extract_text_from_audio, "audio"),
    ".mp3":  ("AUDIO", extract_text_from_audio, "audio"),
    ".m4a":  ("AUDIO", extract_text_from_audio, "audio"),
    ".ogg":  ("AUDIO", extract_text_from_audio, "audio"),
    ".flac": ("AUDIO", extract_text_from_audio, "audio"),

    # Video
    ".mp4": ("VIDEO", extract_text_from_video, "video"),
    ".mkv": ("VIDEO", extract_text_from_video, "video"),
    ".avi": ("VIDEO", extract_text_from_video, "video"),
    ".mov": ("VIDEO", extract_text_from_video, "video"),
}


# ─────────────────────────────────────────────
# Banner / UI helpers
# ─────────────────────────────────────────────

SEPARATOR = "=" * 52

def print_banner():
    print()
    print(SEPARATOR)
    print("           OmniBot")
    print("   Ask Anything From Any File")
    print(SEPARATOR)
    print()
    print("  Supported file types:")
    print("  PDF | TXT | IMAGE (jpg/png) | AUDIO (wav/mp3)")
    print("  VIDEO (mp4/mkv/avi)")
    print()


def print_separator():
    print(SEPARATOR)


# ─────────────────────────────────────────────
# File Processing
# ─────────────────────────────────────────────

def process_file(filepath: str, retriever: TFIDFRetriever) -> bool:
    """
    Detect file type, extract text, chunk it, and add to the retriever.

    Args:
        filepath : Absolute or relative path to the file.
        retriever: The TFIDFRetriever instance to add chunks to.

    Returns:
        True if the file was processed successfully, False otherwise.
    """
    filepath = filepath.strip()

    # Validate file existence
    if not os.path.exists(filepath):
        print(f"[ERROR] File does not exist: {filepath}")
        return False

    if not os.path.isfile(filepath):
        print(f"[ERROR] Path is not a file: {filepath}")
        return False

    ext = os.path.splitext(filepath)[1].lower()
    filename = os.path.basename(filepath)

    if ext not in EXTENSION_MAP:
        print(f"[ERROR] Unsupported file type: '{ext}'")
        print(f"        Supported types: {', '.join(sorted(EXTENSION_MAP.keys()))}")
        return False

    display_name, processor_fn, file_type = EXTENSION_MAP[ext]

    print(f"[INFO] Processing {display_name}: {filename}")

    # Extract text
    extracted_text = processor_fn(filepath)

    if not extracted_text or not extracted_text.strip():
        print(f"[WARNING] No text could be extracted from: {filename}")
        return False

    # Chunk the text and add to retriever
    chunks = chunk_text(
        text=extracted_text,
        source=filename,
        file_type=file_type,
        chunk_size=150,   # ~150 words per chunk
        overlap=30        # 30-word overlap between consecutive chunks
    )

    if not chunks:
        print(f"[WARNING] Text extraction succeeded but chunking produced no chunks for: {filename}")
        return False

    retriever.add_chunks(chunks)
    print(f"[INFO] Successfully processed '{filename}' → {len(chunks)} chunk(s) added.")
    return True


# ─────────────────────────────────────────────
# File Collection Loop
# ─────────────────────────────────────────────

def collect_files(retriever: TFIDFRetriever) -> int:
    """
    Interactively ask the user to provide file paths until they type 'done'.

    Returns:
        Number of successfully processed files.
    """
    print("Enter file path(s) one by one.")
    print("Type 'done' when finished.\n")

    processed_count = 0

    while True:
        try:
            raw_input = input("File path > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Input interrupted.")
            break

        if not raw_input:
            print("[INFO] Please enter a file path or type 'done'.")
            continue

        if raw_input.lower() == "done":
            break

        success = process_file(raw_input, retriever)
        if success:
            processed_count += 1

        print()  # blank line for readability

    return processed_count


# ─────────────────────────────────────────────
# Question-Answering Loop
# ─────────────────────────────────────────────

def chat_loop(retriever: TFIDFRetriever):
    """
    Interactively answer user questions using TF-IDF cosine similarity retrieval.
    """
    print()
    print("You can now ask questions about the uploaded files.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Chat interrupted.")
            break

        if not question:
            print("[INFO] Please enter a question.\n")
            continue

        if question.lower() in {"exit", "quit", "q", "bye"}:
            break

        # Get answer using TF-IDF retrieval
        answer_text, source = retriever.answer(question)

        print()
        print(f"Bot: {answer_text}")

        if source:
            print(f"\nSource: {source}")

        print()


# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────

def main():
    print_banner()

    # Initialize the retriever
    retriever = TFIDFRetriever(
        similarity_threshold=0.05,  # Minimum similarity to return a result
        top_k=3                     # Number of top chunks to consider
    )

    # ── Step 1: Collect files ──
    processed_count = collect_files(retriever)

    if processed_count == 0:
        print_separator()
        print("[ERROR] No files were successfully processed. Exiting.")
        print_separator()
        return

    # ── Step 2: Build TF-IDF index ──
    print_separator()
    print(f"  Building knowledge base from {processed_count} file(s)...")
    print(f"  Total chunks: {retriever.chunk_count}")

    success = retriever.build_index()

    if not success:
        print("[ERROR] Failed to build the knowledge base. Exiting.")
        print_separator()
        return

    print()
    print("  Knowledge base created successfully!")
    print(f"  Files processed : {retriever.document_count}")
    print(f"  Total chunks    : {retriever.chunk_count}")
    print_separator()

    # ── Step 3: Chat loop ──
    chat_loop(retriever)

    # ── Step 4: Exit message ──
    print()
    print_separator()
    print("  Chatbot terminated. Goodbye!")
    print_separator()
    print()


if __name__ == "__main__":
    main()
