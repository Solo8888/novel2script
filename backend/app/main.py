from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core import settings, log


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(f"Application {settings.APP_NAME} starting...")
    log.debug(f"Debug mode: {settings.DEBUG}")
    yield
    log.info("Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    log.debug("Health check endpoint called")
    return {"status": "ok", "app_name": settings.APP_NAME}

