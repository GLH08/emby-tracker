import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器 - 添加 token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    // 401 错误时清除 token 并跳转登录
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  getMe: () => api.get('/auth/me'),
  changePassword: (oldPassword, newPassword) => api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
  checkInit: () => api.get('/auth/check-init'),
  initAdmin: () => api.post('/auth/init'),
  // 访客管理
  getGuests: () => api.get('/auth/guests'),
  createGuest: (data) => api.post('/auth/guests', data),
  updateGuest: (id, data) => api.put(`/auth/guests/${id}`, data),
  deleteGuest: (id) => api.delete(`/auth/guests/${id}`),
}

// Emby API
export const embyApi = {
  getServerInfo: () => api.get('/emby/server-info'),
  getUsers: () => api.get('/emby/users'),
  getLibraries: (userId) => api.get(`/emby/libraries/${userId}`),
  getItems: (userId, params) => api.get(`/emby/items/${userId}`, { params }),
  getItem: (userId, itemId) => api.get(`/emby/item/${userId}/${itemId}`),
  getSeasons: (userId, seriesId) => api.get(`/emby/seasons/${userId}/${seriesId}`),
  getEpisodes: (userId, seriesId, seasonId) => api.get(`/emby/episodes/${userId}/${seriesId}`, { params: { season_id: seasonId } }),
  getRecentlyAdded: (userId, limit = 20) => api.get(`/emby/recently-added/${userId}`, { params: { limit } }),
  getResumeItems: (userId, limit = 20) => api.get(`/emby/resume/${userId}`, { params: { limit } }),
  markPlayed: (userId, itemId) => api.post(`/emby/mark-played/${userId}/${itemId}`),
  markUnplayed: (userId, itemId) => api.post(`/emby/mark-unplayed/${userId}/${itemId}`),
  toggleFavorite: (userId, itemId, isFavorite) => api.post(`/emby/toggle-favorite/${userId}/${itemId}`, null, { params: { is_favorite: isFavorite } }),
}

// TMDB API
export const tmdbApi = {
  getMovie: (movieId) => api.get(`/tmdb/movie/${movieId}`),
  getTvShow: (tvId) => api.get(`/tmdb/tv/${tvId}`),
  getTvSeason: (tvId, seasonNumber) => api.get(`/tmdb/tv/${tvId}/season/${seasonNumber}`),
  searchMovie: (query, page = 1) => api.get('/tmdb/search/movie', { params: { query, page } }),
  searchTv: (query, page = 1) => api.get('/tmdb/search/tv', { params: { query, page } }),
  searchMulti: (query, page = 1) => api.get('/tmdb/search/multi', { params: { query, page } }),
  getTrending: (mediaType = 'all', timeWindow = 'week', page = 1) => api.get(`/tmdb/trending/${mediaType}/${timeWindow}`, { params: { page } }),
  getPopularMovies: (page = 1) => api.get('/tmdb/movie/popular', { params: { page } }),
  getPopularTv: (page = 1) => api.get('/tmdb/tv/popular', { params: { page } }),
  getNowPlayingMovies: (page = 1) => api.get('/tmdb/movie/now-playing', { params: { page } }),
  getUpcomingMovies: (page = 1) => api.get('/tmdb/movie/upcoming', { params: { page } }),
  getTopRatedMovies: (page = 1) => api.get('/tmdb/movie/top-rated', { params: { page } }),
  getTopRatedTv: (page = 1) => api.get('/tmdb/tv/top-rated', { params: { page } }),
  getPerson: (personId) => api.get(`/tmdb/person/${personId}`),
  getGenres: (mediaType = 'movie') => api.get(`/tmdb/genres/${mediaType}`),
  // 新增 API
  discoverMovies: (params) => api.get('/tmdb/discover/movie', { params }),
  discoverTv: (params) => api.get('/tmdb/discover/tv', { params }),
  getNetworks: () => api.get('/tmdb/networks'),
  getWatchProviders: (mediaType, mediaId) => api.get(`/tmdb/watch-providers/${mediaType}/${mediaId}`),
  getMovieRecommendations: (movieId, page = 1) => api.get(`/tmdb/movie/${movieId}/recommendations`, { params: { page } }),
  getTvRecommendations: (tvId, page = 1) => api.get(`/tmdb/tv/${tvId}/recommendations`, { params: { page } }),
  getMovieSimilar: (movieId, page = 1) => api.get(`/tmdb/movie/${movieId}/similar`, { params: { page } }),
  getTvSimilar: (tvId, page = 1) => api.get(`/tmdb/tv/${tvId}/similar`, { params: { page } }),
}

