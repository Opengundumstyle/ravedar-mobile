from __future__ import annotations

import re
from pathlib import Path

import psycopg

from app.core.config import get_settings

# ==========================
#   迁移文件匹配规则
# ==========================
VERSION_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+_v(?P<version>\d+)\.sql$")
MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "sql" / "migrations"


# ==========================
#   解析迁移版本号
# ==========================
def parse_version(version: str) -> int:
    if not re.fullmatch(r"v\d+", version):
        raise ValueError(f"Unsupported version format: {version}")
    return int(version[1:])


# ==========================
#   加载并校验迁移文件
# ==========================
def load_migrations() -> dict[int, Path]:
    migrations: dict[int, Path] = {}
    seen_versions: set[int] = set()

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        match = VERSION_PATTERN.fullmatch(path.name)
        if match is None:
            raise ValueError(f"Unsupported migration filename: {path.name}")

        version = int(match.group("version"))
        if version in seen_versions:
            raise ValueError(f"Duplicate migration version: v{version}")

        seen_versions.add(version)
        migrations[version] = path

    return migrations


# ==========================
#   读取当前数据库版本
# ==========================
def get_current_version(conn: psycopg.Connection) -> int:
    conn.execute(
        """
        create table if not exists schema_version (
            version integer not null
        )
        """
    )
    row = conn.execute("select count(*) from schema_version").fetchone()
    if row and row[0] == 0:
        conn.execute("insert into schema_version (version) values (0)")
    row = conn.execute("select version from schema_version limit 1").fetchone()
    if row is None:
        return 0
    return int(row[0])


# ==========================
#   校验目标版本
# ==========================
def validate_target_version(target_version: str, migrations: dict[int, Path]) -> int:
    target_number = parse_version(target_version)
    if target_number and target_number not in migrations:
        raise ValueError(f"Target version {target_version} does not exist in sql/migrations")
    return target_number


# ==========================
#   执行待运行迁移
# ==========================
def apply_migrations() -> None:
    settings = get_settings()
    migrations = load_migrations()
    target_number = validate_target_version(settings.migration.version, migrations)

    with psycopg.connect(settings.psycopg_database_url) as conn:
        with conn.transaction():
            # 避免多实例同时执行迁移。
            conn.execute("select pg_advisory_xact_lock(%s)", (settings.migration.lock_id,))
            current_version = get_current_version(conn)

            if current_version > target_number:
                raise ValueError(
                    "Target version is behind the database version; rollback is not automatic"
                )

            for version in range(current_version + 1, target_number + 1):
                path = migrations.get(version)
                if path is None:
                    raise ValueError(f"Missing migration file for version v{version}")

                conn.execute(path.read_text(encoding="utf-8"))
                conn.execute("update schema_version set version = %s", (version,))
                print(f"applied {path.name}")


# ==========================
#   命令行入口
# ==========================
def main() -> None:
    apply_migrations()


if __name__ == "__main__":
    main()
