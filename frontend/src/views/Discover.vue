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

    <!-- 分类标签 -->
    <div v-else>
      <div class="flex overflow-x-auto space-x-2 mb-8 pb-2 scrollbar-hide">
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
import { tmdbApi } from '../api'
import MediaGrid from '../components/MediaGrid.vue'

const appStore = useAppStore()
const loading = ref(true)
const loadingMore = ref(false)
const loadingSearch = ref(false)
const items = ref([])
const searchResults = ref([])
const page = ref(1)
const totalPages = ref(1)
const activeTab = ref('trending')
const searchQuery = ref('')
const isSearching = ref(false)

const tabs = [
  { key: 'trending', name: '热门趋势' },
  { key: 'popular_movies', name: '热门电影' },
  { key: 'popular_tv', name: '热门剧集' },
  { key: 'now_playing', name: '正在上映' },
  { key: 'upcoming', name: '即将上映' },
  { key: 'top_rated_movies', name: '高分电影' },
  { key: 'top_rated_tv', name: '高分剧集' },
]

const hasMore = computed(() => page.value < totalPages.value)

const getMediaType = () => {
  if (activeTab.value === 'trending') return 'mixed'
  if (activeTab.value.includes('tv')) return 'tv'
  return 'movie'
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
    }
    
    if (result && result.results) {
      const newItems = result.results.map(item => ({
        ...item,
        id: item.id,
        name: item.title || item.name,
        media_type: item.media_type || (activeTab.value.includes('tv') ? 'tv' : 'movie'),
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

const loadMore = () => {
  page.value++
  fetchData()
}

watch(activeTab, () => fetchData(true))

onMounted(() => fetchData(true))
</script>
