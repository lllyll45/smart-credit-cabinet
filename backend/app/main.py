from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.applications import router as applications_router
from app.api.products import router as products_router
from app.api.calculator import router as calculator_router
from app.api.business_profile import router as business_profile_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    applications_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    products_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    calculator_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    business_profile_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
def root():
    return {"message": "Smart Credit Cabinet API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}