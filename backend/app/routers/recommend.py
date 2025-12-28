"""推荐系统路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List
from collections import Counter
from app.database import get_db
from app.models import WatchHistory
from app.services.tmdb import tmdb_service
from app.services.emby import emby_service

router = APIRouter(prefix="/recommend", tags=["Recommend"])


@router.get("/for-you")
async def get_recommendations_for_you(
    user_id: str = Query(..., description="Emby 用户 ID"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    基于用户观看历史的个性化推荐
    分析用户偏好的类型，推荐相似内容
    """
    recommendations = []
    
    try:
        # 1. 分析用户类型偏好
        result = await db.execute(
            select(WatchHistory.genres)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.genres.isnot(None),
                )
            )
        )
        
        genre_counter = Counter()
        for row in result.fetchall():
            if row[0]:
                for genre in row[0]:
                    genre_counter[genre] += 1
        
        # 获取前3个偏好类型
        top_genres = [g[0] for g in genre_counter.most_common(3)]
        
        if not top_genres:
            # 没有观看历史，返回热门内容
            trending = await tmdb_service.get_trending("all", "week", 1)
            return {
                "items": trending.get("results", [])[:limit],
                "reason": "热门推荐",
                "based_on": None,
            }
        
        # 2. 获取 TMDB 类型 ID 映射
        movie_genres = await tmdb_service.get_genres("movie")
        tv_genres = await tmdb_service.get_genres("tv")
        
        genre_id_map = {}
        for g in movie_genres.get("genres", []) + tv_genres.get("genres", []):
            genre_id_map[g["name"]] = g["id"]
        
        # 3. 根据偏好类型获取推荐
        seen_ids = set()
        
        for genre_name in top_genres:
            genre_id = genre_id_map.get(genre_name)
            if not genre_id:
                continue
            
            # 获取该类型的热门电影
            movies = await tmdb_service.discover_by_genre("movie", genre_id, 1)
            for item in movies.get("results", [])[:5]:
                if item["id"] not in seen_ids:
                    seen_ids.add(item["id"])
                    recommendations.append({
                        **item,
                        "media_type": "movie",
                        "reason": f"因为你喜欢 {genre_name}",
                    })
            
            # 获取该类型的热门剧集
            tv_shows = await tmdb_service.discover_by_genre("tv", genre_id, 1)
            for item in tv_shows.get("results", [])[:5]:
                if item["id"] not in seen_ids:
                    seen_ids.add(item["id"])
                    recommendations.append({
                        **item,
                        "media_type": "tv",
                        "reason": f"因为你喜欢 {genre_name}",
                    })
            
            if len(recommendations) >= limit:
                break
        
        return {
            "items": recommendations[:limit],
            "reason": "基于你的观看偏好",
            "based_on": top_genres,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")


@router.get("/because-you-watched/{emby_id}")
async def get_recommendations_because_watched(
    emby_id: str,
    user_id: str = Query(..., description="Emby 用户 ID"),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    基于特定观看记录的推荐
    "因为你看过 X"
    """
    try:
        # 获取观看记录
        result = await db.execute(
            select(WatchHistory)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.emby_id == emby_id,
                )
            )
        )
        watch_record = result.scalar_one_or_none()
        
        if not watch_record:
            raise HTTPException(status_code=404, detail="未找到观看记录")
        
        # 尝试获取 TMDB ID
        tmdb_id = None
        media_type = "movie" if watch_record.media_type == "Movie" else "tv"
        
        # 从 Emby 获取 TMDB ID
        try:
            item_detail = await emby_service.get_item(user_id, emby_id)
            tmdb_id = item_detail.provider_ids.get("Tmdb") if item_detail.provider_ids else None
        except Exception:
            pass
        
        if not tmdb_id:
            # 通过搜索获取 TMDB ID
            search_result = await tmdb_service.search_multi(watch_record.title)
            for item in search_result.get("results", []):
                if item.get("media_type") == media_type:
                    tmdb_id = item["id"]
                    break
        
        if not tmdb_id:
            return {
                "items": [],
                "reason": f"因为你看过《{watch_record.title}》",
                "based_on": watch_record.title,
            }
        
        # 获取推荐
        if media_type == "movie":
            recommendations = await tmdb_service.get_movie_recommendations(int(tmdb_id))
        else:
            recommendations = await tmdb_service.get_tv_recommendations(int(tmdb_id))
        
        items = []
        for item in recommendations.get("results", [])[:limit]:
            items.append({
                **item,
                "media_type": media_type,
            })
        
        return {
            "items": items,
            "reason": f"因为你看过《{watch_record.title}》",
            "based_on": watch_record.title,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")


@router.get("/similar/{media_type}/{tmdb_id}")
async def get_similar_content(
    media_type: str,
    tmdb_id: int,
    page: int = Query(1, ge=1),
):
    """
    获取相似内容
    """
    try:
        if media_type == "movie":
            result = await tmdb_service.get_movie_similar(tmdb_id, page)
        else:
            result = await tmdb_service.get_tv_similar(tmdb_id, page)
        
        items = []
        for item in result.get("results", []):
            items.append({
                **item,
                "media_type": media_type,
            })
        
        return {
            "items": items,
            "page": result.get("page", 1),
            "total_pages": result.get("total_pages", 1),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取相似内容失败: {str(e)}")


@router.get("/trending-by-genre")
async def get_trending_by_genre(
    genre_id: int = Query(..., description="类型 ID"),
    media_type: str = Query("movie", description="movie 或 tv"),
    page: int = Query(1, ge=1),
):
    """
    按类型获取热门内容
    """
    try:
        result = await tmdb_service.discover_by_genre(media_type, genre_id, page)
        
        items = []
        for item in result.get("results", []):
            items.append({
                **item,
                "media_type": media_type,
            })
        
        return {
            "items": items,
            "page": result.get("page", 1),
            "total_pages": result.get("total_pages", 1),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内容失败: {str(e)}")


@router.get("/by-network/{network_id}")
async def get_by_network(
    network_id: int,
    page: int = Query(1, ge=1),
):
    """
    按电视网络获取剧集
    """
    try:
        result = await tmdb_service.discover_by_network(network_id, page)
        
        items = []
        for item in result.get("results", []):
            items.append({
                **item,
                "media_type": "tv",
            })
        
        return {
            "items": items,
            "page": result.get("page", 1),
            "total_pages": result.get("total_pages", 1),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内容失败: {str(e)}")


@router.get("/genre-preferences")
async def get_genre_preferences(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户类型偏好分析
    """
    try:
        result = await db.execute(
            select(WatchHistory.genres, WatchHistory.media_type)
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.genres.isnot(None),
                )
            )
        )
        
        movie_genres = Counter()
        tv_genres = Counter()
        
        for row in result.fetchall():
            genres, media_type = row
            if genres:
                if media_type == "Movie":
                    for g in genres:
                        movie_genres[g] += 1
                elif media_type == "Episode":
                    for g in genres:
                        tv_genres[g] += 1
        
        return {
            "movie_preferences": dict(movie_genres.most_common(10)),
            "tv_preferences": dict(tv_genres.most_common(10)),
            "overall_preferences": dict((movie_genres + tv_genres).most_common(10)),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取偏好失败: {str(e)}")
