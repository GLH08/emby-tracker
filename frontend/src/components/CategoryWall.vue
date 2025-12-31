<template>
  <div class="category-wall">
    <!-- 加载状态 -->
    <div v-if="loading" class="category-wall-grid">
      <div 
        v-for="i in 12" 
        :key="i"
        class="category-card animate-pulse"
        :class="getSkeletonSizeClass(i)"
      >
        <div class="absolute inset-0 bg-gray-200 dark:bg-dark-100 rounded-2xl"></div>
      </div>
    </div>

    <!-- 分类墙 -->
    <div v-else class="category-wall-grid">
      <router-link
        v-for="(library, index) in librariesWithImages"
        :key="library.id"
        :to="`/library/${library.id}`"
        class="category-card group"
        :class="getCardSizeClass(index, librariesWithImages.length)"
      >
        <!-- 背景图片层 -->
        <div class="absolute inset-0 overflow-hidden rounded-2xl">
          <!-- 多图拼接背景 -->
          <div v-if="library.images && library.images.length > 1" class="absolute inset-0 grid grid-cols-2 grid-rows-2">
            <div 
              v-for="(img, imgIndex) in library.images.slice(0, 4)" 
              :key="imgIndex"
              class="relative overflow-hidden"
            >
              <img 
                :src="img"
                :alt="library.name"
                class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                loading="lazy"
              />
            </div>
          </div>
          <!-- 单图背景 -->
          <img 
            v-else-if="library.images && library.images.length === 1"
            :src="library.images[0]"
            :alt="library.name"
            class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
          />
          <!-- 无图占位 -->
          <div v-else class="absolute inset-0 bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
            <svg class="w-16 h-16 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
            </svg>
          </div>
          
          <!-- 渐变遮罩 -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
        </div>

        <!-- 内容层 -->
        <div class="absolute inset-0 p-4 flex flex-col justify-end">
          <!-- 类型标签 -->
          <div class="mb-2">
            <span 
              class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium backdrop-blur-sm"
              :class="getTypeTagClass(library.collection_type)"
            >
              <svg v-if="library.collection_type === 'movies'" class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm3 2h6v4H7V5zm8 8v2h-2v-2h2zm-2-2H7v4h6v-4zm2 0h2v2h-2v-2zm0-4h2v2h-2V7zm-8-2v2H5V5h2zm-2 4h2v2H5V9zm0 4h2v2H5v-2z"/>
              </svg>
              <svg v-else class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zm14.553 1.106a1 1 0 00-1.414 0L12 10.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 000-1.414z"/>
              </svg>
              {{ getTypeText(library.collection_type) }}
            </span>
          </div>
          
          <!-- 标题 -->
          <h3 class="text-white font-bold text-lg md:text-xl drop-shadow-lg group-hover:text-primary-300 transition-colors">
            {{ library.name }}
          </h3>
          
          <!-- 数量 -->
          <p class="text-gray-300 text-sm mt-1">
            {{ library.item_count || 0 }} 部
          </p>
        </div>

        <!-- 悬停边框效果 -->
        <div class="absolute inset-0 rounded-2xl border-2 border-transparent group-hover:border-primary-500/50 transition-colors duration-300"></div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'
import { embyApi } from '../api'

const props = defineProps({
  libraries: {
    type: Array,
    default: () => []
  }
})

const appStore = useAppStore()
const loading = ref(true)
const libraryImages = ref({}) // { libraryId: [imageUrls] }

// 带图片的媒体库列表
const librariesWithImages = computed(() => {
  return props.libraries.map(lib => ({
    ...lib,
    images: libraryImages.value[lib.id] || []
  }))
})

