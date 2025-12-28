<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">发现</h1>
      <!-- 搜索框 -->
      <div class="relative w-80">
        <input
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text"
          placeholder="搜索电影、剧集..."
          class="w-full px-4 py-2 pl-10 rounded-lg border border-gray-300 dark:border-dark-100 bg-white dark:bg-dark-200 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <button v-if="searchQuery" @click="clearSearch" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="isSearching" class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">搜索结果: "{{ searchQuery }}"</h2>
        <button @click="clearSearch" class="text-primary-500 hover:text-primary-600">返回发现</button>
      </div>
      <MediaGrid 
        :items="searchResults"
        :loading="loadingSearch"
        :loading-more="false"
        :has-more="false"
        media-type="mixed"
        source="tmdb"
      />
      <div v-if="!loadingSearch && searchResults.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        未找到相关内容
      </div>
    </div>

    <!-- 主内容 -->
    <div v-else>
      <!-- 为你推荐 -->
      <section v-if="recommendations.length > 0" class="mb-10">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">为你推荐</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ recommendReason }}</p>
          </div>
          <button @click="refreshRecommendations" class="text-primary-500 hover:text-primary-600 text-sm">
            换一批
          </button>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <router-link
            v-for="item in recommendations.slice(0, 10)"
            :key="`rec-${item.id}`"
            :to="`/tmdb/${item.media_type}/${item.id}`"
            class="group"
          >
            <div class="aspect-[2/3] rounded-xl overflow-hidden bg-gray-100 dark:bg-dark-100 relative">
              <img
                v-if="item.poster_path"
                :src="`${appStore.tmdbImageBaseUrl}/w342${item.poster_path}`"
                :alt="item.title || item.name"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
                </svg>
              </div>
              <!-- 类型标签 -->
              <div class="absolute top-2 left-2">
                <span class="px-2 py-0.5 text-xs font-medium rounded bg-black/60 text-white">
                  {{ item.media_type === 'movie' ? '电影' : '剧集' }}
                </span>
              </div>
              <!-- 评分 -->
              <div v-if="item.vote_average" class="absolute top-2 right-2 flex items-center bg-black/60 rounded px-1.5 py-0.5">
                <svg class="w-3 h-3 text-yellow-400 mr-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="text-xs text-white">{{ item.vote_average.toFixed(1) }}</span>
              </div>
            </div>
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white truncate">{{ item.title || item.name }}</h3>
            <p v-if="item.reason" class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ item.reason }}</p>
          </router-link>
        </div>
      </section>

      <!-- 分类标签 -->
      <div class="flex overflow-x-auto space-x-2 mb-6 pb-2 scrollbar-hide">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="flex-shrink-0 px-4 py-2 rounded-lg font-medium transition-colors"
          :class="activeTab === tab.key 
            ? 'bg-primary-500 text-white' 
            : 'bg-gray-100 dark:bg-dark-100 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-200'"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- 筛选器 -->
      <div class="flex flex-wrap items-center gap-3 mb-6">
        <!-- 类型筛选 -->
        <select v-model="filterGenre" @change="applyFilters" class="input w-auto text-sm py-1.5">
          <option value="">全部类型</option>
          <option v-for="genre in genres" :key="genre.id" :value="genre.id">{{ genre.name }}</option>
        </select>
        
        <!-- 年份筛选 -->
        <select v-model="filterYear" @change="applyFilters" class="input w-auto text-sm py-1.5">
          <option value="">全部年份</option>
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
        
        <!-- 网络筛选（仅剧集） -->
        <select 
          v-if="activeTab.includes('tv') || activeTab === 'by_network'"
          v-model="filterNetwork" 
          @change="applyFilters" 
          class="input w-auto text-sm py-1.5"
        >
          <option value="">全部平台</option>
          <option v-for="network in networks" :key="network.id" :value="network.id">{{ network.name }}</option>
        </select>
        
        <!-- 排序 -->
        <select v-model="sortBy" @change="applyFilters" class="input w-auto text-sm py-1.5">
          <option value="popularity.desc">热门优先</option>
          <option value="vote_average.desc">评分优先</option>
          <option value="release_date.desc">最新优先</option>
          <option value="release_date.asc">最早优先</option>
        </select>
        
        <!-- 清除筛选 -->
        <button 
          v-if="filterGenre || filterYear || filterNetwork"
          @click="clearFilters"
          class="text-sm text-primary-500 hover:text-primary-600"
        >
          清除筛选
        </button>
      </div>

      <!-- 内容 -->
      <MediaGrid 
        :items="items"
        :loading="loading"
        :loading-more="loadingMore"
        :has-more="hasMore"
        :media-type="getMediaType()"
        source="tmdb"
        @load-more="loadMore"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { tmdbApi, recommendApi } from '../api'
import MediaGrid from '../components/MediaGrid.vue'

const appStore = useAppStore()
const loading = ref(true)
const loadingMore = ref(false)
const loadingSearch = ref(false)
const items = ref([])
const searchResults = ref([])
const recommendations = ref([])
const recommendReason = ref('')
const page = ref(1)
const totalPages = ref(1)
const activeTab = ref('trending')
const searchQuery = ref('')
const isSearching = ref(false)

// 筛选器
const filterGenre = ref('')
const filterYear = ref('')
const filterNetwork = ref('')
const sortBy = ref('popularity.desc')
const genres = ref([])
const networks = ref([])

