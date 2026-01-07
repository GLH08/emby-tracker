import httpx
import logging
from typing import Optional
from app.config import get_settings
from app.schemas import EmbyLibrary, EmbyMediaItem, EmbyMediaList

settings = get_settings()
logger = logging.getLogger(__name__)


class EmbyService:
    def __init__(self):
        self.base_url = settings.emby_url.rstrip("/") if settings.emby_url else ""
        self.api_key = settings.emby_api_key or ""
        self.headers = {
            "X-Emby-Token": self.api_key,
            "Accept": "application/json",
        }
    
    def _check_config(self):
        """检查配置是否有效"""
        if not self.base_url or not self.api_key:
            raise ValueError("Emby URL 或 API Key 未配置")
    
    async def _request(self, method: str, endpoint: str, params: dict = None) -> dict:
        self._check_config()
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}{endpoint}"
            response = await client.request(method, url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_server_info(self) -> dict:
        """获取服务器信息"""
        return await self._request("GET", "/System/Info/Public")
    
    async def get_users(self) -> list[dict]:
        """获取用户列表"""
        return await self._request("GET", "/Users")
    
    async def get_libraries(self, user_id: str) -> list[EmbyLibrary]:
        """获取媒体库列表"""
        data = await self._request("GET", f"/Users/{user_id}/Views")
        libraries = []
        for item in data.get("Items", []):
            libraries.append(EmbyLibrary(
                id=item.get("Id"),
                name=item.get("Name"),
                collection_type=item.get("CollectionType"),
                item_count=item.get("ChildCount", 0),
            ))
        return libraries
    
    async def get_items(
        self,
        user_id: str,
        parent_id: Optional[str] = None,
        include_item_types: Optional[str] = None,
        filters: Optional[str] = None,
        sort_by: str = "SortName",
        sort_order: str = "Ascending",
        start_index: int = 0,
        limit: int = 50,
        search_term: Optional[str] = None,
        genres: Optional[str] = None,
        years: Optional[str] = None,
        is_played: Optional[bool] = None,
    ) -> EmbyMediaList:
        """获取媒体项列表"""
        params = {
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "Recursive": "true",
            "Fields": "Overview,Genres,ProviderIds,PrimaryImageAspectRatio,UserData,MediaSources,CommunityRating,ProductionYear,DatePlayed",
            "StartIndex": start_index,
            "Limit": limit,
            "ImageTypeLimit": 1,
            "EnableImageTypes": "Primary,Backdrop",
        }
        
        if parent_id:
            params["ParentId"] = parent_id
        if include_item_types:
            params["IncludeItemTypes"] = include_item_types
        if filters:
            params["Filters"] = filters
        if search_term:
            params["SearchTerm"] = search_term
        if genres:
            params["Genres"] = genres
        if years:
            params["Years"] = years
        if is_played is not None:
            params["IsPlayed"] = str(is_played).lower()
        
        data = await self._request("GET", f"/Users/{user_id}/Items", params)
        
        items = []
        for item in data.get("Items", []):
            items.append(self._parse_media_item(item))
        
        return EmbyMediaList(
            items=items,
            total_count=data.get("TotalRecordCount", 0),
        )
    
    async def get_item(self, user_id: str, item_id: str) -> EmbyMediaItem:
        """获取单个媒体项详情"""
        data = await self._request(
            "GET",
            f"/Users/{user_id}/Items/{item_id}",
            params={"Fields": "Overview,Genres,ProviderIds,People,Studios,UserData,MediaSources"}
        )
        return self._parse_media_item(data)
    
    async def get_seasons(self, user_id: str, series_id: str) -> list[EmbyMediaItem]:
        """获取剧集的季列表"""
        data = await self._request(
            "GET",
            f"/Shows/{series_id}/Seasons",
            params={"UserId": user_id, "Fields": "Overview,UserData"}
        )
        return [self._parse_media_item(item) for item in data.get("Items", [])]
    
    async def get_episodes(self, user_id: str, series_id: str, season_id: Optional[str] = None) -> list[EmbyMediaItem]:
        """获取剧集的集列表"""
        params = {
            "UserId": user_id,
            "Fields": "Overview,ProviderIds,UserData,MediaSources"
        }
        if season_id:
            params["SeasonId"] = season_id
        
        data = await self._request("GET", f"/Shows/{series_id}/Episodes", params)
        return [self._parse_media_item(item) for item in data.get("Items", [])]
    
    async def get_recently_added(self, user_id: str, limit: int = 20) -> list[EmbyMediaItem]:
        """获取最近添加的媒体"""
        data = await self._request(
            "GET",
            f"/Users/{user_id}/Items/Latest",
            params={
                "Limit": limit,
                "Fields": "Overview,Genres,ProviderIds,UserData",
                "IncludeItemTypes": "Movie,Series",
            }
        )
        return [self._parse_media_item(item) for item in data]
    
    async def get_resume_items(self, user_id: str, limit: int = 20) -> list[EmbyMediaItem]:
        """获取继续观看的媒体"""
        data = await self._request(
            "GET",
            f"/Users/{user_id}/Items/Resume",
            params={
                "Limit": limit,
                "Fields": "Overview,Genres,ProviderIds,UserData",
                "MediaTypes": "Video",
            }
        )
        return [self._parse_media_item(item) for item in data.get("Items", [])]
    
    async def mark_played(self, user_id: str, item_id: str) -> None:
        """标记为已播放"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/Users/{user_id}/PlayedItems/{item_id}"
            response = await client.post(url, headers=self.headers)
            response.raise_for_status()
    
    async def mark_unplayed(self, user_id: str, item_id: str) -> None:
        """标记为未播放"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/Users/{user_id}/PlayedItems/{item_id}"
            response = await client.delete(url, headers=self.headers)
            response.raise_for_status()
    
    async def toggle_favorite(self, user_id: str, item_id: str, is_favorite: bool) -> None:
        """切换收藏状态"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/Users/{user_id}/FavoriteItems/{item_id}"
            if is_favorite:
                response = await client.post(url, headers=self.headers)
            else:
                response = await client.delete(url, headers=self.headers)
            response.raise_for_status()
    
    def _parse_media_item(self, item: dict) -> EmbyMediaItem:
        """解析媒体项数据"""
        user_data = item.get("UserData", {})
        
        return EmbyMediaItem(
            id=item.get("Id"),
            name=item.get("Name"),
            type=item.get("Type"),
            overview=item.get("Overview"),
            year=item.get("ProductionYear"),
            premiere_date=item.get("PremiereDate"),
            community_rating=item.get("CommunityRating"),
            official_rating=item.get("OfficialRating"),
            runtime_ticks=item.get("RunTimeTicks"),
            genres=item.get("Genres", []),
            primary_image_tag=item.get("ImageTags", {}).get("Primary"),
            backdrop_image_tag=(item.get("BackdropImageTags") or [None])[0] if item.get("BackdropImageTags") else None,
            provider_ids=item.get("ProviderIds", {}),
            played=user_data.get("Played", False),
            play_count=user_data.get("PlayCount", 0),
            playback_position_ticks=user_data.get("PlaybackPositionTicks", 0),
            is_favorite=user_data.get("IsFavorite", False),
            last_played_date=user_data.get("LastPlayedDate"),
            series_id=item.get("SeriesId"),
            series_name=item.get("SeriesName"),
            season_id=item.get("SeasonId"),
            season_name=item.get("SeasonName"),
            index_number=item.get("IndexNumber"),
            parent_index_number=item.get("ParentIndexNumber"),
        )
    
    def get_image_url(self, item_id: str, image_type: str = "Primary", max_width: int = 400) -> str:
        """获取图片 URL"""
        return f"{self.base_url}/Items/{item_id}/Images/{image_type}?maxWidth={max_width}&api_key={self.api_key}"

    async def get_playback_history(self, user_id: str, limit: int = 500, start_index: int = 0) -> list[dict]:
        """
        从活动日志获取播放历史
        这个 API 可以获取到 302 直链播放的记录，即使项目没有被标记为 played
        """
        try:
            # 使用 Items API 获取有 LastPlayedDate 的项目（不管 IsPlayed 状态）
            params = {
                "SortBy": "DatePlayed",
                "SortOrder": "Descending",
                "Recursive": "true",
                "Fields": "Overview,Genres,ProviderIds,UserData,MediaSources,CommunityRating,ProductionYear,DatePlayed",
                "StartIndex": start_index,
                "Limit": limit,
                "IncludeItemTypes": "Movie,Episode",
                "HasQueryLimit": "false",
            }
            # 使用 Filters=IsPlayed 获取有播放记录的（包括正在播放和已播放）
            # 但这可能仍然遗漏 302 播放的

            data = await self._request("GET", f"/Users/{user_id}/Items", params)
            return data.get("Items", [])
        except Exception as e:
            logger.warning(f"获取播放历史失败: {e}")
            return []

    async def get_activity_log(self, user_id: str = None, limit: int = 500, start_index: int = 0) -> list[dict]:
        """
        获取活动日志（包含所有播放活动，即使是 302 直链播放）
        """
        try:
            params = {
                "StartIndex": start_index,
                "Limit": limit,
            }
            if user_id:
                params["UserId"] = user_id

            data = await self._request("GET", "/System/ActivityLog/Entries", params)
            return data.get("Items", [])
        except Exception as e:
            logger.warning(f"获取活动日志失败: {e}")
            return []


def get_emby_service() -> EmbyService:
    """获取 EmbyService 实例（延迟初始化）"""
    return EmbyService()


# 为了兼容现有代码，保留全局实例（但建议使用 get_emby_service）
emby_service = EmbyService()