// Recommend API (推荐系统)
export const recommendApi = {
  getForYou: (userId, limit = 20) => api.get('/recommend/for-you', { params: { user_id: userId, limit } }),
  getBecauseYouWatched: (embyId, userId, limit = 10) => api.get(`/recommend/because-you-watched/${embyId}`, { params: { user_id: userId, limit } }),
  getSimilar: (mediaType, tmdbId, page = 1) => api.get(`/recommend/similar/${mediaType}/${tmdbId}`, { params: { page } }),
  getTrendingByGenre: (genreId, mediaType = 'movie', page = 1) => api.get('/recommend/trending-by-genre', { params: { genre_id: genreId, media_type: mediaType, page } }),
  getByNetwork: (networkId, page = 1) => api.get(`/recommend/by-network/${networkId}`, { params: { page } }),
  getGenrePreferences: (userId) => api.get('/recommend/genre-preferences', { params: { user_id: userId } }),
}

// Lists API (自定义列表)
export const listsApi = {
  getLists: (userId) => api.get('/lists/', { params: { user_id: userId } }),
  createList: (userId, data) => api.post('/lists/', data, { params: { user_id: userId } }),
  getList: (listId, userId) => api.get(`/lists/${listId}`, { params: { user_id: userId } }),
  updateList: (listId, userId, data) => api.put(`/lists/${listId}`, data, { params: { user_id: userId } }),
  deleteList: (listId, userId) => api.delete(`/lists/${listId}`, { params: { user_id: userId } }),
  addItem: (listId, userId, data) => api.post(`/lists/${listId}/items`, data, { params: { user_id: userId } }),
  removeItem: (listId, itemId, userId) => api.delete(`/lists/${listId}/items/${itemId}`, { params: { user_id: userId } }),
  reorderItems: (listId, userId, itemIds) => api.post(`/lists/${listId}/reorder`, itemIds, { params: { user_id: userId } }),
}

// Ratings API (用户评分)
export const ratingsApi = {
  getRatings: (userId, params) => api.get('/ratings/', { params: { user_id: userId, ...params } }),
  createRating: (userId, data) => api.post('/ratings/', data, { params: { user_id: userId } }),
  checkRating: (userId, params) => api.get('/ratings/check', { params: { user_id: userId, ...params } }),
  updateRating: (ratingId, userId, data) => api.put(`/ratings/${ratingId}`, data, { params: { user_id: userId } }),
  deleteRating: (ratingId, userId) => api.delete(`/ratings/${ratingId}`, { params: { user_id: userId } }),
  getStats: (userId) => api.get('/ratings/stats', { params: { user_id: userId } }),
}