// 年份列表
const currentYear = new Date().getFullYear()
const years = Array.from({ length: 50 }, (_, i) => currentYear - i)

const tabs = [
  { key: 'trending', name: '热门趋势' },
  { key: 'popular_movies', name: '热门电影' },
  { key: 'popular_tv', name: '热门剧集' },
  { key: 'now_playing', name: '正在上映' },
  { key: 'upcoming', name: '即将上映' },
  { key: 'top_rated_movies', name: '高分电影' },
  { key: 'top_rated_tv', name: '高分剧集' },
  { key: 'by_network', name: '按平台' },
]

const hasMore = computed(() => page.value < totalPages.value)

const getMediaType = () => {
  if (activeTab.value === 'trending') return 'mixed'
  if (activeTab.value.includes('tv') || activeTab.value === 'by_network') return 'tv'
  return 'movie'
}

const fetchGenres = async () => {
  try {
    const mediaType = getMediaType() === 'tv' ? 'tv' : 'movie'
    const result = await tmdbApi.getGenres(mediaType)
    genres.value = result.genres || []
  } catch (e) {
    console.error('Failed to fetch genres:', e)
  }
}

const fetchNetworks = async () => {
  try {
    const result = await tmdbApi.getNetworks()
    networks.value = result.networks || []
  } catch (e) {
    console.error('Failed to fetch networks:', e)
  }
}

const fetchRecommendations = async () => {
  if (!appStore.currentEmbyUser) return
  
  try {
    const result = await recommendApi.getForYou(appStore.currentEmbyUser.Id, 20)
    recommendations.value = result.items || []
    recommendReason.value = result.reason || '基于你的观看偏好'
  } catch (e) {
    console.error('Failed to fetch recommendations:', e)
  }
}

const refreshRecommendations = () => {
  fetchRecommendations()
}

const fetchData = async (reset = false) => {
  if (reset) {
    page.value = 1
    items.value = []
  }
  
  loading.value = reset
  loadingMore.value = !reset
  
  try {
    let result
    const mediaType = getMediaType()
    
    // 如果有筛选条件，使用 discover API
    if (filterGenre.value || filterYear.value || filterNetwork.value) {
      const params = {
        page: page.value,
        sort_by: sortBy.value,
      }
      if (filterGenre.value) params.genre = filterGenre.value
      if (filterYear.value) params.year = filterYear.value
      if (filterNetwork.value) params.network = filterNetwork.value
      
      if (mediaType === 'tv' || activeTab.value === 'by_network') {
        result = await tmdbApi.discoverTv(params)
      } else {
        result = await tmdbApi.discoverMovies(params)
      }
    } else {
      // 使用预设的 API
      switch (activeTab.value) {
        case 'trending':
          result = await tmdbApi.getTrending('all', 'week', page.value)
          break
        case 'popular_movies':
          result = await tmdbApi.getPopularMovies(page.value)
          break
        case 'popular_tv':
          result = await tmdbApi.getPopularTv(page.value)
          break
        case 'now_playing':
          result = await tmdbApi.getNowPlayingMovies(page.value)
          break
        case 'upcoming':
          result = await tmdbApi.getUpcomingMovies(page.value)
          break
        case 'top_rated_movies':
          result = await tmdbApi.getTopRatedMovies(page.value)
          break
        case 'top_rated_tv':
          result = await tmdbApi.getTopRatedTv(page.value)
          break
        case 'by_network':
          if (filterNetwork.value) {
            result = await tmdbApi.discoverTv({ page: page.value, network: filterNetwork.value })
          } else {
            result = await tmdbApi.getPopularTv(page.value)
          }
          break
      }
    }
    
    if (result && result.results) {
      const newItems = result.results.map(item => ({
        ...item,
        id: item.id,
        name: item.title || item.name,
        media_type: item.media_type || mediaType,
      }))
      
      if (reset) {
        items.value = newItems
      } else {
        items.value.push(...newItems)
      }
      
      totalPages.value = result.total_pages || 1
    }
  } catch (e) {
    console.error('Failed to fetch discover data:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  isSearching.value = true
  loadingSearch.value = true
  searchResults.value = []
  
  try {
    const result = await tmdbApi.searchMulti(searchQuery.value.trim())
    if (result && result.results) {
      searchResults.value = result.results
        .filter(item => item.media_type === 'movie' || item.media_type === 'tv')
        .map(item => ({
          ...item,
          id: item.id,
          name: item.title || item.name,
        }))
    }
  } catch (e) {
    console.error('Search failed:', e)
  } finally {
    loadingSearch.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  isSearching.value = false
  searchResults.value = []
}

const applyFilters = () => {
  fetchData(true)
}

const clearFilters = () => {
  filterGenre.value = ''
  filterYear.value = ''
  filterNetwork.value = ''
  sortBy.value = 'popularity.desc'
  fetchData(true)
}

const loadMore = () => {
  page.value++
  fetchData()
}

watch(activeTab, () => {
  clearFilters()
  fetchGenres()
})

watch(() => appStore.currentEmbyUser, fetchRecommendations)

onMounted(async () => {
  await Promise.all([
    fetchData(true),
    fetchGenres(),
    fetchNetworks(),
    fetchRecommendations(),
  ])
})
</script>
