from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from devaccountbook_backend.core.config import settings
from devaccountbook_backend.db.driver import init_driver, close_driver
from devaccountbook_backend.api.v1.items_router import router as items_router

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

app.include_router(items_router, prefix="/v1")

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
