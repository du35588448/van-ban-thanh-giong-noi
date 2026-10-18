import asyncio
import os
import re
import uuid
import json
from pathlib import Path
from datetime import datetime

import edge_tts
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)
OUTPUT_DIR = Path("static/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = OUTPUT_DIR / "history.json"

VOICES = {
    "nam": "vi-VN-NamMinhNeural",
    "nu": "vi-VN-HoaiMyNeural",
}

STYLE_SETTINGS = {
    "chat": {"rate": 0, "pitch": 0},
    "story": {"rate": -8, "pitch": -2},
    "advert": {"rate": 5, "pitch": 1},
}

def split_text(text, limit=1800):
    """Split long text at paragraph/sentence boundaries where possible."""
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    chunks, current = [], ""
    for paragraph in paragraphs:
        # Break an exceptionally long paragraph into sentence-like pieces.
        pieces = re.split(r"(?<=[.!?。！？])\s+", paragraph)
        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            while len(piece) > limit:
                cut = piece.rfind(" ", 0, limit)
                if cut < limit // 2:
                    cut = limit
                part, piece = piece[:cut].strip(), piece[cut:].strip()
                if current:
                    chunks.append(current)
                    current = ""
                if part:
                    chunks.append(part)
            candidate = f"{current}\n{piece}".strip() if current else piece
            if len(candidate) > limit and current:
                chunks.append(current)
                current = piece
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks or [text]

def read_history():
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def write_history(items):
    HISTORY_FILE.write_text(json.dumps(items[:50], ensure_ascii=False, indent=2), encoding="utf-8")

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/history")
def history():
    return jsonify(read_history())

@app.post("/convert")
def convert():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    voice_key = data.get("voice", "nam")
    style_key = data.get("style", "chat")
    rate = int(data.get("rate", 0))
    pitch = int(data.get("pitch", 0))

    if not text:
        return jsonify({"error": "Bạn hãy nhập văn bản trước nhé."}), 400
    if len(text) > 50000:
        return jsonify({"error": "Văn bản quá dài. Bạn hãy chia thành các phần nhỏ hơn 50.000 ký tự."}), 400

    voice = VOICES.get(voice_key, VOICES["nam"])
    style = STYLE_SETTINGS.get(style_key, STYLE_SETTINGS["chat"])
    rate_text = f"{max(-50, min(50, rate + style['rate'])):+d}%"
    pitch_text = f"{max(-20, min(20, pitch + style['pitch'])):+d}Hz"
    file_id = uuid.uuid4().hex[:12]
    filename = f"giong-noi-{file_id}.mp3"
    filepath = OUTPUT_DIR / filename
    chunks = split_text(text)
    temp_files = []

    async def make_audio():
        for index, chunk in enumerate(chunks, start=1):
            temp_path = OUTPUT_DIR / f"temp-{file_id}-{index}.mp3"
            communicate = edge_tts.Communicate(
                text=chunk, voice=voice, rate=rate_text, pitch=pitch_text
            )
            await communicate.save(str(temp_path))
            temp_files.append(temp_path)
        # Concatenate MP3 streams in order. MP3 frame streams are commonly
        # concatenable; the result is a single downloadable MP3.
        with filepath.open("wb") as output:
            for temp_path in temp_files:
                output.write(temp_path.read_bytes())

    try:
        asyncio.run(make_audio())
    except Exception:
        for p in temp_files:
            try: p.unlink(missing_ok=True)
            except Exception: pass
        try: filepath.unlink(missing_ok=True)
        except Exception: pass
        return jsonify({
            "error": "Chưa tạo được âm thanh. Hãy kiểm tra kết nối Internet rồi thử lại. "
                     "Dịch vụ giọng nói có thể đang tạm thời không khả dụng."
        }), 502
    finally:
        for p in temp_files:
            try: p.unlink(missing_ok=True)
            except Exception: pass

    item = {
        "id": file_id,
        "filename": filename,
        "title": text[:70].replace("\n", " "),
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "audio_url": f"/audio/{filename}",
        "download_url": f"/download/{filename}",
        "chars": len(text),
        "parts": len(chunks),
    }
    items = read_history()
    items.insert(0, item)
    write_history(items)
    return jsonify(item)

@app.get("/audio/<path:filename>")
def audio(filename):
    return send_from_directory(OUTPUT_DIR, filename, mimetype="audio/mpeg")

@app.get("/download/<path:filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
