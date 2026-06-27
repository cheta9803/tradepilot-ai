from fastapi import FastAPI

from app.core.config import settings
from app.core.logger import logger

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.on_event("startup")
async def startup():
    logger.info("TradePilot AI started successfully")


@app.get("/")
async def root():
    logger.info("Root endpoint called")

    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "status": "running",
    }


@app.get("/health")
async def health():
    logger.info("Health check")

    return {
        "status": "healthy"
    }