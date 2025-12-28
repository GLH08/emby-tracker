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
}

// History API (本地存储的观看历史)
export const historyApi = {
  getHistory: (userId, params) => api.get('/history/', { params: { user_id: userId, ...params } }),
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
}

export default api
