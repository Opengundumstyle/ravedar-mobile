import logging
from logging.config import dictConfig


# ==========================
#   统一配置日志
# ==========================
def configure_logging(debug: bool) -> None:
    level = "DEBUG" if debug else "INFO"
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["default"],
                "level": level,
            },
        }
    )
    # 保持访问日志始终可见，便于联调排查。
    logging.getLogger("uvicorn.access").setLevel("INFO")
