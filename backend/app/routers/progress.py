"""剧集进度追踪路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct, literal_column
from typing import Optional, List
from collections import defaultdict
from app.database import get_db
from app.models import WatchHistory
from app.services.emby import emby_service
from app.services.tmdb import tmdb_service

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/shows")
async def get_shows_progress(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有正在追的剧集进度
    按剧名去重，合并不同 series_id 的记录（解决重建媒体库后的重复问题）
    使用 (season_number, episode_number) 去重，避免多次删除重新添加后进度超过 100%
    """
    # 从观看历史中获取所有看过的剧集，按剧名分组
    # 使用 (season_number, episode_number) 去重而不是 emby_id，避免重复计算
    result = await db.execute(
        select(
            WatchHistory.series_id,
            WatchHistory.series_name,
            func.max(WatchHistory.watched_at).label("last_watched"),
        )
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.series_id.isnot(None),
                WatchHistory.series_name.isnot(None),
            )
        )
        .group_by(WatchHistory.series_id, WatchHistory.series_name)
        .order_by(func.max(WatchHistory.watched_at).desc())
    )

    # 按剧名合并记录
    shows_by_name = {}
    for row in result.fetchall():
        series_id, series_name, last_watched = row

        # 标准化剧名（去除空格、转小写）用于比较
        normalized_name = series_name.strip().lower() if series_name else ""

        if normalized_name not in shows_by_name:
            shows_by_name[normalized_name] = {
                "series_ids": [series_id],
                "series_name": series_name,
                "last_watched": last_watched,
                "primary_series_id": series_id,  # 使用最新的 series_id 作为主 ID
            }
        else:
            # 合并记录
            shows_by_name[normalized_name]["series_ids"].append(series_id)
            # 使用最新的观看时间
            if last_watched and (not shows_by_name[normalized_name]["last_watched"] or
                                 last_watched > shows_by_name[normalized_name]["last_watched"]):
                shows_by_name[normalized_name]["last_watched"] = last_watched
                shows_by_name[normalized_name]["primary_series_id"] = series_id
    
    shows_progress = []

    for normalized_name, show_data in shows_by_name.items():
        series_id = show_data["primary_series_id"]
        series_name = show_data["series_name"]
        last_watched = show_data["last_watched"]

        try:
            # 从 Emby 获取剧集详情
            series_detail = await emby_service.get_item(user_id, series_id)

            # 获取总集数
            total_episodes = 0
            seasons_info = []

            # 获取季列表（返回 EmbyMediaItem 对象列表）
            seasons = await emby_service.get_seasons(user_id, series_id)

            # 收集当前 Emby 中存在的所有剧集的 (season_number, episode_number)
            current_emby_episodes = set()

            for season in seasons:
                # season 是 EmbyMediaItem 对象，使用属性访问
                if season.name and season.name.startswith("Specials"):
                    continue  # 跳过特别篇

                season_id = season.id
                season_number = season.index_number or 0

                # 获取该季的集数
                episodes = await emby_service.get_episodes(user_id, series_id, season_id)
                season_total = len(episodes)
                total_episodes += season_total

                # 记录当前存在的剧集
                for ep in episodes:
                    current_emby_episodes.add((season_number, ep.index_number or 0))

                # 统计该季已看集数（按 season_number + episode_number 去重，包括所有 series_id 的记录）
                # 使用子查询来统计不同的 (season_number, episode_number) 组合数量
                season_watched = await db.execute(
                    select(func.count(distinct(
                        func.printf('%d-%d', WatchHistory.season_number, WatchHistory.episode_number)
                    )))
                    .where(
                        and_(
                            WatchHistory.user_id == user_id,
                            WatchHistory.series_id.in_(show_data["series_ids"]),
                            WatchHistory.season_number == season_number,
                            WatchHistory.episode_number.isnot(None),
                        )
                    )
                )
                season_watched_count = season_watched.scalar() or 0
                # 确保不超过实际集数
                season_watched_count = min(season_watched_count, season_total)

                # 获取每集的观看状态
                episodes_info = []
                for ep in sorted(episodes, key=lambda x: x.index_number or 0):
                    ep_watched_result = await db.execute(
                        select(WatchHistory)
                        .where(
                            and_(
                                WatchHistory.user_id == user_id,
                                WatchHistory.emby_id == ep.id,
                            )
                        )
                    )
                    ep_record = ep_watched_result.scalar_one_or_none()

                    # 如果没有找到记录，尝试用 season_number + episode_number 查找（兼容旧记录）
                    if not ep_record:
                        ep_watched_result = await db.execute(
                            select(WatchHistory)
                            .where(
                                and_(
                                    WatchHistory.user_id == user_id,
                                    WatchHistory.series_id.in_(show_data["series_ids"]),
                                    WatchHistory.season_number == season_number,
                                    WatchHistory.episode_number == ep.index_number,
                                )
                            )
                            .order_by(WatchHistory.watched_at.desc())
                            .limit(1)
                        )
                        ep_record = ep_watched_result.scalar_one_or_none()

                    # 判断是否已看完：watched 为 True 或 进度 >= 90%
                    progress_percent = ep_record.watch_progress if ep_record else 0
                    is_watched = False
                    if ep_record:
                        is_watched = ep_record.watched or progress_percent >= 90

                    episodes_info.append({
                        "episode_id": ep.id,
                        "episode_number": ep.index_number or 0,
                        "episode_name": ep.name,
                        "is_watched": is_watched,
                        "progress_percent": progress_percent if not is_watched else 100,
                    })

                seasons_info.append({
                    "season_id": season_id,
                    "season_number": season_number,
                    "season_name": season.name,
                    "total_episodes": season_total,
                    "watched_episodes": season_watched_count,
                    "progress": round(season_watched_count / season_total * 100, 1) if season_total > 0 else 0,
                    "poster_path": season.primary_image_tag,
                    "episodes": episodes_info,
                })

            # 计算总的已看集数（按 season_number + episode_number 去重）
            # 使用 printf 创建唯一标识符来进行去重计数
            total_watched_result = await db.execute(
                select(func.count(distinct(
                    func.printf('%d-%d', WatchHistory.season_number, WatchHistory.episode_number)
                )))
                .where(
                    and_(
                        WatchHistory.user_id == user_id,
                        WatchHistory.series_id.in_(show_data["series_ids"]),
                        WatchHistory.season_number.isnot(None),
                        WatchHistory.episode_number.isnot(None),
                    )
                )
            )
            watched_count = total_watched_result.scalar() or 0
            # 确保不超过实际总集数
            watched_count = min(watched_count, total_episodes)

            # 计算总进度
            progress = round(watched_count / total_episodes * 100, 1) if total_episodes > 0 else 0

            # 获取下一集信息
            next_episode = await get_next_episode(user_id, series_id, db)
            
            shows_progress.append({
                "series_id": series_id,
                "series_name": series_name or series_detail.name,
                "poster_path": series_detail.primary_image_tag,
                "backdrop_path": series_detail.backdrop_image_tag,
                "total_episodes": total_episodes,
                "watched_episodes": watched_count,
                "progress": progress,
                "last_watched": last_watched.isoformat() if last_watched else None,
                "seasons": seasons_info,
                "next_episode": next_episode,
                "tmdb_id": series_detail.provider_ids.get("Tmdb") if series_detail.provider_ids else None,
                "status": series_detail.status if hasattr(series_detail, 'status') else None,
            })
            
        except Exception as e:
            print(f"获取剧集 {series_id} 进度失败: {e}")
            continue
    
    return {"shows": shows_progress}


