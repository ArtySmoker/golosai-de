from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import uvicorn
import tempfile

app = FastAPI()

# Загружаем модель один раз при старте
# Можно выбрать "large-v3" или "medium" для скорости
model = WhisperModel("base", device="cpu", compute_type="int8")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        segments, info = model.transcribe(tmp_path, language="de")
        text = " ".join([seg.text for seg in segments])
        return {"language": info.language, "text": text}
    except Exception as e:
        print("ASR error:", e)
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)