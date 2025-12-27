from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """系统用户"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    is_admin = Column(Boolean, default=False)
    
    # 访客用户可访问的 Emby 用户 ID 列表 (JSON 数组)
    allowed_emby_users = Column(JSON, default=list)
    # 访客用户可访问的媒体库 ID 列表 (JSON 数组)
    allowed_libraries = Column(JSON, default=list)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WatchHistory(Base):
    """观看历史记录"""
    __tablename__ = "watch_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)  # Emby 用户 ID
    emby_id = Column(String(100), index=True)  # Emby 媒体 ID
    tmdb_id = Column(Integer, index=True, nullable=True)  # TMDB ID
    media_type = Column(String(20))  # Movie / Episode
    title = Column(String(500))
    
    # 剧集信息
    series_id = Column(String(100), nullable=True)
    series_name = Column(String(500), nullable=True)
    season_number = Column(Integer, nullable=True)
    episode_number = Column(Integer, nullable=True)
    
    # 媒体信息
    year = Column(Integer, nullable=True)
    runtime_minutes = Column(Integer, default=0)
    community_rating = Column(Float, nullable=True)
    genres = Column(JSON, default=list)  # 类型列表
    
    # 观看状态
    watched = Column(Boolean, default=False)  # 是否已看完
    watch_progress = Column(Float, default=0)  # 观看进度 (0-100)
    play_count = Column(Integer, default=0)  # 播放次数
    
    # 时间记录
    watched_at = Column(DateTime, nullable=True)  # 观看时间（用于分组显示）
    last_played_date = Column(String(50), nullable=True)  # Emby 原始播放日期
    
    # 来源标记
    source = Column(String(20), default="emby")  # emby / manual
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Watchlist(Base):
    """想看列表"""
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    emby_id = Column(String(100), index=True, nullable=True)
    tmdb_id = Column(Integer, index=True, nullable=True)
    media_type = Column(String(20))  # movie / tv
    title = Column(String(500))
    poster_path = Column(String(500), nullable=True)
    overview = Column(Text, nullable=True)
    release_date = Column(String(20), nullable=True)
    vote_average = Column(Float, nullable=True)
    
    added_at = Column(DateTime, server_default=func.now())


class MediaCache(Base):
    """TMDB 媒体信息缓存"""
    __tablename__ = "media_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, index=True)
    media_type = Column(String(20))  # movie / tv
    data = Column(JSON)  # 完整的 TMDB 数据
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class HeroSlide(Base):
    """首页轮播海报配置"""
    __tablename__ = "hero_slides"
    
    id = Column(Integer, primary_key=True, index=True)
    emby_id = Column(String(100), index=True)  # Emby 媒体 ID
    title = Column(String(500))
    overview = Column(Text, nullable=True)
    backdrop_url = Column(String(1000), nullable=True)  # 背景图 URL
    media_type = Column(String(20))  # Movie / Series
    sort_order = Column(Integer, default=0)  # 排序顺序
    is_active = Column(Boolean, default=True)  # 是否启用
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
