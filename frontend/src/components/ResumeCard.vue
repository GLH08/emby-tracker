<template>
  <router-link 
    :to="detailLink"
    class="group block"
  >
    <div class="card overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
      <!-- 海报 -->
      <div class="relative aspect-[2/3] bg-gray-200 dark:bg-dark-100 overflow-hidden">
        <img 
          v-if="posterUrl"
          :src="posterUrl"
          :alt="displayTitle"
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
          <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
        </div>

        <!-- 观看进度 -->
        <div class="absolute bottom-0 left-0 right-0 h-1.5 bg-gray-800/50">
          <div 
            class="h-full bg-primary-500"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>

        <!-- 剧集标签 -->
        <div 
          v-if="item.type === 'Episode'"
          class="absolute top-2 left-2 px-2 py-1 bg-black/70 rounded-lg text-xs text-white"
        >
          S{{ item.parent_index_number || '?' }}E{{ item.index_number || '?' }}
        </div>
      </div>

      <!-- 信息 -->
      <div class="p-3">
        <h3 class="font-medium text-gray-900 dark:text-white truncate group-hover:text-primary-500 transition-colors">
          {{ displayTitle }}
        </h3>
        <p v-if="subtitle" class="text-sm text-gray-500 dark:text-gray-400 truncate mt-1">
          {{ subtitle }}
        </p>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
          {{ Math.round(progress) }}% 已观看
        </p>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

const appStore = useAppStore()

// 对于剧集，使用剧集的海报；对于电影，使用电影海报
const posterUrl = computed(() => {
  // 如果是剧集，优先使用剧集的海报
  if (props.item.type === 'Episode' && props.item.series_id) {
    return appStore.getEmbyImageUrl(props.item.series_id, 'Primary', 400)
  }
  return props.item.primary_image_tag 
    ? appStore.getEmbyImageUrl(props.item.id, 'Primary', 400)
    : ''
})

// 显示标题：剧集显示剧集名，电影显示电影名
const displayTitle = computed(() => {
  if (props.item.type === 'Episode' && props.item.series_name) {
    return props.item.series_name
  }
  return props.item.name
})

// 副标题：剧集显示集名
const subtitle = computed(() => {
  if (props.item.type === 'Episode') {
    return props.item.name
  }
  return ''
})

const progress = computed(() => {
  if (!props.item.runtime_ticks || !props.item.playback_position_ticks) return 0
  return (props.item.playback_position_ticks / props.item.runtime_ticks) * 100
})

const detailLink = computed(() => {
  if (props.item.type === 'Episode' && props.item.series_id) {
    return `/show/${props.item.series_id}`
  }
  if (props.item.type === 'Series') {
    return `/show/${props.item.id}`
  }
  return `/movie/${props.item.id}`
})
</script>
