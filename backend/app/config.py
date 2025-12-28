from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Emby 配置
    emby_url: str = "http://localhost:8096"
    emby_api_key: str = ""
    # 允许的 Emby 用户 ID 列表（逗号分隔），为空表示允许所有
    allowed_emby_users: str = ""
    
    # TMDB 配置
    tmdb_api_key: str = ""
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p"
    
    # OMDb 配置（用于获取 IMDB、烂番茄、Metacritic 评分）
    omdb_api_keys: str = ""  # 多个 Key 用逗号分隔
    
    # 应用配置
    secret_key: str = "change-this-secret-key"
    database_url: str = "sqlite+aiosqlite:///./data/emby_tracker.db"
    
    # 管理员账户配置
    admin_username: str = "admin"
    admin_password: str = "admin123"
    
    # 同步配置
    sync_interval_minutes: int = 30  # 定时同步间隔（分钟），0 表示禁用
    sync_on_startup: bool = True  # 启动时是否自动同步
    
    # 调试配置
    debug: bool = False
    log_level: str = "INFO"
    
    @property
    def allowed_emby_user_ids(self) -> list[str]:
        """获取允许的 Emby 用户 ID 列表"""
        if not self.allowed_emby_users:
            return []
        return [uid.strip() for uid in self.allowed_emby_users.split(",") if uid.strip()]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
