from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
CONFIG_EXAMPLE_FILE = BASE_DIR / "config" / "config.example.yaml"


# ==========================
#   统一管理运行时配置
# ==========================
@dataclass(slots=True)
class AppConfig:
    name: str
    env: str
    debug: bool
    api_prefix: str
    host: str
    port: int


@dataclass(slots=True)
class PostgresConfig:
    host: str
    port: int
    database: str
    user: str
    password: str


@dataclass(slots=True)
class MigrationConfig:
    version: str
    lock_id: int


@dataclass(slots=True)
class Settings:
    app: AppConfig
    postgres: PostgresConfig
    migration: MigrationConfig

    # 构造 ORM 使用的 SQLAlchemy 连接串。
    @property
    def sqlalchemy_database_url(self) -> str:
        return (
            f"postgresql+psycopg://{quote_plus(self.postgres.user)}:"
            f"{quote_plus(self.postgres.password)}@{self.postgres.host}:"
            f"{self.postgres.port}/{self.postgres.database}"
        )

    # 构造迁移脚本使用的 psycopg 连接串。
    @property
    def psycopg_database_url(self) -> str:
        return (
            f"postgresql://{quote_plus(self.postgres.user)}:{quote_plus(self.postgres.password)}"
            f"@{self.postgres.host}:{self.postgres.port}/{self.postgres.database}"
        )


def load_config_data() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"缺少配置文件: {CONFIG_FILE}，请先复制 {CONFIG_EXAMPLE_FILE.name} 为 config.yaml"
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


# ==========================
#   缓存配置对象
# ==========================
@lru_cache
def get_settings() -> Settings:
    config_data = load_config_data()
    app_config = config_data.get("app")
    postgres_config = config_data.get("postgres")
    migration_config = config_data.get("migration")

    if not isinstance(app_config, dict):
        raise ValueError("config.yaml 缺少 app 配置")

    if not isinstance(postgres_config, dict):
        raise ValueError("config.yaml 缺少 postgres 配置")

    if not isinstance(migration_config, dict):
        raise ValueError("config.yaml 缺少 migration 配置")

    return Settings(
        app=AppConfig(**app_config),
        postgres=PostgresConfig(**postgres_config),
        migration=MigrationConfig(**migration_config),
    )
