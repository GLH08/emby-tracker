<template>
  <div class="masonry-wall">
    <!-- 加载状态 -->
    <div v-if="loading && items.length === 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      <div v-for="i in 18" :key="i" class="animate-pulse">
        <div class="aspect-[2/3] bg-gray-200 dark:bg-dark-100 rounded-xl"></div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="items.length === 0" class="text-center py-16">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
      </svg>
      <p class="mt-4 text-gray-500 dark:text-gray-400">{{ emptyText }}</p>
    </div>

    <!-- 瀑布流容器 -->
    <div v-else ref="containerRef" class="masonry-container" :style="{ height: containerHeight + 'px' }">
      <div
        v-for="(item, index) in positionedItems"
        :key="item.id"
        class="masonry-item"
        :style="{
          width: itemWidth + 'px',
          transform: `translate(${item.x}px, ${item.y}px)`
        }"
      >
        <router-link :to="getDetailLink(item)" class="block group">
          <div class="relative overflow-hidden rounded-xl bg-gray-200 dark:bg-dark-100 shadow-sm hover:shadow-xl transition-shadow duration-300">
            <img 
              v-if="getPosterUrl(item)"
              :src="getPosterUrl(item)"
              :alt="item.name || item.title"
              class="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
              @error="onImageError($event, item)"
            />
            <div v-else class="aspect-[2/3] flex items-center justify-center text-gray-400">
              <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>

            <!-- 渐变遮罩 -->
            <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

            <!-- 已观看标记 -->
            <div 
              v-if="item.played"
              class="absolute top-2 right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center shadow-lg"
            >
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>

            <!-- 评分 -->
            <div 
              v-if="getRating(item)"
              class="absolute top-2 left-2 px-2 py-1 bg-black/70 rounded-lg flex items-center space-x-1"
            >
              <svg class="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span class="text-white text-xs font-medium">{{ getRating(item).toFixed(1) }}</span>
            </div>

            <!-- 悬停标题 -->
            <div class="absolute bottom-0 left-0 right-0 p-3 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
              <h3 class="text-white font-medium text-sm line-clamp-2 drop-shadow-lg">
                {{ item.name || item.title }}
              </h3>
              <p v-if="getYear(item)" class="text-gray-300 text-xs mt-1">
                {{ getYear(item) }}
              </p>
            </div>
          </div>
        </router-link>
      </div>
    </div>

    <!-- 加载更多 / 滚动加载指示器 -->
    <div ref="loadMoreRef" class="mt-8 text-center">
      <div v-if="loadingMore" class="flex items-center justify-center space-x-2 text-gray-500">
        <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>加载中...</span>
      </div>
      <div v-else-if="!hasMore && items.length > 0" class="text-gray-400 text-sm">
        已加载全部 {{ items.length }} 项
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  loading: Boolean,
  loadingMore: Boolean,
  hasMore: Boolean,
  emptyText: {
    type: String,
    default: '暂无内容'
  },
  source: {
    type: String,
    default: 'emby'
  }
})

const emit = defineEmits(['load-more'])

const appStore = useAppStore()
const containerRef = ref(null)
const loadMoreRef = ref(null)

// 布局相关
const columnCount = ref(6)
const gap = 16
const itemWidth = ref(200)
const containerHeight = ref(0)
const columnHeights = ref([])
const itemPositions = ref([]) // { id, x, y }

// 计算带位置的项目
const positionedItems = computed(() => {
  return props.items.map((item, index) => {
    const pos = itemPositions.value[index]
    return {
      ...item,
      x: pos?.x || 0,
      y: pos?.y || 0
    }
  })
})

