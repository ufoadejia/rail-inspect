"""应用配置。从环境变量读取，.env 文件优先。

LoongArch 版本：使用 pydantic v1 BaseSettings（纯 Python，无需 Rust 编译）。
"""
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    # 多模态大模型
    dashscope_api_key: str = ""
    qwen_vl_model: str = "qwen-vl-max"
    qwen_text_model: str = "qwen-plus"
    use_mock: bool = True  # 无 API key 时用 mock，不阻塞开发

    # SQLite（LoongArch 环境默认用 SQLite，不依赖 PostgreSQL）
    sqlite_path: str = "backend/data/rail.db"

    # 以下保留但默认不启用（兼容旧配置）
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "rail"
    postgres_password: str = "rail123"
    postgres_db: str = "rail_defect"
    use_sqlite_fallback: bool = True

    # Milvus（默认不用）
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # MinIO（默认不用）
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "rail-defect"

    # 应用
    secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173"

    @property
    def sqlite_dsn(self) -> str:
        return f"sqlite:///{self.sqlite_path}"

    @property
    def cors_origin_list(self) -> list:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
