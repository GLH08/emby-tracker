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


# ============ 发现相关 ============

@router.get("/discover/movie")
async def discover_movies(
    page: int = Query(1, ge=1),
    genre: Optional[int] = None,
    year: Optional[int] = None,
    sort_by: str = "popularity.desc",
):
    """发现电影"""
    try:
        params = {"page": page, "sort_by": sort_by}
        if genre:
            params["with_genres"] = genre
        if year:
            params["primary_release_year"] = year
        return await tmdb_service.discover_movie(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discover/tv")
async def discover_tv(
    page: int = Query(1, ge=1),
    genre: Optional[int] = None,
    year: Optional[int] = None,
    network: Optional[int] = None,
    sort_by: str = "popularity.desc",
):
    """发现剧集"""
    try:
        params = {"page": page, "sort_by": sort_by}
        if genre:
            params["with_genres"] = genre
        if year:
            params["first_air_date_year"] = year
        if network:
            params["with_networks"] = network
        return await tmdb_service.discover_tv(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/networks")
async def get_networks():
    """获取电视网络列表"""
    try:
        return await tmdb_service.get_networks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 流媒体可用性 ============

@router.get("/watch-providers/{media_type}/{media_id}")
async def get_watch_providers(media_type: str, media_id: int):
    """获取流媒体可用性"""
    try:
        return await tmdb_service.get_watch_providers(media_type, media_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 推荐相关 ============

@router.get("/movie/{movie_id}/recommendations")
async def get_movie_recommendations(movie_id: int, page: int = Query(1, ge=1)):
    """获取电影推荐"""
    try:
        return await tmdb_service.get_movie_recommendations(movie_id, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/{tv_id}/recommendations")
async def get_tv_recommendations(tv_id: int, page: int = Query(1, ge=1)):
    """获取剧集推荐"""
    try:
        return await tmdb_service.get_tv_recommendations(tv_id, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movie/{movie_id}/similar")
async def get_movie_similar(movie_id: int, page: int = Query(1, ge=1)):
    """获取相似电影"""
    try:
        return await tmdb_service.get_movie_similar(movie_id, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tv/{tv_id}/similar")
async def get_tv_similar(tv_id: int, page: int = Query(1, ge=1)):
    """获取相似剧集"""
    try:
        return await tmdb_service.get_tv_similar(tv_id, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
