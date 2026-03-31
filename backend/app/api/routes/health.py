from fastapi import APIRouter

from app.core.config import get_settings

# ==========================
#   健康检查路由
# ==========================
router = APIRouter(prefix="/health", tags=["health"])


# ==========================
#   返回最小可用状态
# ==========================
@router.get("")
async def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app.name,
        "env": settings.app.env,
    }
