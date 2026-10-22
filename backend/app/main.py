#минимальный сервер
from fastapi import FastAPI

app = FastAPI(title="Smart Credit Cabinet")


@app.get("/")
def root():
    return {"message": "Smart Credit Cabinet API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}