# run_server.py
import asyncio, platform
import uvicorn
from devaccountbook_backend.main import app  # FastAPI 인스턴스

if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
