<template>
  <div 
    v-if="showRating && rating" 
    class="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-xs font-medium"
    :class="badgeClass"
    :title="`IMDB: ${rating.toFixed(1)}`"
  >
    <span class="text-yellow-500">★</span>
    <span>{{ rating.toFixed(1) }}</span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps({
  imdbId: String,
  tmdbId: [Number, String],
  // 直接传入评分（如果已有）
  imdbRating: Number,
  // 样式变体
  variant: {
    type: String,
    default: 'default', // default, overlay, minimal
  },
})

const appStore = useAppStore()
const rating = ref(props.imdbRating || null)
const loading = ref(false)

// 是否显示评分（根据全局设置）
const showRating = computed(() => {
  return appStore.showExternalRatings && rating.value
})

// 徽章样式
const badgeClass = computed(() => {
  const base = {
    default: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300',
    overlay: 'bg-black/70 text-white backdrop-blur-sm',
    minimal: 'bg-transparent text-yellow-500',
  }
  return base[props.variant] || base.default
})

// 从缓存获取评分
const fetchRating = async () => {
  if (rating.value || loading.value) return
  if (!props.imdbId && !props.tmdbId) return
  if (!appStore.showExternalRatings) return
  
  // 从全局缓存获取
  const cached = appStore.getExternalRating(props.imdbId, props.tmdbId)
  if (cached) {
    rating.value = cached
  }
}

// 监听设置变化
watch(() => appStore.showExternalRatings, (newVal) => {
  if (newVal && !rating.value) {
    fetchRating()
  }
})

// 监听 props 变化
watch(() => props.imdbRating, (newVal) => {
  if (newVal) rating.value = newVal
})

onMounted(fetchRating)
</script>
