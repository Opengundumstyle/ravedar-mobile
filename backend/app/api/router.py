from fastapi import APIRouter

from app.api.routes.health import router as health_router

# ==========================
#   聚合所有 API 路由
# ==========================
api_router = APIRouter()
api_router.include_router(health_router)
