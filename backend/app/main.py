
from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.core.config import settings
from app.api.applications import router as applications_router

app = FastAPI(title=settings.app_name)

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(
    applications_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
def root():
    return {"message": "Smart Credit Cabinet API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
