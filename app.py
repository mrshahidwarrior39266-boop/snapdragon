import base64
import io
import os
import platform
import httpx
import numpy as np
from PIL import Image, ImageOps
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import easyocr
from faster_whisper import WhisperModel

app = FastAPI(title="Campus Companion Local Backend")

# Platform info (useful for debugging on Snapdragon ARM64 vs x86)
print(f"[Backend] Platform: {platform.machine()} | OS: {platform.system()} {platform.version()}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. OCR Engine (English + Hindi on CPU)
print("[Backend] Initializing EasyOCR (en, hi)...")
ocr_reader = easyocr.Reader(['en', 'hi'], gpu=False)

# 2. STT Engine (Whisper Base int8 on CPU)
print("[Backend] Initializing Whisper...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# 3. Llamafile Local Endpoint
LLAMAFILE_URL = "http://127.0.0.1:8081/v1/chat/completions"


class OCRRequest(BaseModel):
    image_base64: str


class LLMRequest(BaseModel):
    mode: str
    notes: str = ""
    question: str = ""


@app.post("/api/ocr")
def extract_text(payload: OCRRequest):
    """Synchronous so FastAPI runs it in a threadpool — prevents event loop blocking."""
    import time
    try:
        raw_b64 = payload.image_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]

        image_bytes = base64.b64decode(raw_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Auto-orient based on EXIF tag if present
        image = ImageOps.exif_transpose(image)

        # Convert to grayscale — removes colored highlights that confuse OCR
        image = ImageOps.grayscale(image)
        # Boost contrast so characters stand out clearly
        image = ImageOps.autocontrast(image, cutoff=1)

        # Resize: cap large images at 1500px, upscale small images to 1500px
        # EasyOCR needs reasonably sized text to work accurately
        TARGET_WIDTH = 1500
        if image.width != TARGET_WIDTH:
            ratio = TARGET_WIDTH / image.width
            new_size = (TARGET_WIDTH, int(image.height * ratio))
            resample = Image.LANCZOS if ratio < 1 else Image.BICUBIC
            image = image.resize(new_size, resample)
            print(f"[OCR] Resized image from {image_bytes.__len__()} bytes to {new_size}")

        image_np = np.array(image)

        print(f"[OCR] Processing image of size {image.size}...")
        t0 = time.perf_counter()
        results = ocr_reader.readtext(image_np, detail=0, paragraph=True)
        elapsed = time.perf_counter() - t0
        extracted = "\n".join(results).strip()
        print(f"[OCR] Extracted {len(results)} blocks in {elapsed:.1f}s")

        return {"text": extracted}
    except Exception as e:
        print(f"[OCR Error] {e}")
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


@app.post("/api/stt")
async def transcribe_audio(file: UploadFile = File(...), lang: str = Form("en")):
    try:
        audio_bytes = await file.read()
        audio_stream = io.BytesIO(audio_bytes)
        target_lang = "hi" if "hi" in lang.lower() else "en"

        segments, _ = whisper_model.transcribe(
            audio_stream,
            language=target_lang,
            beam_size=3,
            vad_filter=True
        )
        return {"text": " ".join([seg.text for seg in segments]).strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")


@app.post("/api/llm")
async def generate_response(req: LLMRequest):
    notes = req.notes.strip()
    question = req.question.strip()

    # Determine prompt logic based on mode and presence of notes
    if req.mode == "summary":
        if not notes:
            raise HTTPException(status_code=400, detail="Cannot summarize without notes.")
        system_prompt = "You are a study assistant. Provide a concise, clear bulleted summary of these notes."
        user_prompt = f"Study Notes:\n{notes}\n\nSummary:"

    elif req.mode == "explain":
        system_prompt = (
            "You are a helpful campus tutor. Answer the student's question clearly and step-by-step. "
            "Match their language style (Hindi, Hinglish, or English)."
        )
        if notes:
            user_prompt = f"Reference Notes:\n{notes}\n\nStudent Question: {question}\n\nExplanation:"
        else:
            user_prompt = f"Student Question: {question}\n\nExplanation:"

    elif req.mode == "practice":
        if not notes:
            raise HTTPException(status_code=400, detail="Cannot generate practice questions without notes.")
        system_prompt = "Create 3-5 fill-in-the-blank practice questions from these notes, followed by an Answer Key."
        user_prompt = f"Notes:\n{notes}\n\nQuestions:"
    else:
        raise HTTPException(status_code=400, detail="Invalid mode.")

    payload = {
        "model": "qwen2.5-coder-7b-instruct",  # Required by Llamafile /v1/chat/completions
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1024
    }

    try:
        print(f"[LLM] Forwarding request to {LLAMAFILE_URL} (mode={req.mode})...")
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(LLAMAFILE_URL, json=payload)
            if resp.status_code != 200:
                print(f"[Llamafile Error] {resp.status_code} - {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=f"Llamafile error: {resp.text}")

            data = resp.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return {"answer": answer}
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Llamafile server is not running on port 8081.")
    except Exception as e:
        print(f"[LLM Exception] {e}")
        raise HTTPException(status_code=500, detail=str(e))


if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)