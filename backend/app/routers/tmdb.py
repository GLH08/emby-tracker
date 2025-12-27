from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.tmdb import tmdb_service

router = APIRouter(prefix="/tmdb", tags=["TMDB"])


# ============ 搜索相关 ============

@router.get("/search/movie")
async def search_movie(
    query: str,
    page: int = Query(1, ge=1),
    year: Optional[int] = None,
):
    """搜索电影"""
    try:
        return await tmdb_service.search_movie(query, page, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/tv")
async def search_tv(
    query: str,
    page: int = Query(1, ge=1),
    year: Optional[int] = None,
):
    """搜索剧集"""
    try:
        return await tmdb_service.search_tv(query, page, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/multi")
async def search_multi(query: str, page: int = Query(1, ge=1)):
    """多类型搜索"""
    try:
        return await tmdb_service.search_multi(query, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 趋势相关 ============

@router.get("/trending/{media_type}/{time_window}")
async def get_trending(
    media_type: str = "all",
    time_window: str = "week",
    page: int = Query(1, ge=1),
):
    """获取趋势内容"""
    try:
        return await tmdb_service.get_trending(media_type, time_window, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 电影相关（具体路径必须在动态路径前面）============

@router.get("/movie/popular")
async def get_popular_movies(page: int = Query(1, ge=1)):
    """获取热门电影"""
    try:
        return await tmdb_service.get_popular_movies(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movie/now-playing")
async def get_now_playing_movies(page: int = Query(1, ge=1)):
    """获取正在上映的电影"""
    try:
        return await tmdb_service.get_now_playing_movies(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movie/upcoming")
async def get_upcoming_movies(page: int = Query(1, ge=1)):
    """获取即将上映的电影"""
    try:
        return await tmdb_service.get_upcoming_movies(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movie/top-rated")
async def get_top_rated_movies(page: int = Query(1, ge=1)):
    """获取高分电影"""
    try:
        return await tmdb_service.get_top_rated_movies(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movie/{movie_id}")
async def get_movie(movie_id: int):
    """获取电影详情"""
    try:
        return await tmdb_service.get_movie(movie_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 剧集相关（具体路径必须在动态路径前面）============

@router.get("/tv/popular")
async def get_popular_tv(page: int = Query(1, ge=1)):
    """获取热门剧集"""
    try:
        return await tmdb_service.get_popular_tv(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/top-rated")
async def get_top_rated_tv(page: int = Query(1, ge=1)):
    """获取高分剧集"""
    try:
        return await tmdb_service.get_top_rated_tv(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/{tv_id}/season/{season_number}/episode/{episode_number}")
async def get_tv_episode(tv_id: int, season_number: int, episode_number: int):
    """获取集详情"""
    try:
        return await tmdb_service.get_tv_episode(tv_id, season_number, episode_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/{tv_id}/season/{season_number}")
async def get_tv_season(tv_id: int, season_number: int):
    """获取季详情"""
    try:
        return await tmdb_service.get_tv_season(tv_id, season_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/{tv_id}")
async def get_tv_show(tv_id: int):
    """获取剧集详情"""
    try:
        return await tmdb_service.get_tv_show(tv_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 人物相关 ============

@router.get("/person/{person_id}")
async def get_person(person_id: int):
    """获取人物详情"""
    try:
        return await tmdb_service.get_person(person_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 其他 ============

@router.get("/genres/{media_type}")
async def get_genres(media_type: str = "movie"):
    """获取类型列表"""
    try:
        return await tmdb_service.get_genres(media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image-url")
async def get_image_url(path: str, size: str = "w500"):
    """获取图片完整 URL"""
    return {"url": tmdb_service.get_image_url(path, size)}
