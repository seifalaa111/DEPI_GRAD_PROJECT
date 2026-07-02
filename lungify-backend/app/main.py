from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.services.model_registry import ModelRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry = ModelRegistry(settings)
    registry.load()
    app.state.models = registry
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real Lungify AI backend for CT screening, subtype support, and tumor localization.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.allow_all_cors_origins else list(settings.cors_origins),
    allow_credentials=not settings.allow_all_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
