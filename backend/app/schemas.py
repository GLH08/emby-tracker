from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


# ============ Emby 相关 ============

class EmbyLibrary(BaseModel):
    id: str
    name: str
    collection_type: Optional[str] = None
    item_count: int = 0


class EmbyMediaItem(BaseModel):
    id: str
    name: str
    type: str  # Movie / Series / Episode
    overview: Optional[str] = None
    year: Optional[int] = None
    premiere_date: Optional[str] = None
    community_rating: Optional[float] = None
    official_rating: Optional[str] = None
    runtime_ticks: Optional[int] = None
    genres: list[str] = []
    
    # 图片
    primary_image_tag: Optional[str] = None
    backdrop_image_tag: Optional[str] = None
    
    # Provider IDs
    provider_ids: dict[str, str] = {}
    
    # 用户数据
    played: bool = False
    play_count: int = 0
    playback_position_ticks: int = 0
    is_favorite: bool = False
    last_played_date: Optional[str] = None  # 最后播放日期
    
    # 剧集特有
    series_id: Optional[str] = None
    series_name: Optional[str] = None
    season_id: Optional[str] = None
    season_name: Optional[str] = None
    index_number: Optional[int] = None
    parent_index_number: Optional[int] = None


class EmbyMediaList(BaseModel):
    items: list[EmbyMediaItem]
    total_count: int


# ============ TMDB 相关 ============

class TMDBMovie(BaseModel):
    id: int
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: float = 0
    vote_count: int = 0
    popularity: float = 0
    genres: list[dict] = []
    runtime: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    budget: int = 0
    revenue: int = 0
    production_companies: list[dict] = []
    credits: Optional[dict] = None
    videos: Optional[dict] = None
    similar: Optional[dict] = None
    recommendations: Optional[dict] = None


class TMDBTVShow(BaseModel):
    id: int
    name: str
    original_name: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    first_air_date: Optional[str] = None
    last_air_date: Optional[str] = None
    vote_average: float = 0
    vote_count: int = 0
    popularity: float = 0
    genres: list[dict] = []
    episode_run_time: list[int] = []
    status: Optional[str] = None
    tagline: Optional[str] = None
    number_of_seasons: int = 0
    number_of_episodes: int = 0
    networks: list[dict] = []
    created_by: list[dict] = []
    credits: Optional[dict] = None
    videos: Optional[dict] = None
    similar: Optional[dict] = None
    recommendations: Optional[dict] = None


# ============ 观看记录相关 ============

class WatchHistoryCreate(BaseModel):
    emby_id: str
    tmdb_id: Optional[int] = None
    media_type: str
    title: str
    watched: bool = False
    watch_progress: float = 0
    play_count: int = 0


class WatchHistoryResponse(BaseModel):
    id: int
    emby_id: str
    tmdb_id: Optional[int]
    media_type: str
    title: str
    watched: bool
    watch_progress: float
    play_count: int
    last_watched_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    emby_id: Optional[str] = None
    tmdb_id: Optional[int] = None
    media_type: str
    title: str
    poster_path: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None


class WatchlistResponse(BaseModel):
    id: int
    emby_id: Optional[str]
    tmdb_id: Optional[int]
    media_type: str
    title: str
    poster_path: Optional[str]
    overview: Optional[str]
    release_date: Optional[str]
    vote_average: Optional[float]
    added_at: datetime

    class Config:
        from_attributes = True


# ============ 统计相关 ============

class WatchStats(BaseModel):
    total_movies: int = 0
    total_shows: int = 0
    total_episodes: int = 0
    watched_movies: int = 0
    watched_episodes: int = 0
    total_watch_time_minutes: int = 0
    watchlist_count: int = 0
    genres_distribution: dict[str, int] = {}
    recent_watched: list[dict] = []
