<div align="center">

# OmniBot

### Multimodal Unstructured Data Chatbot

Read PDFs, notes, images, audio, and videos from a simple terminal chat.

`Python` · `TF-IDF Search` · `OCR` · `Whisper`

[Get started](#get-started) · [Supported files](#supported-files) · [Help](#help--troubleshooting)

</div>

---

## Browser experience

Omni includes a local browser interface powered by the Cloudee avatar definition. The assistant stays visible in the center of the page and continuously cycles through its expressions while it is idle.

![Omni Cloudee-style assistant avatar](frontend/omni-avatar.svg)

### What the browser UI does

| UI area | Behavior |
|---|---|
| Omni avatar | Continuously animates through the expressions from `cloudee.avatar.json` |
| Assistant status | Shows whether Omni is available, listening, thinking, searching, excited, or suspicious |
| Add files | Uploads one or more supported files to the local knowledge base |
| Chat box | Sends questions to the local TF-IDF retriever |
| Source label | Shows which uploaded file supplied the answer |

Omni changes animation automatically:

```text
Idle        → continuous expression cycle
Focus input → listening
Typing      → thinking
Uploading   → listening
Searching   → searching
Answer      → excited
Error       → suspicious
```

No cloud account or API key is required. The browser server, extracted text, uploaded files, and search index stay on your computer while the app is running.

### Start the browser UI

```zsh
cd "/Users/aryangaikwad/Desktop/OmniBot - Multimodal Unstructured Data Chatbot"
python3 web_app.py
```

Open [http://localhost:8000](http://localhost:8000), select **Add files**, and ask Omni a question.

The browser frontend is made from:

- `frontend/index.html` — page structure and assistant layout
- `frontend/style.css` — responsive cloud UI and floating animation
- `frontend/app.js` — avatar expressions, lifecycle animations, uploads, and chat
- `cloudee.avatar.json` — Cloudee expressions, colors, and animation sequences
- `web_app.py` — local static-file server and API adapter

### Browser API

The frontend uses three local endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/avatar` | GET | Loads the complete Cloudee avatar definition |
| `/api/status` | GET | Returns processed files and index status |
| `/api/upload` | POST | Extracts and indexes uploaded files |
| `/api/ask` | POST | Retrieves an answer and source filename |

Example question request:

```zsh
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is machine learning?"}'
```

---

## What is OmniBot?

OmniBot turns the files you choose into a temporary, searchable knowledge base. Ask a question in plain English and it returns relevant text with the file name it came from.

| | What OmniBot does |
|---|---|
| 📄 | Reads text from TXT and PDF files |
| 🖼️ | Reads text in images with OCR |
| 🎙️ | Converts speech in audio files to text |
| 🎬 | Extracts and searches speech from video files |
| 🔎 | Finds the most relevant answer using TF-IDF search |

No API key is required. Your files are processed locally while the program is running.

### Sample files

The repository includes sample content for trying each supported modality:

![Sample handwritten notes used for OCR](sample_files/sample_notes.png)

| Sample | Type | Try asking |
|---|---|---|
| `sample_files/sample_lecture.txt` | Text | “What is machine learning?” |
| `sample_files/sample_data_science.pdf` | PDF | “What are the steps in the data science workflow?” |
| `sample_files/sample_notes.png` | Image/OCR | “What is a function in Python?” |
| `sample_files/sample_intro.mp3` | Audio | “What does OmniBot use to find answers?” |
| `sample_files/sample_video.mp4` | Video | “What is quantum computing?” |

---

## Get started

### Step 1 — Open the project

Open **Terminal** and copy this command:

```zsh
cd "/Users/aryangaikwad/Desktop/OmniBot - Multimodal Unstructured Data Chatbot"
```

> Use the normal hyphen (`-`) in the folder name, not a long dash (`—`).

### Step 2 — Install OmniBot

Run these commands once:

```zsh
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Install these additional tools once if you will use images, audio, or video:

```zsh
brew install tesseract ffmpeg
```

| Tool | Needed for |
|---|---|
| Tesseract | PNG, JPG, JPEG, BMP, TIFF images |
| FFmpeg | MP3, WAV, M4A, OGG, FLAC audio and MP4/MKV/AVI/MOV video |

### Step 3 — Start a chat

Run this whenever you want to use OmniBot:

```zsh
cd "/Users/aryangaikwad/Desktop/OmniBot - Multimodal Unstructured Data Chatbot"
source venv/bin/activate
python3 main.py
```

OmniBot will ask for a file path:

```text
File path >
```

For the browser experience, see [Browser experience](#browser-experience) above. For the terminal experience, choose a guide below, enter a file path, type `done`, then ask your question.

---

## Supported files

| File type | Extensions | Use it for | Setup |
|---|---|---|---|
| Text | `.txt` | Notes, articles, text documents | Ready to use |
| PDF | `.pdf` | Digital reports and documents | Ready to use |
| Image | `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff` | Screenshots and photographed notes | Tesseract |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` | Lectures and voice notes | FFmpeg |
| Video | `.mp4`, `.mkv`, `.avi`, `.mov` | Lessons and recorded presentations | FFmpeg |

---

## Use a TXT file

Best for notes, articles, and plain text documents.

**1. Start OmniBot**

```zsh
python3 main.py
```

**2. Add the file**

```text
File path > sample_files/sample_lecture.txt
File path > done
```

**3. Ask a question**

```text
You: What is machine learning?
```

Use your own file:

```text
File path > /Users/your-name/Documents/my-notes.txt
```

---

## Use a PDF file

Best for digital PDFs where you can select text using your cursor.

**1. Start OmniBot**

```zsh
python3 main.py
```

**2. Add the file**

```text
File path > sample_files/sample_data_science.pdf
File path > done
```

**3. Ask a question**

```text
You: What are the steps in the data science workflow?
```

Use your own file:

```text
File path > /Users/your-name/Documents/report.pdf
```

> Scanned PDFs are images, so their text cannot be extracted by the current PDF reader. Save the pages as images and use the image guide instead.

---

## Use an image file

Best for screenshots, scanned notes, and images that contain readable text.

**1. Install Tesseract once**

```zsh
brew install tesseract
```

**2. Start OmniBot and add an image**

```zsh
python3 main.py
```

```text
File path > sample_files/sample_notes.png
File path > done
```

**3. Ask a question**

```text
You: What is a function in Python?
```

Use your own image:

```text
File path > /Users/your-name/Desktop/notes.png
```

**Works with:** PNG, JPG, JPEG, BMP, and TIFF.

> For best results, use a clear image with large, dark text and a light background.

---

## Use an audio file

Best for voice notes, lectures, interviews, and recorded explanations.

**1. Install FFmpeg once**

```zsh
brew install ffmpeg
```

**2. Start OmniBot and add an audio file**

```zsh
python3 main.py
```

```text
File path > sample_files/sample_intro.mp3
File path > done
```

**3. Ask a question**

```text
You: What does OmniBot use to find answers?
```

Use your own audio:

```text
File path > /Users/your-name/Music/lecture.mp3
```

**Works with:** MP3, WAV, M4A, OGG, and FLAC.

> Audio is transcribed with Whisper before it is searched. The first transcription can take a little longer while the Whisper model is prepared. The `FP16` / `FP32` message on a Mac is normal.

---

## Use a video file

Best for recorded lessons, presentations, and videos containing spoken audio.

**1. Install FFmpeg once**

```zsh
brew install ffmpeg
```

**2. Start OmniBot and add a video**

```zsh
python3 main.py
```

```text
File path > sample_files/sample_video.mp4
File path > done
```

**3. Ask a question**

```text
You: What is quantum computing?
```

Use your own video:

```text
File path > /Users/your-name/Movies/lesson.mp4
```

**Works with:** MP4, MKV, AVI, and MOV.

> OmniBot searches the spoken audio. A silent video or a video where information appears only on screen cannot be searched yet.

---

## Add several files at once

Mix any supported file types in one chat. Add every file first, then type `done`.

```text
File path > sample_files/sample_lecture.txt
File path > sample_files/sample_data_science.pdf
File path > sample_files/sample_notes.png
File path > sample_files/sample_intro.mp3
File path > sample_files/sample_video.mp4
File path > done
```

Ask your question normally. OmniBot shows the source filename below its answer.

---

## Help & troubleshooting

| Problem | Fix |
|---|---|
| `bad interpreter` when using `pip3` | Recreate the virtual environment using the commands below. |
| `No such file or directory: 'ffmpeg'` or `'ffprobe'` | Run `brew install ffmpeg`, then restart Terminal. |
| Tesseract is not found | Run `brew install tesseract`. |
| `File does not exist` | Check the filename and full path. |
| “I could not find enough relevant information” | Confirm you added the correct file before `done`, then ask with words present in that file. |

### Fix a moved or renamed project

If the project folder was moved after you made `venv`, run:

```zsh
deactivate 2>/dev/null || true
rm -rf venv
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

This deletes only the local `venv` folder, not your project files.

### Audio loads but “OmniBot” is not found

An older demo MP3 may not contain the word **OmniBot**. Recreate the demo file:

```zsh
source venv/bin/activate
python3 generate_samples.py
```

Restart OmniBot, add `sample_files/sample_intro.mp3` again, type `done`, and ask the question again.

---

## How it works

```text
Your file → text extraction → small text chunks → TF-IDF search → answer + source
```

OmniBot only answers from files loaded in the current session. It does not remember files after you exit.

<div align="center">

Built with Python, PyMuPDF, Tesseract, Whisper, and scikit-learn.

</div>
