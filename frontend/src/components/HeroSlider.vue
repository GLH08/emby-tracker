<template>
  <div class="relative h-[500px] md:h-[600px] overflow-hidden bg-dark-400">
    <!-- 背景图 -->
    <transition name="fade" mode="out-in">
      <div 
        v-if="currentItem"
        :key="currentIndex"
        class="absolute inset-0"
      >
        <img 
          :src="backdropUrl"
          :alt="currentItem.name || currentItem.title"
          class="w-full h-full object-cover"
        />
        <div class="absolute inset-0 bg-gradient-to-r from-dark-400 via-dark-400/80 to-transparent"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-dark-400 via-transparent to-transparent"></div>
      </div>
    </transition>

    <!-- 内容 -->
    <div class="relative h-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center">
      <transition name="slide" mode="out-in">
        <div 
          v-if="currentItem"
          :key="currentIndex"
          class="max-w-2xl"
        >
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4">
            {{ currentItem.name || currentItem.title }}
          </h1>
          
          <div class="flex items-center space-x-4 mb-4">
            <span v-if="currentItem.year" class="text-gray-300">{{ currentItem.year }}</span>
            <span v-if="currentItem.community_rating" class="flex items-center space-x-1">
              <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span class="text-white font-medium">{{ currentItem.community_rating.toFixed(1) }}</span>
            </span>
            <span 
              v-if="currentItem.type === 'Series' || currentItem.media_type === 'Series'"
              class="badge badge-primary"
            >
              剧集
            </span>
          </div>

          <p class="text-gray-300 text-lg line-clamp-3 mb-6">
            {{ currentItem.overview || '暂无简介' }}
          </p>

          <div class="flex items-center space-x-4">
            <router-link 
              :to="detailLink"
              class="btn btn-primary px-8 py-3 text-lg"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>
              </svg>
              查看详情
            </router-link>
            <button 
              @click="toggleWatchlist"
              class="btn btn-secondary px-6 py-3"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              想看
            </button>
          </div>
        </div>
      </transition>
    </div>

    <!-- 指示器 -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center space-x-2">
      <button
        v-for="(item, index) in items"
        :key="item.id || item.emby_id"
        @click="currentIndex = index"
        class="w-2 h-2 rounded-full transition-all duration-300"
        :class="index === currentIndex ? 'w-8 bg-primary-500' : 'bg-white/50 hover:bg-white/80'"
      ></button>
    </div>

    <!-- 左右箭头 -->
    <button 
      @click="prev"
      class="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/30 hover:bg-black/50 flex items-center justify-center text-white transition-colors"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
    </button>
    <button 
      @click="next"
      class="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/30 hover:bg-black/50 flex items-center justify-center text-white transition-colors"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  isCustom: {
    type: Boolean,
    default: false,
  },
})

const appStore = useAppStore()
const currentIndex = ref(0)
let autoPlayTimer = null

const currentItem = computed(() => props.items[currentIndex.value])

const backdropUrl = computed(() => {
  if (!currentItem.value) return ''
  // 自定义轮播使用 backdrop_url 字段
  if (props.isCustom && currentItem.value.backdrop_url) {
    return currentItem.value.backdrop_url
  }
  // Emby 数据使用 Emby 图片 API
  return currentItem.value.backdrop_image_tag
    ? appStore.getEmbyImageUrl(currentItem.value.id || currentItem.value.emby_id, 'Backdrop', 1920)
    : appStore.getEmbyImageUrl(currentItem.value.id || currentItem.value.emby_id, 'Primary', 1920)
})

const detailLink = computed(() => {
  if (!currentItem.value) return '/'
  const itemType = props.isCustom ? currentItem.value.media_type : currentItem.value.type
  const itemId = props.isCustom ? currentItem.value.emby_id : currentItem.value.id
  const type = (itemType === 'Series' || itemType === 'series') ? 'show' : 'movie'
  return `/${type}/${itemId}`
})

const prev = () => {
  currentIndex.value = currentIndex.value === 0 
    ? props.items.length - 1 
    : currentIndex.value - 1
  resetAutoPlay()
}

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % props.items.length
  resetAutoPlay()
}

const toggleWatchlist = () => {
  // TODO: 实现想看功能
}

const startAutoPlay = () => {
  autoPlayTimer = setInterval(next, 6000)
}

const resetAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
  }
  startAutoPlay()
}

onMounted(() => {
  if (props.items.length > 1) {
    startAutoPlay()
  }
})

onUnmounted(() => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer)
  }
})
</script>