@router.get("/show/{series_id}")
async def get_show_progress(
    series_id: str,
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个剧集的详细进度
    """
    try:
        # 从 Emby 获取剧集详情
        series_detail = await emby_service.get_item(user_id, series_id)
        
        # 获取所有季（返回 EmbyMediaItem 对象列表）
        seasons = await emby_service.get_seasons(user_id, series_id)
        
        seasons_progress = []
        total_episodes = 0
        total_watched = 0
        
        for season in seasons:
            # season 是 EmbyMediaItem 对象
            season_id = season.id
            season_number = season.index_number or 0
            season_name = season.name or f"第 {season_number} 季"
            
            # 获取该季所有集（返回 EmbyMediaItem 对象列表）
            episodes = await emby_service.get_episodes(user_id, series_id, season_id)
            
            episodes_progress = []
            season_watched = 0
            
            for ep in episodes:
                # ep 是 EmbyMediaItem 对象
                ep_id = ep.id
                ep_number = ep.index_number or 0
                
                # 检查是否已看
                watched_result = await db.execute(
                    select(WatchHistory)
                    .where(
                        and_(
                            WatchHistory.user_id == user_id,
                            WatchHistory.emby_id == ep_id,
                        )
                    )
                )
                watch_record = watched_result.scalar_one_or_none()
                
                is_watched = watch_record is not None
                if is_watched:
                    season_watched += 1
                
                episodes_progress.append({
                    "episode_id": ep_id,
                    "episode_number": ep_number,
                    "episode_name": ep.name,
                    "runtime": ep.runtime_ticks // 600000000 if ep.runtime_ticks else 0,  # 转换为分钟
                    "is_watched": is_watched,
                    "watched_at": watch_record.watched_at.isoformat() if watch_record and watch_record.watched_at else None,
                    "progress_percent": watch_record.watch_progress if watch_record else 0,
                    "overview": ep.overview,
                    "still_path": ep.primary_image_tag,
                })
            
            season_total = len(episodes)
            total_episodes += season_total
            total_watched += season_watched
            
            seasons_progress.append({
                "season_id": season_id,
                "season_number": season_number,
                "season_name": season_name,
                "total_episodes": season_total,
                "watched_episodes": season_watched,
                "progress": round(season_watched / season_total * 100, 1) if season_total > 0 else 0,
                "episodes": episodes_progress,
                "poster_path": season.primary_image_tag,
            })
        
        # 获取下一集
        next_episode = await get_next_episode(user_id, series_id, db)
        
        return {
            "series_id": series_id,
            "series_name": series_detail.name,
            "poster_path": series_detail.primary_image_tag,
            "backdrop_path": series_detail.backdrop_image_tag,
            "total_episodes": total_episodes,
            "watched_episodes": total_watched,
            "progress": round(total_watched / total_episodes * 100, 1) if total_episodes > 0 else 0,
            "seasons": seasons_progress,
            "next_episode": next_episode,
            "tmdb_id": series_detail.provider_ids.get("Tmdb") if series_detail.provider_ids else None,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剧集进度失败: {str(e)}")


async def get_next_episode(user_id: str, series_id: str, db: AsyncSession):
    """获取下一集未看的剧集"""
    try:
        # 获取所有季（返回 EmbyMediaItem 对象列表）
        seasons = await emby_service.get_seasons(user_id, series_id)
        
        for season in sorted(seasons, key=lambda x: x.index_number or 0):
            # season 是 EmbyMediaItem 对象
            if season.name and season.name.startswith("Specials"):
                continue
                
            season_id = season.id
            season_number = season.index_number or 0
            
            # 获取该季所有集（返回 EmbyMediaItem 对象列表）
            episodes = await emby_service.get_episodes(user_id, series_id, season_id)
            
            for ep in sorted(episodes, key=lambda x: x.index_number or 0):
                # ep 是 EmbyMediaItem 对象
                ep_id = ep.id
                
                # 检查是否已看
                watched_result = await db.execute(
                    select(WatchHistory)
                    .where(
                        and_(
                            WatchHistory.user_id == user_id,
                            WatchHistory.emby_id == ep_id,
                        )
                    )
                )
                
                if not watched_result.scalar_one_or_none():
                    # 找到第一个未看的集
                    return {
                        "episode_id": ep_id,
                        "season_number": season_number,
                        "episode_number": ep.index_number or 0,
                        "episode_name": ep.name,
                        "overview": ep.overview,
                        "runtime": ep.runtime_ticks // 600000000 if ep.runtime_ticks else 0,
                        "still_path": ep.primary_image_tag,
                    }
        
        return None  # 全部看完
        
    except Exception:
        return None


@router.get("/stats")
async def get_progress_stats(
    user_id: str = Query(..., description="Emby 用户 ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取进度统计概览
    """
    # 统计正在追的剧集数（按剧名去重）
    result = await db.execute(
        select(WatchHistory.series_name)
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.series_name.isnot(None),
            )
        )
        .distinct()
    )
    unique_shows = set()
    for row in result.fetchall():
        if row[0]:
            unique_shows.add(row[0].strip().lower())
    watching_count = len(unique_shows)
    
    # 统计总观看集数
    episodes_result = await db.execute(
        select(func.count(distinct(WatchHistory.emby_id)))
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
            )
        )
    )
    episodes_watched = episodes_result.scalar() or 0
    
    # 统计本周观看集数
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    
    week_result = await db.execute(
        select(func.count(distinct(WatchHistory.emby_id)))
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.watched_at >= week_ago,
            )
        )
    )
    episodes_this_week = week_result.scalar() or 0
    
    return {
        "watching_shows": watching_count,
        "episodes_watched": episodes_watched,
        "episodes_this_week": episodes_this_week,
    }


