import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { embyApi, configApi, authApi } from '../api'

export const useAppStore = defineStore('app', () => {
  // 状态
  const darkMode = ref(localStorage.getItem('darkMode') === 'true')
  const config = ref(null)
  
  // 认证状态
  const token = ref(localStorage.getItem('token'))
  const currentSystemUser = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isAuthenticated = computed(() => !!token.value && !!currentSystemUser.value)
  const isAdmin = computed(() => currentSystemUser.value?.is_admin || false)
  
  // Emby 状态
  const embyUsers = ref([])
  const currentEmbyUser = ref(null)
  const libraries = ref([])
  const selectedLibraryId = ref(localStorage.getItem('selectedLibraryId') || null)
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const embyUrl = computed(() => config.value?.emby_url || '')
  const tmdbImageBaseUrl = computed(() => config.value?.tmdb_image_base_url || 'https://image.tmdb.org/t/p')
  
  // 可访问的 Emby 用户（管理员可访问所有，访客只能访问允许的）
  const allowedEmbyUsers = computed(() => {
    if (!currentSystemUser.value) return []
    if (currentSystemUser.value.is_admin) return embyUsers.value
    const allowed = currentSystemUser.value.allowed_emby_users || []
    return embyUsers.value.filter(u => allowed.includes(u.Id))
  })
  
  // 可访问的媒体库
  const allowedLibraries = computed(() => {
    if (!currentSystemUser.value) return []
    if (currentSystemUser.value.is_admin) return libraries.value
    const allowed = currentSystemUser.value.allowed_libraries || []
    if (allowed.length === 0) return libraries.value // 如果没有限制，返回所有
    return libraries.value.filter(l => allowed.includes(l.id))
  })
  
  // 当前选中的媒体库
  const currentLibrary = computed(() => {
    if (!selectedLibraryId.value) return null
    return allowedLibraries.value.find(l => l.id === selectedLibraryId.value)
  })
  
  // 按类型分组的媒体库
  const movieLibraries = computed(() => {
    return allowedLibraries.value.filter(l => l.collection_type === 'movies')
  })
  
  const tvLibraries = computed(() => {
    return allowedLibraries.value.filter(l => l.collection_type === 'tvshows')
  })

  // 方法
  const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value)
    updateDarkModeClass()
  }

  const updateDarkModeClass = () => {
    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const fetchConfig = async () => {
    try {
      config.value = await configApi.getConfig()
    } catch (e) {
      console.error('Failed to fetch config:', e)
    }
  }

  // 认证方法
  const login = async (username, password) => {
    const result = await authApi.login(username, password)
    token.value = result.token
    currentSystemUser.value = result.user
    localStorage.setItem('token', result.token)
    localStorage.setItem('user', JSON.stringify(result.user))
    return result
  }

  const logout = () => {
    token.value = null
    currentSystemUser.value = null
    currentEmbyUser.value = null
    libraries.value = []
    embyUsers.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentEmbyUserId')
    localStorage.removeItem('selectedLibraryId')
  }

  const refreshUser = async () => {
    if (!token.value) return
    try {
      currentSystemUser.value = await authApi.getMe()
      localStorage.setItem('user', JSON.stringify(currentSystemUser.value))
    } catch (e) {
      logout()
    }
  }

  // Emby 方法
  const fetchEmbyUsers = async () => {
    try {
      embyUsers.value = await embyApi.getUsers()
      // 选择第一个允许的用户
      if (allowedEmbyUsers.value.length > 0 && !currentEmbyUser.value) {
        const savedUserId = localStorage.getItem('currentEmbyUserId')
        const savedUser = allowedEmbyUsers.value.find(u => u.Id === savedUserId)
        currentEmbyUser.value = savedUser || allowedEmbyUsers.value[0]
      }
    } catch (e) {
      console.error('Failed to fetch emby users:', e)
      error.value = '无法连接到 Emby 服务器'
    }
  }

  const setCurrentEmbyUser = (user) => {
    currentEmbyUser.value = user
    localStorage.setItem('currentEmbyUserId', user.Id)
    fetchLibraries()
  }

  const fetchLibraries = async () => {
    if (!currentEmbyUser.value) return
    try {
      libraries.value = await embyApi.getLibraries(currentEmbyUser.value.Id)
    } catch (e) {
      console.error('Failed to fetch libraries:', e)
    }
  }

  const selectLibrary = (libraryId) => {
    selectedLibraryId.value = libraryId
    localStorage.setItem('selectedLibraryId', libraryId)
  }

  const getEmbyImageUrl = (itemId, imageType = 'Primary', maxWidth = 400) => {
    if (!embyUrl.value || !itemId) return ''
    return `${embyUrl.value}/Items/${itemId}/Images/${imageType}?maxWidth=${maxWidth}`
  }

  const getTmdbImageUrl = (path, size = 'w500') => {
    if (!path) return ''
    return `${tmdbImageBaseUrl.value}/${size}${path}`
  }

  const init = async () => {
    updateDarkModeClass()
    await fetchConfig()
    
    if (isAuthenticated.value) {
      await refreshUser()
      await fetchEmbyUsers()
      if (currentEmbyUser.value) {
        await fetchLibraries()
      }
    }
  }

  return {
    // 状态
    darkMode,
    config,
    token,
    currentSystemUser,
    isAuthenticated,
    isAdmin,
    embyUsers,
    currentEmbyUser,
    libraries,
    selectedLibraryId,
    loading,
    error,
    // 计算属性
    embyUrl,
    tmdbImageBaseUrl,
    allowedEmbyUsers,
    allowedLibraries,
    currentLibrary,
    movieLibraries,
    tvLibraries,
    // 方法
    toggleDarkMode,
    fetchConfig,
    login,
    logout,
    refreshUser,
    fetchEmbyUsers,
    setCurrentEmbyUser,
    fetchLibraries,
    selectLibrary,
    getEmbyImageUrl,
    getTmdbImageUrl,
    init,
  }
})