// Export API (数据导出)
export const exportApi = {
  exportHistory: (userId, format = 'json') => `/api/export/history?user_id=${userId}&format=${format}`,
  exportWatchlist: (format = 'json') => `/api/export/watchlist?format=${format}`,
  exportRatings: (userId, format = 'json') => `/api/export/ratings?user_id=${userId}&format=${format}`,
  exportLists: (userId) => `/api/export/lists?user_id=${userId}`,
  exportFullBackup: (userId) => `/api/export/full-backup?user_id=${userId}`,
  importTraktHistory: (userId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/export/import/trakt-history?user_id=${userId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  importBackup: (userId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/export/import/backup?user_id=${userId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}

// Check-in API (签到)
export const checkinApi = {
  create: (userId, data) => api.post('/checkin/', data, { params: { user_id: userId } }),
  getCurrent: (userId) => api.get('/checkin/current', { params: { user_id: userId } }),
  end: (userId, checkinId) => api.post('/checkin/end', null, { params: { user_id: userId, checkin_id: checkinId } }),
  getHistory: (userId, params) => api.get('/checkin/history', { params: { user_id: userId, ...params } }),
  delete: (checkinId, userId) => api.delete(`/checkin/${checkinId}`, { params: { user_id: userId } }),
}

// Watchlist API
export const watchlistApi = {
  getWatchlist: (mediaType) => api.get('/watchlist/', { params: { media_type: mediaType } }),
  addToWatchlist: (item) => api.post('/watchlist/', item),
  removeFromWatchlist: (itemId) => api.delete(`/watchlist/${itemId}`),
  checkInWatchlist: (params) => api.get('/watchlist/check', { params }),
  getHistory: (params) => api.get('/watchlist/history', { params }),
  addHistory: (item) => api.post('/watchlist/history', item),
  deleteHistory: (itemId) => api.delete(`/watchlist/history/${itemId}`),
}

// Stats API
export const statsApi = {
  getStats: (userId, libraryIds) => api.get('/stats/', { params: { user_id: userId, library_ids: libraryIds } }),
  getOverview: (userId, libraryIds) => api.get(`/stats/overview/${userId}`, { params: { library_ids: libraryIds } }),
  getGenreStats: (userId, libraryIds, mediaType) => api.get(`/stats/genres/${userId}`, { params: { library_ids: libraryIds, media_type: mediaType } }),
  getYearStats: (userId, libraryIds, mediaType) => api.get(`/stats/years/${userId}`, { params: { library_ids: libraryIds, media_type: mediaType } }),
  getRatingStats: (userId, libraryIds, mediaType) => api.get(`/stats/ratings/${userId}`, { params: { library_ids: libraryIds, media_type: mediaType } }),
  getRecentWatched: (userId, libraryIds, mediaType, limit) => api.get(`/stats/recent/${userId}`, { params: { library_ids: libraryIds, media_type: mediaType, limit } }),
  getTopRated: (userId, libraryIds, mediaType, limit) => api.get(`/stats/top-rated/${userId}`, { params: { library_ids: libraryIds, media_type: mediaType, limit } }),
  // 新增统计 API
  getTrends: (userId, days = 30) => api.get(`/stats/trends/${userId}`, { params: { days } }),
  getTimeDistribution: (userId) => api.get(`/stats/time-distribution/${userId}`),
  getHeatmap: (userId, weeks = 12) => api.get(`/stats/heatmap/${userId}`, { params: { weeks } }),
  getStreak: (userId) => api.get(`/stats/streak/${userId}`),
  getMonthlyStats: (userId, year) => api.get(`/stats/monthly/${userId}`, { params: { year } }),
  getWeekdayStats: (userId) => api.get(`/stats/weekday/${userId}`),
  getYearlyReview: (userId, year) => api.get(`/stats/yearly-review/${userId}`, { params: { year } }),
}

// History API (本地存储的观看历史)
export const historyApi = {
  getHistory: (userId, params) => api.get('/history/', { params: { user_id: userId, ...params } }),
  getGenres: (userId) => api.get('/history/genres', { params: { user_id: userId } }),
  syncFromEmby: (userId) => api.post('/history/sync', null, { params: { user_id: userId } }),
  addHistory: (userId, data) => api.post('/history/', data, { params: { user_id: userId } }),
  updateHistory: (historyId, data) => api.put(`/history/${historyId}`, data),
  deleteHistory: (historyId) => api.delete(`/history/${historyId}`),
  getStats: (userId) => api.get('/history/stats', { params: { user_id: userId } }),
}

// Hero Slides API (轮播海报管理)
export const heroApi = {
  getSlides: (activeOnly = true) => api.get('/hero/', { params: { active_only: activeOnly } }),
  createSlide: (data) => api.post('/hero/', data),
  updateSlide: (id, data) => api.put(`/hero/${id}`, data),
  deleteSlide: (id) => api.delete(`/hero/${id}`),
  reorderSlides: (order) => api.post('/hero/reorder', order),
}

// Config API
export const configApi = {
  getConfig: () => api.get('/config'),
  healthCheck: () => api.get('/health'),
}

// Calendar API (日历)
export const calendarApi = {
  getShowsCalendar: (startDate, endDate, userId) => api.get('/calendar/shows', { params: { start_date: startDate, end_date: endDate, user_id: userId } }),
  getMoviesCalendar: (startDate, endDate) => api.get('/calendar/movies', { params: { start_date: startDate, end_date: endDate } }),
  getAllCalendar: (startDate, endDate, userId) => api.get('/calendar/all', { params: { start_date: startDate, end_date: endDate, user_id: userId } }),
  getMyShowsCalendar: (startDate, endDate, userId) => api.get('/calendar/my-shows', { params: { start_date: startDate, end_date: endDate, user_id: userId } }),
  exportIcal: (userId) => `/api/calendar/ical?user_id=${userId}`,
}

// Progress API (剧集进度)
export const progressApi = {
  getShowsProgress: (userId) => api.get('/progress/shows', { params: { user_id: userId } }),
  getShowProgress: (seriesId, userId) => api.get(`/progress/show/${seriesId}`, { params: { user_id: userId } }),
  getProgressStats: (userId) => api.get('/progress/stats', { params: { user_id: userId } }),
  cleanupDuplicates: (userId, dryRun = true) => api.delete('/progress/cleanup-duplicates', { params: { user_id: userId, dry_run: dryRun } }),
}

// External Ratings API (外部评分 - IMDB/烂番茄/Metacritic)
export const externalRatingsApi = {
  getRatings: (params) => api.get('/external-ratings/', { params }),
  // 强制刷新单个媒体的外部评分
  refreshRatings: (params) => api.get('/external-ratings/', { params: { ...params, force: true } }),
  search: (query, mediaType = 'movie', page = 1) => api.get('/external-ratings/search', { params: { query, media_type: mediaType, page } }),
  getStatus: () => api.get('/external-ratings/status'),
  resetKeys: () => api.post('/external-ratings/reset-keys'),
  getSyncStatus: () => api.get('/external-ratings/sync-status'),
  startSync: (userId, force = false) => api.post('/external-ratings/sync', null, { params: { user_id: userId, force } }),
  getCachedCount: () => api.get('/external-ratings/cached-count'),
  getAllCached: (limit = 5000) => api.get('/external-ratings/cached', { params: { limit } }),
}

// Sync API (同步管理)
export const syncApi = {
  getStatus: () => api.get('/sync/status'),
  getUserStatus: (userId) => api.get(`/sync/status/${userId}`),
  triggerSync: (userId = null) => api.post('/sync/trigger', null, { params: userId ? { user_id: userId } : {} }),
  getLibraries: (userId, useCache = true) => api.get(`/sync/libraries/${userId}`, { params: { use_cache: useCache } }),
  refreshLibraries: (userId) => api.post(`/sync/libraries/${userId}/refresh`),
}

export default api