@router.delete("/cleanup-duplicates")
async def cleanup_duplicate_series(
    user_id: str = Query(..., description="Emby 用户 ID"),
    dry_run: bool = Query(True, description="仅预览，不实际删除"),
    db: AsyncSession = Depends(get_db),
):
    """
    清理重复的剧集记录（针对重建媒体库后产生的重复）
    
    逻辑：
    1. 按剧名分组找出有多个 series_id 的剧集
    2. 保留最新的 series_id 对应的记录
    3. 删除旧的 series_id 对应的记录（这些在 Emby 中已不存在）
    """
    # 找出所有剧集记录，按剧名分组
    result = await db.execute(
        select(
            WatchHistory.series_id,
            WatchHistory.series_name,
            func.max(WatchHistory.watched_at).label("last_watched"),
            func.count(WatchHistory.id).label("record_count"),
        )
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.media_type == "Episode",
                WatchHistory.series_name.isnot(None),
            )
        )
        .group_by(WatchHistory.series_id, WatchHistory.series_name)
    )
    
    # 按剧名分组
    shows_by_name = {}
    for row in result.fetchall():
        series_id, series_name, last_watched, record_count = row
        normalized_name = series_name.strip().lower() if series_name else ""
        
        if normalized_name not in shows_by_name:
            shows_by_name[normalized_name] = []
        
        shows_by_name[normalized_name].append({
            "series_id": series_id,
            "series_name": series_name,
            "last_watched": last_watched,
            "record_count": record_count,
        })
    
    # 找出有重复的剧集
    duplicates = []
    to_delete_ids = []
    
    for name, entries in shows_by_name.items():
        if len(entries) > 1:
            # 按最后观看时间排序，保留最新的
            sorted_entries = sorted(entries, key=lambda x: x["last_watched"] or "", reverse=True)
            keep = sorted_entries[0]
            remove = sorted_entries[1:]
            
            duplicates.append({
                "series_name": keep["series_name"],
                "keep_series_id": keep["series_id"],
                "keep_record_count": keep["record_count"],
                "remove": [
                    {
                        "series_id": r["series_id"],
                        "record_count": r["record_count"],
                    }
                    for r in remove
                ],
            })
            
            # 收集要删除的 series_id
            for r in remove:
                to_delete_ids.append(r["series_id"])
    
    if not duplicates:
        return {
            "message": "没有发现重复的剧集记录",
            "duplicates": [],
            "deleted_count": 0,
        }
    
    deleted_count = 0
    
    if not dry_run and to_delete_ids:
        # 实际删除
        delete_result = await db.execute(
            select(func.count(WatchHistory.id))
            .where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.series_id.in_(to_delete_ids),
                )
            )
        )
        deleted_count = delete_result.scalar() or 0
        
        await db.execute(
            WatchHistory.__table__.delete().where(
                and_(
                    WatchHistory.user_id == user_id,
                    WatchHistory.series_id.in_(to_delete_ids),
                )
            )
        )
        await db.commit()
    
    return {
        "message": "预览模式，未实际删除" if dry_run else f"已删除 {deleted_count} 条重复记录",
        "dry_run": dry_run,
        "duplicates": duplicates,
        "deleted_count": deleted_count if not dry_run else sum(
            sum(r["record_count"] for r in d["remove"]) for d in duplicates
        ),
    }


