from fastapi import FastAPI
from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Evidence-driven multi-agent data reliability and self-healing platform",
)
app.include_router(router)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "status": "ok",
        "model_mode": settings.model_mode,
        "docs": "/docs",
    }
