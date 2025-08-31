# app/main.py (혹은 현재 파일 이름)
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles  # ✅ 추가

from devaccountbook_backend.api.v1.account_entries_router import router as items_router
from devaccountbook_backend.core.config import settings
from devaccountbook_backend.db.driver import init_driver, close_driver


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_driver(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    try:
        yield
    finally:
        close_driver()

app = FastAPI(title="DevAccountBook API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=512)

# API
app.include_router(items_router, prefix="/v1")

# STATIC 파일 배포
def resource_path(*parts: str) -> Path:
    # ✅ PyInstaller(onefile)와 개발 환경 모두에서 동일하게 동작
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).joinpath("devaccountbook_backend", *parts)
    import devaccountbook_backend as pkg
    return Path(pkg.__file__).resolve().parent.joinpath(*parts)

static_dir = resource_path("static")

# 정적 파일 서빙 (Vite base를 /static/로 맞출 예정)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
# 루트: index.html
@app.get("/", include_in_schema=False)
def serve_index():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"ok": True}

# SPA 라우팅 fallback (API/정적·문서 경로는 제외)
@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    # API/정적/헬스체크/문서 엔드포인트는 통과
    if full_path.startswith((
        "v1/", "static/", "assets/", "healthz",
        "docs", "redoc", "openapi.json"
    )):
        raise HTTPException(status_code=404)

    # 파일처럼 보이면(확장자 있음) 404
    if "." in full_path.split("/")[-1]:
        raise HTTPException(status_code=404)

    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    raise HTTPException(status_code=404)

@app.get("/healthz")
def healthz():
    return {"ok": True}
