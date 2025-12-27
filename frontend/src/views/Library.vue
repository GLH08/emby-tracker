<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题和筛选 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ library?.name || '媒体库' }}</h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1">{{ getLibraryTypeText(library?.collection_type) }}</p>
      </div>
      
      <div class="flex flex-wrap items-center gap-3">
        <!-- 搜索 -->
        <div class="relative">
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="搜索..."
            class="input pl-10 w-48"
            @keyup.enter="search"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>

        <!-- 排序 -->
        <select v-model="sortBy" @change="fetchItems()" class="input w-auto">
          <option value="SortName">名称</option>
          <option value="DateCreated">添加时间</option>
          <option value="PremiereDate">上映日期</option>
          <option value="CommunityRating">评分</option>
        </select>

        <!-- 筛选 -->
        <select v-model="filter" @change="fetchItems()" class="input w-auto">
          <option value="">全部</option>
          <option value="IsPlayed">已看</option>
          <option value="IsUnplayed">未看</option>
          <option value="IsFavorite">收藏</option>
        </select>
      </div>
    </div>

    <!-- 统计信息和分页信息 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
        <span>共 {{ totalCount }} 项</span>
        <span v-if="watchedCount > 0">已看 {{ watchedCount }} 项</span>
      </div>
      <div class="text-sm text-gray-500 dark:text-gray-400">
        第 {{ currentPage }} / {{ totalPages }} 页
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      <div v-for="i in pageSize" :key="i" class="animate-pulse">
        <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100 rounded-xl"></div>
        <div class="mt-3 h-4 bg-gray-200 dark:bg-dark-100 rounded w-3/4"></div>
        <div class="mt-2 h-3 bg-gray-200 dark:bg-dark-100 rounded w-1/2"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="items.length === 0" class="text-center py-16">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">暂无内容</p>
    </div>

    <!-- 内容列表 -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      <MediaCard 
        v-for="item in items" 
        :key="item.id"
        :item="item"
      />
    </div>

    <!-- 分页控件 -->
    <div v-if="totalPages > 1" class="mt-8 flex items-center justify-center space-x-2">
      <button 
        @click="goToPage(1)"
        :disabled="currentPage === 1"
        class="btn btn-secondary px-3 py-2"
        :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
        </svg>
      </button>
      <button 
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-secondary px-3 py-2"
        :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      
      <!-- 页码按钮 -->
      <template v-for="page in visiblePages" :key="page">
        <span v-if="page === '...'" class="px-2 text-gray-400">...</span>
        <button 
          v-else
          @click="goToPage(page)"
          class="btn px-4 py-2"
          :class="page === currentPage ? 'btn-primary' : 'btn-secondary'"
        >
          {{ page }}
        </button>
      </template>
      
      <button 
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-secondary px-3 py-2"
        :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </button>
      <button 
        @click="goToPage(totalPages)"
        :disabled="currentPage === totalPages"
        class="btn btn-secondary px-3 py-2"
        :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import { embyApi } from '../api'
import MediaCard from '../components/MediaCard.vue'

const route = useRoute()
const appStore = useAppStore()

const items = ref([])
const loading = ref(true)
const totalCount = ref(0)
const watchedCount = ref(0)
const searchQuery = ref('')
const sortBy = ref('SortName')
const filter = ref('')
const currentPage = ref(1)
const pageSize = 36 // 每页显示数量

const library = computed(() => {
  return appStore.allowedLibraries.find(l => l.id === route.params.id)
})

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize) || 1)

// 计算可见的页码
const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

const getLibraryTypeText = (type) => {
  const map = {
    'movies': '电影',
    'tvshows': '剧集',
    'music': '音乐',
    'musicvideos': '音乐视频',
    'homevideos': '家庭视频',
    'boxsets': '合集',
    'books': '书籍',
    'photos': '照片',
  }
  return map[type] || type || ''
}

const getItemTypes = () => {
  const type = library.value?.collection_type
  if (type === 'movies') return 'Movie'
  if (type === 'tvshows') return 'Series'
  return 'Movie,Series,Video'
}

const fetchItems = async () => {
  if (!appStore.currentEmbyUser || !library.value) return
  
  loading.value = true
  
  try {
    const startIndex = (currentPage.value - 1) * pageSize
    
    const result = await embyApi.getItems(appStore.currentEmbyUser.Id, {
      parent_id: library.value.id,
      include_item_types: getItemTypes(),
      sort_by: sortBy.value,
      sort_order: sortBy.value === 'SortName' ? 'Ascending' : 'Descending',
      start_index: startIndex,
      limit: pageSize,
      filters: filter.value || undefined,
      search_term: searchQuery.value || undefined,
    })
    
    items.value = result.items
    totalCount.value = result.total_count
    
    // 获取已看数量（仅首次加载）
    if (!filter.value && watchedCount.value === 0) {
      const watchedResult = await embyApi.getItems(appStore.currentEmbyUser.Id, {
        parent_id: library.value.id,
        include_item_types: getItemTypes(),
        is_played: true,
        limit: 1,
      })
      watchedCount.value = watchedResult.total_count
    }
  } catch (e) {
    console.error('Failed to fetch items:', e)
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  fetchItems()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const search = () => {
  currentPage.value = 1
  fetchItems()
}

watch(() => route.params.id, () => {
  currentPage.value = 1
  watchedCount.value = 0
  fetchItems()
})

watch(() => appStore.currentEmbyUser, () => {
  currentPage.value = 1
  watchedCount.value = 0
  fetchItems()
})

onMounted(() => {
  if (appStore.currentEmbyUser && library.value) {
    fetchItems()
  }
})
</script>
