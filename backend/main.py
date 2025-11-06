import os, yaml
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import requests, tempfile, base64, time
from fastapi.responses import JSONResponse

def load_yaml(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return default or {}

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/config.yaml")
SCENARIOS_PATH = os.getenv("SCENARIOS_PATH", "config/scenarios.yaml")

_cfg = load_yaml(CONFIG_PATH)
_scn = load_yaml(SCENARIOS_PATH)

ASR_URL = _cfg.get("asr", {}).get("url", "http://asr:9001/transcribe")
LLM_URL = _cfg.get("llm", {}).get("url", "http://llm:9002/ask")
TTS_URL = _cfg.get("tts", {}).get("url", "http://tts:9003/speak")
DEFAULT_VOICE = _cfg.get("tts", {}).get("default_voice", "de_DE-thorsten-high")
DEFAULT_SCENARIO = _cfg.get("app", {}).get("default_scenario", "restaurant")
MAX_HISTORY = int(_cfg.get("llm", {}).get("max_history", 8))

app = FastAPI()
sessions = {}  # session_id → {"history": [{"role":"user"/"assistant","content":...}], "scenario_id": str}

def safe_post(url, **kwargs):
    for i in range(5):
        try:
            resp = requests.post(url, timeout=_cfg.get("app", {}).get("response_timeout", 30), **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            if i == 4: raise
            time.sleep(3)

@app.post("/start_session")
def start_session(session_id: str = None, scenario_id: str = None):
    sid = session_id or str(int(time.time()*1000))
    scn = scenario_id or DEFAULT_SCENARIO
    sessions[sid] = {"history": [], "scenario_id": scn}
    return {"session_id": sid, "scenario_id": scn, "scenario_title": _scn["scenarios"][scn]["title"]}

@app.get("/scenarios")
def list_scenarios():
    return [{"id": k, "title": v["title"]} for k, v in _scn.get("scenarios", {}).items()]

@app.post("/dialogue_file")
async def dialogue_file(
    audio: UploadFile = File(...),
    voice: str = Form(DEFAULT_VOICE),
    session_id: str = Form(None),
    scenario_id: str = Form(None),
):
    sid = session_id or str(int(time.time()*1000))
    if sid not in sessions:
        sessions[sid] = {"history": [], "scenario_id": scenario_id or DEFAULT_SCENARIO}

    # 1. ASR
    asr_resp = safe_post(ASR_URL, files={"file": audio.file})
    text_in = asr_resp.json().get("text", "")

    # 2. LLM
    scn_id = sessions[sid]["scenario_id"]
    system_prompt = _scn["scenarios"][scn_id]["system_prompt"]
    payload = {
        "system": system_prompt,
        "history": sessions[sid]["history"][-MAX_HISTORY:],
        "prompt": text_in
    }
    llm_resp = safe_post(LLM_URL, json=payload)
    text_out = llm_resp.json().get("answer", "")

    # Update history
    sessions[sid]["history"].append({"role": "user", "content": text_in})
    sessions[sid]["history"].append({"role": "assistant", "content": text_out})

    # 3. TTS
    tts_resp = safe_post(TTS_URL, data={"text": text_out, "voice": voice})
    audio_b64 = base64.b64encode(tts_resp.content).decode("utf-8")

    # 4. Возвращаем JSON
    return JSONResponse({
        "session_id": sid,
        "recognized": text_in,
        "answer": text_out,
        "voice": voice,
        "audio_b64": audio_b64
    })

@app.post("/end_session")
def end_session(session_id: str = Form(...)):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    history = sessions[session_id]["history"]
    transcript = []
    for turn in history:
        role = "Вы" if turn["role"] == "user" else "AI"
        transcript.append(f"{role}: {turn['content']}")

    # Можно вернуть как JSON или как текстовый файл
    return {"session_id": session_id, "transcript": "\n".join(transcript)}