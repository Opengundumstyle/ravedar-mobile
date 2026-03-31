from pathlib import Path
import sys

import uvicorn
from fastapi import FastAPI

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

# ==========================
#   应用启动初始化
# ==========================
settings = get_settings()
configure_logging(settings.app.debug)

app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    docs_url=f"{settings.app.api_prefix}/docs",
    redoc_url=f"{settings.app.api_prefix}/redoc",
    openapi_url=f"{settings.app.api_prefix}/openapi.json",
)

# ==========================
#   注册全局路由
# ==========================
app.include_router(api_router, prefix=settings.app.api_prefix)


# ==========================
#   本地启动入口
# ==========================
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
    )
