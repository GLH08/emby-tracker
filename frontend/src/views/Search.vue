<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 搜索框 -->
    <div class="max-w-2xl mx-auto mb-12">
      <div class="relative">
        <input 
          v-model="query"
          type="text"
          placeholder="搜索电影、剧集..."
          class="w-full px-6 py-4 pl-14 text-lg rounded-2xl border-2 border-gray-200 dark:border-dark-100 bg-white dark:bg-dark-300 focus:outline-none focus:border-primary-500 transition-colors"
          @keyup.enter="search"
          autofocus
        />
        <svg class="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <button 
          v-if="query"
          @click="query = ''; results = []"
          class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- 搜索类型 -->
      <div class="flex justify-center space-x-4 mt-4">
        <button 
          @click="searchType = 'emby'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="searchType === 'emby' 
            ? 'bg-primary-500 text-white' 
            : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
        >
          搜索媒体库
        </button>
        <button 
          @click="searchType = 'tmdb'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="searchType === 'tmdb' 
            ? 'bg-primary-500 text-white' 
            : 'bg-gray-100 dark:bg-dark-100 text-gray-600 dark:text-gray-400'"
        >
          搜索 TMDB
        </button>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <div v-else-if="searched && results.length === 0" class="text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">未找到相关结果</p>
    </div>

    <MediaGrid 
      v-else-if="results.length > 0"
      :items="results"
      :source="searchType"
      :media-type="searchType === 'tmdb' ? 'movie' : ''"
    />

    <!-- 热门搜索 -->
    <div v-if="!searched && !loading" class="mt-8">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">热门搜索</h2>
      <div class="flex flex-wrap gap-3">
        <button 
          v-for="term in hotSearches" 
          :key="term"
          @click="query = term; search()"
          class="px-4 py-2 bg-gray-100 dark:bg-dark-100 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-dark-200 transition-colors"
        >
          {{ term }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/app'
import { embyApi, tmdbApi } from '../api'
import MediaGrid from '../components/MediaGrid.vue'

const appStore = useAppStore()
const query = ref('')
const searchType = ref('emby')
const loading = ref(false)
const searched = ref(false)
const results = ref([])

const hotSearches = ['复仇者联盟', '权力的游戏', '星际穿越', '绝命毒师', '盗梦空间', '怪奇物语']

const search = async () => {
  if (!query.value.trim()) return
  
  loading.value = true
  searched.value = true
  results.value = []
  
  try {
    if (searchType.value === 'emby' && appStore.currentEmbyUser) {
      const result = await embyApi.getItems(appStore.currentEmbyUser.Id, {
        search_term: query.value,
        include_item_types: 'Movie,Series',
        limit: 50,
      })
      results.value = result.items
    } else {
      const result = await tmdbApi.searchMulti(query.value)
      results.value = result.results
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
    loading.value = false
  }
}
</script>