// 计算列数和宽度
const calculateColumns = () => {
  if (!containerRef.value) return
  
  const containerWidth = containerRef.value.parentElement?.offsetWidth || window.innerWidth - 64
  
  // 响应式列数
  if (containerWidth >= 1536) {
    columnCount.value = 7
  } else if (containerWidth >= 1280) {
    columnCount.value = 6
  } else if (containerWidth >= 1024) {
    columnCount.value = 5
  } else if (containerWidth >= 768) {
    columnCount.value = 4
  } else if (containerWidth >= 640) {
    columnCount.value = 3
  } else {
    columnCount.value = 2
  }
  
  // 计算每个项目的宽度
  itemWidth.value = (containerWidth - gap * (columnCount.value - 1)) / columnCount.value
}

// 计算瀑布流布局
const calculateLayout = () => {
  if (!props.items.length) {
    containerHeight.value = 0
    return
  }
  
  // 初始化列高度
  columnHeights.value = new Array(columnCount.value).fill(0)
  itemPositions.value = []
  
  // 为每个项目计算位置 - 放到最短的列
  props.items.forEach((item, index) => {
    // 找到最短的列
    const minHeight = Math.min(...columnHeights.value)
    const columnIndex = columnHeights.value.indexOf(minHeight)
    
    // 计算位置
    const x = columnIndex * (itemWidth.value + gap)
    const y = minHeight
    
    itemPositions.value.push({ x, y })
    
    // 更新列高度 (假设海报比例为 2:3)
    const itemHeight = itemWidth.value * 1.5
    columnHeights.value[columnIndex] = y + itemHeight + gap
  })
  
  // 容器高度为最高列的高度
  containerHeight.value = Math.max(...columnHeights.value)
}

// 重新计算布局
const recalculateLayout = () => {
  calculateColumns()
  nextTick(() => {
    calculateLayout()
  })
}

// 无限滚动
let observer = null
const setupIntersectionObserver = () => {
  if (observer) observer.disconnect()
  
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && props.hasMore && !props.loadingMore && !props.loading) {
        emit('load-more')
      }
    },
    { rootMargin: '200px' }
  )
  
  if (loadMoreRef.value) {
    observer.observe(loadMoreRef.value)
  }
}

// 图片加载错误处理
const onImageError = (event, item) => {
  // 可以设置默认图片
  event.target.style.display = 'none'
}

const getPosterUrl = (item) => {
  if (props.source === 'tmdb') {
    return item.poster_path 
      ? appStore.getTmdbImageUrl(item.poster_path, 'w342')
      : ''
  }
  return item.primary_image_tag 
    ? appStore.getEmbyImageUrl(item.id, 'Primary', 342)
    : ''
}

const getRating = (item) => {
  if (props.source === 'tmdb') {
    return item.vote_average
  }
  return item.community_rating
}

const getYear = (item) => {
  if (props.source === 'tmdb') {
    const date = item.release_date || item.first_air_date
    return date ? date.split('-')[0] : ''
  }
  return item.year || ''
}

const getDetailLink = (item) => {
  if (props.source === 'tmdb') {
    const type = item.media_type === 'tv' ? 'tv' : 'movie'
    return `/tmdb/${type}/${item.id}`
  }
  const type = item.type === 'Series' ? 'show' : 'movie'
  return `/${type}/${item.id}`
}

// 监听窗口大小变化
let resizeTimeout = null
const handleResize = () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(recalculateLayout, 150)
}

// 监听数据变化
watch(() => props.items.length, () => {
  nextTick(recalculateLayout)
})

watch(() => props.loading, (newVal) => {
  if (!newVal && props.items.length > 0) {
    nextTick(recalculateLayout)
  }
})

onMounted(() => {
  recalculateLayout()
  setupIntersectionObserver()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
  window.removeEventListener('resize', handleResize)
  clearTimeout(resizeTimeout)
})
</script>

<style scoped>
.masonry-wall {
  @apply w-full;
}

.masonry-container {
  position: relative;
  width: 100%;
}

.masonry-item {
  position: absolute;
  top: 0;
  left: 0;
  transition: transform 0.3s ease;
}
</style>
