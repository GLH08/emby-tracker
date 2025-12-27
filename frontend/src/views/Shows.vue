<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题和筛选 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">剧集</h1>
      
      <div class="flex flex-wrap items-center gap-3">
        <!-- 搜索 -->
        <div class="relative">
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="搜索剧集..."
            class="input pl-10 w-48"
            @keyup.enter="search"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>

        <!-- 排序 -->
        <select v-model="sortBy" @change="fetchShows(true)" class="input w-auto">
          <option value="SortName">名称</option>
          <option value="DateCreated">添加时间</option>
          <option value="PremiereDate">首播日期</option>
          <option value="CommunityRating">评分</option>
        </select>

        <!-- 筛选 -->
        <select v-model="filter" @change="fetchShows(true)" class="input w-auto">
          <option value="">全部</option>
          <option value="IsPlayed">已看</option>
          <option value="IsUnplayed">未看</option>
          <option value="IsFavorite">收藏</option>
        </select>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="flex items-center space-x-6 mb-6 text-sm text-gray-500 dark:text-gray-400">
      <span>共 {{ totalCount }} 部剧集</span>
    </div>

    <!-- 剧集列表 -->
    <MediaGrid 
      :items="shows"
      :loading="loading"
      :loading-more="loadingMore"
      :has-more="hasMore"
      empty-text="暂无剧集"
      @load-more="loadMore"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { embyApi } from '../api'
import MediaGrid from '../components/MediaGrid.vue'

const appStore = useAppStore()
const shows = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const totalCount = ref(0)
const searchQuery = ref('')
const sortBy = ref('SortName')
const filter = ref('')
const startIndex = ref(0)
const limit = 30

const hasMore = computed(() => shows.value.length < totalCount.value)

const fetchShows = async (reset = false) => {
  if (!appStore.currentEmbyUser) return
  
  if (reset) {
    startIndex.value = 0
    shows.value = []
  }
  
  loading.value = reset
  loadingMore.value = !reset
  
  try {
    // 使用 store 中的剧集库（第一个）
    const tvLibrary = appStore.tvLibraries[0]
    
    const result = await embyApi.getItems(appStore.currentEmbyUser.Id, {
      parent_id: tvLibrary?.id,
      include_item_types: 'Series',
      sort_by: sortBy.value,
      sort_order: sortBy.value === 'SortName' ? 'Ascending' : 'Descending',
      start_index: startIndex.value,
      limit,
      filters: filter.value || undefined,
      search_term: searchQuery.value || undefined,
    })
    
    if (reset) {
      shows.value = result.items
    } else {
      shows.value.push(...result.items)
    }
    totalCount.value = result.total_count
  } catch (e) {
    console.error('Failed to fetch shows:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  startIndex.value += limit
  fetchShows()
}

const search = () => {
  fetchShows(true)
}

watch(() => appStore.currentEmbyUser, () => fetchShows(true))
watch(() => appStore.tvLibraries, () => fetchShows(true))

onMounted(() => {
  if (appStore.currentEmbyUser && appStore.tvLibraries.length > 0) {
    fetchShows(true)
  }
})
</script>
