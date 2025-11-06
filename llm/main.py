from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    # здесь вызов модели
    return {"answer": f"Echo: {prompt}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9002)