@router.post("/validate-emby-ids")
async def validate_emby_ids(
    user_id: str = Query(..., description="Emby 用户 ID"),
    fix_stale: bool = Query(False, description="修复失效的记录（更新 emby_id 为 null）"),
    db: AsyncSession = Depends(get_db),
):
    """
    验证并修复数据库中的 emby_id 是否仍在 Emby 中存在

    针对媒体库删除重新添加后，旧 emby_id 失效的问题：
    1. 检查所有记录的 emby_id 是否仍在 Emby 中存在
    2. 对于失效的 emby_id，如果存在同一剧集的新记录，标记旧记录
    3. 可选择删除或保留失效记录（保留用于历史统计）
    """
    import httpx

    # 获取所有有 emby_id 的记录
    result = await db.execute(
        select(
            WatchHistory.id,
            WatchHistory.emby_id,
            WatchHistory.media_type,
            WatchHistory.title,
            WatchHistory.series_name,
            WatchHistory.season_number,
            WatchHistory.episode_number,
        )
        .where(
            and_(
                WatchHistory.user_id == user_id,
                WatchHistory.emby_id.isnot(None),
            )
        )
    )

    records = result.fetchall()
    stale_records = []
    valid_count = 0
    checked_count = 0

    # 批量检查（避免太多 API 调用）
    for record in records:
        record_id, emby_id, media_type, title, series_name, season_num, episode_num = record
        checked_count += 1

        try:
            # 尝试获取该项目
            await emby_service.get_item(user_id, emby_id)
            valid_count += 1
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                stale_records.append({
                    "id": record_id,
                    "emby_id": emby_id,
                    "media_type": media_type,
                    "title": title,
                    "series_name": series_name,
                    "season_number": season_num,
                    "episode_number": episode_num,
                })
        except Exception as e:
            # 其他错误跳过
            print(f"检查 {emby_id} 时出错: {e}")
            continue

        # 每检查 50 个暂停一下，避免 API 过载
        if checked_count % 50 == 0:
            import asyncio
            await asyncio.sleep(0.5)

    fixed_count = 0

    if fix_stale and stale_records:
        # 将失效的 emby_id 和 series_id 设为 null（但保留记录用于历史统计）
        stale_ids = [r["id"] for r in stale_records]

        for record_id in stale_ids:
            update_result = await db.execute(
                select(WatchHistory).where(WatchHistory.id == record_id)
            )
            record = update_result.scalar_one_or_none()
            if record:
                record.emby_id = None
                record.series_id = None
                fixed_count += 1

        await db.commit()

    return {
        "checked_count": checked_count,
        "valid_count": valid_count,
        "stale_count": len(stale_records),
        "fixed_count": fixed_count if fix_stale else 0,
        "stale_records": stale_records[:50],  # 只返回前 50 条
        "message": f"检查完成: {valid_count} 条有效, {len(stale_records)} 条失效" +
                   (f", 已修复 {fixed_count} 条" if fix_stale else ""),
    }
