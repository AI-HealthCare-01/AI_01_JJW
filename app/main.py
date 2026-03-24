from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager

from app.apis.v1 import v1_routers
from app.db.databases import close_redis
from app.core.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    yield
    # 종료 시 실행
    await close_redis()


app = FastAPI(
    title="AI Healthcare API",
    description="AI 기반 건강 예측 서비스",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Static Files 서빙 (Figma UI)
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# API 라우터 등록
app.include_router(v1_routers, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "AI Healthcare Service", "docs": "/api/docs"}