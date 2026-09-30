# 📚 Campus Companion

**Your AI-powered study assistant — runs 100% locally, no internet required.**

Scan notes from textbooks, ask questions in English/Hindi/Hinglish, get AI-generated summaries, step-by-step explanations, and practice questions — all powered by on-device AI.

---

## ✨ Features

| Feature | Engine | Description |
|---|---|---|
| 📷 **OCR** | EasyOCR | Extract text from photos of textbooks & handwritten notes (English + Hindi) |
| 🎤 **Voice Input** | Whisper (faster-whisper) | Speak your questions — supports English, Hindi, and Hinglish |
| 🧠 **AI Answers** | Qwen 2.5 Coder 7B (via Llamafile) | Summaries, step-by-step explanations, and fill-in-the-blank practice sets |

Everything runs **locally on CPU** — optimized for **Snapdragon X Elite** laptops but works on any Windows/macOS/Linux machine.

---

## 📋 Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Git** (optional) — to clone the repo
- ~**5 GB free disk space** — for the Qwen 2.5 Coder model file

---

## 🚀 Setup (One-Time)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/campus-companion.git
cd campus-companion
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** On first run, EasyOCR will download its language models (~100 MB). This only happens once.

### 3. Download the LLM Model & Llamafile

Download these two files and place them in the `local ai/` folder:

| File | Size | Download |
|---|---|---|
| `llamafile-0.10.6.exe` | ~350 MB | [GitHub Releases](https://github.com/Mozilla-Ocho/llamafile/releases/tag/0.10.6) |
| `qwen2.5-coder-7b-instruct-q4_0.gguf` | ~4.1 GB | [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF) |

Your `local ai/` folder should look like:
```
local ai/
├── llamafile-0.10.6.exe
├── qwen2.5-coder-7b-instruct-q4_0.gguf
├── start.bat
└── startcamp.bat
```

---

## ▶️ How to Run

You need **two terminals** — one for the LLM server, one for the backend.

### Terminal 1 — Start the LLM Server

```bash
cd "local ai"
start.bat
```

Wait until you see a message like `listening on http://127.0.0.1:8081`. This means the Qwen model is loaded and ready.

> **Tip:** Use `startcamp.bat` instead if you want lower memory usage (16K context instead of 20K).

### Terminal 2 — Start the Backend

```bash
python app.py
```

Wait for these startup messages:
```
[Backend] Platform: AARCH64 | OS: Windows ...
[Backend] Initializing EasyOCR (en, hi)...
[Backend] Initializing Whisper...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Open the App

Open your browser and go to:

```
http://127.0.0.1:8000
```

You should see the Campus Companion landing page with the "Start Studying" button.

---

## ✅ How to Verify Everything Works

### Step 1 — Check the Landing Page
- Open `http://127.0.0.1:8000` in your browser
- You should see the dark-themed landing page with three feature cards
- The bottom should say **"Local Backend: Connected"**

### Step 2 — Test OCR (Camera Tab)
- Click **"Start Studying"**
- In the Camera tab, click **"Choose Photos"** and upload a photo of printed/handwritten text
- Click **"Read text"** on the photo thumbnail
- The extracted text should appear in the **Notes** tab

### Step 3 — Test Voice Input (Notes Tab)
- Go to the **Notes** tab
- Select a language (English or Hindi)
- Click **"🎤 Mic"** and speak for ~4 seconds
- Your transcription should appear in the question box

### Step 4 — Test AI Answers (Answers Tab)
- Make sure you have some text in the Notes textarea
- Go to the **Answers** tab
- Click **"📋 Summary"** — should generate a bulleted summary
- Click **"💡 Explain"** — should give a step-by-step explanation
- Click **"✏️ Practice"** — should generate fill-in-the-blank questions

### Step 5 — Test Copy
- After an answer is generated, click **"📋 Copy to Clipboard"**
- You should see a **"Copied"** toast notification

> If any step fails, check the terminal running `app.py` for error messages.

---

## 📁 Project Structure

```
campus-companion/
├── app.py                  # FastAPI backend (OCR, STT, LLM proxy)
├── requirements.txt        # Python dependencies
├── static/
│   └── index.html          # Frontend (single-page app)
└── local ai/
    ├── llamafile-0.10.6.exe            # LLM runtime
    ├── qwen2.5-coder-7b-instruct-q4_0.gguf  # LLM model weights
    ├── start.bat            # Launch LLM server (20K context)
    └── startcamp.bat        # Launch LLM server (16K context, lower RAM)
```

---

## ⚙️ Configuration

### Snapdragon X Elite (Default)
The batch files are pre-tuned for Snapdragon X Elite:
- **Threads:** 10 (out of 12 cores, leaving 2 for OS + backend)
- **GPU layers:** 0 (no CUDA; Adreno GPU via Vulkan is experimental)

### Intel / AMD Laptops
Edit `start.bat` and adjust:
```
--threads 6          (set to your core count minus 2)
--n-gpu-layers 0     (set to 99 if you have an NVIDIA GPU with CUDA)
```

### macOS / Linux
Llamafile works cross-platform. Rename `llamafile-0.10.6.exe` to `llamafile-0.10.6` and run:
```bash
chmod +x llamafile-0.10.6
./llamafile-0.10.6 --server --model "qwen2.5-coder-7b-instruct-q4_0.gguf" --host 127.0.0.1 --port 8081 --threads 10 --ctx-size 20000
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| Blank page at `localhost:8000` | Make sure `static/index.html` exists |
| "Llamafile server is not running on port 8081" | Start the LLM server first (`start.bat`) |
| OCR returns no text | Try clearer lighting and a sharper photo |
| Mic doesn't work | Allow microphone permissions in your browser |
| Slow LLM responses | Increase `--threads` or use `startcamp.bat` (smaller context = faster) |
| `pip install` fails | Try `pip install --upgrade pip` first, then retry |

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) — OCR engine
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Speech-to-text
- [Llamafile](https://github.com/Mozilla-Ocho/llamafile) — Local LLM runtime
- [Qwen 2.5 Coder](https://huggingface.co/Qwen) — Language model
- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework
