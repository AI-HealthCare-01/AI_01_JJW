import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles

from app.apis.v1 import v1_routers
from app.core.config import config
from app.db.databases import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(
    title="만성질환 예측 서비스",
    description="AI 기반 만성질환 예측 및 개선 서비스",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(v1_routers, prefix="/api/v1")

# 빌드된 SPA static 파일 서빙 (assets 디렉토리)
static_dir = config.STATIC_DIR
if os.path.isdir(os.path.join(static_dir, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")


@app.get("/api/info")
async def api_info():
    return {
        "service": "만성질환 예측 서비스",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """SPA fallback - 모든 비-API 경로를 index.html로 라우팅"""
    index_path = os.path.join(static_dir, "index.html")
    # 정적 파일이 존재하면 직접 서빙
    file_path = os.path.join(static_dir, full_path)
    if full_path and os.path.isfile(file_path):
        return FileResponse(file_path)
    # 그 외 모든 경로는 SPA index.html로 fallback
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return ORJSONResponse(
        content={"detail": "프론트엔드 빌드가 필요합니다. cd src && npm install && npm run build"},
        status_code=404,
    )