// 获取每个媒体库的代表图片
const fetchLibraryImages = async () => {
  if (!appStore.currentEmbyUser || props.libraries.length === 0) {
    loading.value = false
    return
  }

  loading.value = true
  
  try {
    const promises = props.libraries.map(async (library) => {
      try {
        // 获取该媒体库最近添加的几个项目作为代表图片
        const result = await embyApi.getItems(appStore.currentEmbyUser.Id, {
          parent_id: library.id,
          sort_by: 'Random', // 随机获取
          limit: 4,
        })
        
        const images = result.items
          .filter(item => item.primary_image_tag)
          .map(item => appStore.getEmbyImageUrl(item.id, 'Primary', 400))
        
        return { id: library.id, images }
      } catch (e) {
        console.error(`Failed to fetch images for library ${library.id}:`, e)
        return { id: library.id, images: [] }
      }
    })

    const results = await Promise.all(promises)
    const imagesMap = {}
    results.forEach(r => {
      imagesMap[r.id] = r.images
    })
    libraryImages.value = imagesMap
  } catch (e) {
    console.error('Failed to fetch library images:', e)
  } finally {
    loading.value = false
  }
}

// 根据索引和总数决定卡片大小
const getCardSizeClass = (index, total) => {
  // 瀑布墙布局策略，模拟参考图的不规则布局
  if (total <= 4) {
    // 4个以下，全部大卡片
    return index === 0 ? 'card-featured' : 'card-large'
  }
  
  if (total <= 6) {
    // 5-6个分类
    if (index === 0) return 'card-featured'
    if (index < 3) return 'card-large'
    return 'card-medium'
  }
  
  if (total <= 9) {
    // 7-9个分类
    if (index === 0) return 'card-featured'
    if (index < 2) return 'card-large'
    if (index < 5) return 'card-medium'
    return 'card-small'
  }
  
  // 10个以上分类 - 更紧凑的布局
  if (index === 0) return 'card-featured'
  if (index < 2) return 'card-large'
  if (index < 6) return 'card-medium'
  return 'card-small'
}

const getSkeletonSizeClass = (index) => {
  if (index === 1) return 'card-featured'
  if (index <= 3) return 'card-large'
  if (index <= 7) return 'card-medium'
  return 'card-small'
}

const getTypeText = (type) => {
  const map = {
    'movies': '电影',
    'tvshows': '剧集',
    'music': '音乐',
    'musicvideos': '音乐视频',
    'homevideos': '家庭视频',
    'boxsets': '合集',
  }
  return map[type] || '媒体'
}

const getTypeTagClass = (type) => {
  if (type === 'movies') {
    return 'bg-purple-500/30 text-purple-200'
  }
  if (type === 'tvshows') {
    return 'bg-blue-500/30 text-blue-200'
  }
  return 'bg-gray-500/30 text-gray-200'
}

watch(() => props.libraries, () => {
  fetchLibraryImages()
}, { immediate: true })

watch(() => appStore.currentEmbyUser, () => {
  fetchLibraryImages()
})
</script>

<style scoped>
.category-wall {
  @apply w-full;
}

.category-wall-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 160px;
  gap: 1rem;
}

.category-card {
  @apply relative rounded-2xl overflow-hidden cursor-pointer;
  @apply transform transition-all duration-300;
  @apply hover:shadow-2xl hover:z-10;
}

.category-card:hover {
  transform: translateY(-4px) scale(1.02);
}

/* 特大卡片 - 占 2x2 */
.card-featured {
  grid-column: span 2;
  grid-row: span 2;
}

/* 大卡片 - 占 2x1 */
.card-large {
  grid-column: span 2;
  grid-row: span 1;
}

/* 中等卡片 - 占 1x1 */
.card-medium {
  grid-column: span 1;
  grid-row: span 1;
}

/* 小卡片 - 占 1x1 */
.card-small {
  grid-column: span 1;
  grid-row: span 1;
}

/* 响应式布局 */
@media (max-width: 1280px) {
  .category-wall-grid {
    grid-template-columns: repeat(4, 1fr);
    grid-auto-rows: 140px;
  }
}

@media (max-width: 1024px) {
  .category-wall-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 130px;
  }
  
  .card-featured {
    grid-column: span 2;
    grid-row: span 2;
  }
  
  .card-large {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .category-wall-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-auto-rows: 120px;
    gap: 0.75rem;
  }
  
  .card-featured {
    grid-column: span 2;
    grid-row: span 2;
  }
  
  .card-large {
    grid-column: span 2;
    grid-row: span 1;
  }
}

@media (max-width: 480px) {
  .category-wall-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-auto-rows: 100px;
    gap: 0.5rem;
  }
  
  .card-featured {
    grid-row: span 2;
  }
}
</style>
