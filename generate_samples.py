"""
generate_samples.py
Generates demo sample files for all supported types:
  - sample_data_science.pdf
  - sample_notes.png  (image with text, for OCR demo)
  - sample_intro.mp3  (audio, for speech-to-text demo)

Run this once before demonstrating the chatbot:
    python3 generate_samples.py
"""

import os
import sys

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_files")
os.makedirs(SAMPLE_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# Content blocks used across all sample files
# ─────────────────────────────────────────────

PDF_CONTENT = """Data Science - Core Concepts

Data Science is an interdisciplinary field that combines statistics, mathematics,
programming, and domain knowledge to extract meaningful insights from data.
Data scientists work with both structured data (tables, databases) and unstructured
data (text, images, audio, video).

The Data Science Workflow
--------------------------
1. Data Collection  - Gathering raw data from various sources.
2. Data Cleaning    - Handling missing values, duplicates, and outliers.
3. Exploratory Data Analysis (EDA) - Understanding patterns using statistics and plots.
4. Feature Engineering - Transforming raw data into useful features for models.
5. Model Building   - Training machine learning models on prepared data.
6. Model Evaluation - Measuring accuracy, precision, recall, and F1-score.
7. Deployment       - Serving the model in a real-world application.

Key Python Libraries for Data Science
---------------------------------------
- NumPy   : Numerical computing with arrays and matrices.
- pandas  : Data manipulation and analysis with DataFrames.
- Matplotlib and Seaborn : Data visualization.
- scikit-learn : Machine learning algorithms and utilities.
- TensorFlow and PyTorch : Deep learning frameworks.

Statistics in Data Science
---------------------------
Statistics is the foundation of data science. Key concepts include:
- Mean, Median, Mode : Measures of central tendency.
- Variance and Standard Deviation : Measures of spread.
- Probability Distributions : Normal, Binomial, Poisson.
- Hypothesis Testing : t-test, chi-square test, ANOVA.
- Correlation and Regression : Measuring relationships between variables.

Big Data Technologies
----------------------
When data is too large to fit in memory, we use distributed systems such as:
- Apache Hadoop  : Distributed storage and processing.
- Apache Spark   : Fast in-memory distributed computing.
- Apache Kafka   : Real-time data streaming.
"""

IMAGE_TEXT = """Python Programming Basics

Variables store data values.
x = 10
name = "Alice"

Lists store multiple items.
fruits = ["apple", "banana", "mango"]

Loops repeat code.
for i in range(5):
    print(i)

Functions reuse code.
def greet(name):
    return "Hello " + name

Classes define objects.
class Dog:
    def bark(self):
        print("Woof!")

Python is easy to learn.
Python is used in AI and Data Science.
NumPy and pandas are popular libraries.
"""

AUDIO_TEXT = (
    "Hello. This is a sample audio file for the OmniBot - Multimodal Unstructured Data Chatbot. "
    "It uses TF-IDF vectorization and cosine similarity to answer questions from uploaded files. "
    "Supported file types include PDF, text files, images, audio, and video. "
    "The system extracts text from each file, creates a knowledge base, "
    "and retrieves the most relevant answers to your questions. "
    "Thank you."
)

VIDEO_AUDIO_TEXT = (
    "Welcome to a short lesson on Quantum Computing. "
    "Unlike classical computers that use bits to represent zero or one, "
    "quantum computers use quantum bits, or qubits. "
    "Qubits can exist in multiple states simultaneously due to superposition. "
    "They also utilize quantum entanglement to link states together. "
    "This makes quantum computing extremely powerful for complex problem solving."
)


# ─────────────────────────────────────────────
# 1. Generate PDF
# ─────────────────────────────────────────────

def generate_pdf():
    pdf_path = os.path.join(SAMPLE_DIR, "sample_data_science.pdf")
    try:
        import fitz  # PyMuPDF - already installed via requirements.txt
    except ImportError:
        print("[ERROR] PyMuPDF not installed. Run: pip install pymupdf")
        return

    doc = fitz.open()          # new empty PDF
    page = doc.new_page()      # A4 page by default

    # Layout constants
    x_margin = 60
    y = 60
    line_height_body = 16
    line_height_heading = 20
    page_bottom = page.rect.height - 60

    for line in PDF_CONTENT.split("\n"):
        line = line.strip()

        # New page if needed
        if y > page_bottom:
            page = doc.new_page()
            y = 60

        if not line:
            y += 8
            continue

        # Detect headings: short lines with no leading digit, not a bullet
        is_heading = (
            len(line) < 55
            and not line[0].isdigit()
            and not line.startswith("-")
            and not line.startswith(".")
        )

        if is_heading:
            fontsize = 13
            fontname = "helv"
            color = (0.05, 0.2, 0.55)     # dark blue
        else:
            fontsize = 11
            fontname = "helv"
            color = (0.1, 0.1, 0.1)       # near-black

        page.insert_text(
            (x_margin, y),
            line,
            fontname=fontname,
            fontsize=fontsize,
            color=color,
        )
        y += line_height_heading if is_heading else line_height_body

    doc.save(pdf_path)
    doc.close()
    print(f"[OK] PDF created : {pdf_path}")



# ─────────────────────────────────────────────
# 2. Generate Image (PNG with text)
# ─────────────────────────────────────────────

def generate_image():
    img_path = os.path.join(SAMPLE_DIR, "sample_notes.png")
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except ImportError:
        print("[ERROR] Pillow not installed. Run: pip install Pillow")
        return

    # Canvas size
    width, height = 900, 700
    bg_color = (255, 255, 255)       # White background
    text_color = (20, 20, 80)        # Dark navy text
    title_color = (0, 80, 180)       # Blue for title
    border_color = (200, 200, 200)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle([10, 10, width - 10, height - 10], outline=border_color, width=2)

    # Try to load a system font; fall back to default
    font_large = None
    font_normal = None
    font_small = None
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_large  = ImageFont.truetype(fp, 28)
                font_normal = ImageFont.truetype(fp, 18)
                font_small  = ImageFont.truetype(fp, 15)
                break
            except Exception:
                pass

    if font_large is None:
        font_large = font_normal = font_small = ImageFont.load_default()

    # Title
    draw.text((40, 30), "Python Programming – Quick Notes", font=font_large, fill=title_color)
    draw.line([(40, 70), (860, 70)], fill=border_color, width=1)

    # Body text
    y = 90
    line_gap = 26
    for line in IMAGE_TEXT.strip().split("\n"):
        line = line.strip()
        if not line:
            y += 10
            continue
        # Code-like lines (indented / contain =)
        if "=" in line or line.startswith("for") or line.startswith("def") \
                or line.startswith("class") or line.startswith("print") \
                or line.startswith("return"):
            draw.text((60, y), line, font=font_small, fill=(0, 120, 0))
        else:
            draw.text((40, y), line, font=font_normal, fill=text_color)
        y += line_gap
        if y > height - 40:
            break

    img.save(img_path, "PNG")
    print(f"[OK] Image created : {img_path}")


# ─────────────────────────────────────────────
# 3. Generate Audio (MP3 using gTTS)
# ─────────────────────────────────────────────

def generate_audio():
    audio_path = os.path.join(SAMPLE_DIR, "sample_intro.mp3")
    try:
        from gtts import gTTS  # type: ignore
    except ImportError:
        print("[INFO] gTTS not installed. Installing...")
        os.system(f"{sys.executable} -m pip install gtts -q")
        try:
            from gtts import gTTS  # type: ignore
        except ImportError:
            print("[ERROR] Could not install gTTS. Skipping audio generation.")
            print("[TIP]  Alternatively, record a .wav file yourself and place it in sample_files/")
            return

    try:
        tts = gTTS(text=AUDIO_TEXT, lang="en", slow=False)
        tts.save(audio_path)
        print(f"[OK] Audio created : {audio_path}")
        print("[NOTE] Audio file requires internet for gTTS generation (done once).")
        print("       Transcription during chatbot run uses local Whisper (offline).")
    except Exception as e:
        print(f"[ERROR] Audio generation failed: {e}")
        print("[TIP]  Check your internet connection (gTTS requires internet to generate audio).")


# ─────────────────────────────────────────────
# 4. Generate Video (MP4 using moviepy)
# ─────────────────────────────────────────────

def generate_video():
    video_path = os.path.join(SAMPLE_DIR, "sample_video.mp4")
    temp_image = os.path.join(SAMPLE_DIR, "temp_video_frame.png")
    temp_audio = os.path.join(SAMPLE_DIR, "temp_video_audio.mp3")

    try:
        from moviepy import ImageClip, AudioFileClip  # type: ignore
        from PIL import Image, ImageDraw, ImageFont # type: ignore
        from gtts import gTTS # type: ignore
    except ImportError:
        print("[INFO] moviepy, gTTS, or PIL not installed. Skipping unique video generation.")
        return

    # 1. Create a unique frame for the video
    img = Image.new("RGB", (900, 700), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font = ImageFont.load_default()
    draw.text((100, 300), "Lesson: Quantum Computing\n(Video File)", font=font, fill=(200, 255, 255))
    img.save(temp_image, "PNG")

    # 2. Create a unique audio track for the video
    try:
        tts = gTTS(text=VIDEO_AUDIO_TEXT, lang="en", slow=False)
        tts.save(temp_audio)
    except Exception as e:
        print(f"[ERROR] Video audio generation failed: {e}")
        return

    # 3. Stitch them together
    try:
        audio = AudioFileClip(temp_audio)
        clip = ImageClip(temp_image).with_duration(audio.duration)
        clip = clip.with_audio(audio)
        clip.write_videofile(video_path, fps=1, logger=None)
        print(f"[OK] Video created : {video_path}")
    except Exception as e:
        print(f"[ERROR] Video generation failed: {e}")
    finally:
        # Cleanup temporary files
        if os.path.exists(temp_image): os.remove(temp_image)
        if os.path.exists(temp_audio): os.remove(temp_audio)

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 52)
    print("  Generating Sample Files for Demo")
    print("=" * 52)
    print()

    print(">>> Generating PDF...")
    generate_pdf()
    print()

    print(">>> Generating Image (PNG)...")
    generate_image()
    print()

    print(">>> Generating Audio (MP3)...")
    generate_audio()
    print()

    print(">>> Generating Video (MP4)...")
    generate_video()
    print()

    print("=" * 52)
    print("  Done! Files saved in: sample_files/")
    print()
    print("  sample_lecture.txt        (already existed)")
    print("  sample_data_science.pdf   (new)")
    print("  sample_notes.png          (new – use with OCR)")
    print("  sample_intro.mp3          (new – use with Whisper)")
    print("  sample_video.mp4          (new – use with Whisper & moviepy)")
    print("=" * 52)
    print()
    print("  Now run: python3 main.py")
    print()
