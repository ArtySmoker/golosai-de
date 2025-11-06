from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import uvicorn

app = FastAPI()

DEFAULT_VOICE = os.getenv("VOICE", "de_DE-thorsten-high")


@app.post("/speak")
async def speak(text: str = Form(...), voice: str = Form(None)):
    """
    Синтезирует речь из текста
    :param text: Текст для озвучивания
    :param voice: Название голоса (опционально)
    """
    # Используем переданный голос или дефолтный
    selected_voice = voice if voice else DEFAULT_VOICE

    out_file = f"/tmp/{uuid.uuid4()}.wav"
    model_path = f"/models/{selected_voice}.onnx"

    # Проверяем существование модели
    if not os.path.exists(model_path):
        print(f"WARNING: Model {model_path} not found, using default {DEFAULT_VOICE}")
        model_path = f"/models/{DEFAULT_VOICE}.onnx"

        # Если и дефолтная не найдена
        if not os.path.exists(model_path):
            return {"error": f"Model file not found: {model_path}"}

    try:
        # Запускаем piper для синтеза
        cmd = ["piper", "--model", model_path, "--output_file", out_file]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=text.encode("utf-8"), timeout=30)

        if proc.returncode != 0:
            print(f"Piper error: {stderr.decode('utf-8')}")
            return {"error": f"Piper failed: {stderr.decode('utf-8')}"}

        # Проверяем что файл создан
        if not os.path.exists(out_file):
            return {"error": "Output file was not created"}

        return FileResponse(
            out_file,
            media_type="audio/wav",
            filename="speech.wav"
        )

    except subprocess.TimeoutExpired:
        proc.kill()
        return {"error": "TTS timeout"}
    except Exception as e:
        print(f"TTS error: {e}")
        return {"error": str(e)}


@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "default_voice": DEFAULT_VOICE}


@app.get("/voices")
async def list_voices():
    """Список доступных голосов"""
    models_dir = "/models"
    if not os.path.exists(models_dir):
        return {"voices": []}

    voices = [
        f.replace(".onnx", "")
        for f in os.listdir(models_dir)
        if f.endswith(".onnx")
    ]
    return {"voices": voices, "default": DEFAULT_VOICE}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9003)