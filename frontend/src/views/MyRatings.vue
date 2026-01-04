<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">我的评分</h1>
      <div class="flex items-center space-x-4">
        <!-- 类型筛选 -->
        <select 
          v-model="filterType" 
          class="input py-2 px-3"
        >
          <option value="">全部类型</option>
          <option value="movie">电影</option>
          <option value="tv">剧集</option>
          <option value="episode">单集</option>
        </select>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="card p-4 text-center">
        <div class="text-3xl font-bold text-primary-500">{{ stats.total }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">总评分数</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-3xl font-bold text-yellow-500">{{ stats.average }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">平均分</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-3xl font-bold text-blue-500">{{ stats.by_type?.movie || 0 }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">电影</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-3xl font-bold text-purple-500">{{ stats.by_type?.tv || 0 }}</div>
        <div class="text-sm text-gray-500 dark:text-gray-400">剧集</div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="ratings.length === 0" class="text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
      </svg>
      <p class="text-gray-500 dark:text-gray-400">还没有评分记录</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">在影视详情页点击评分按钮开始评分</p>
    </div>

    <!-- 评分列表 -->
    <div v-else class="space-y-4">
      <div 
        v-for="rating in ratings" 
        :key="rating.id"
        class="card p-4 flex items-start space-x-4"
      >
        <!-- 评分数字 -->
        <div class="flex-shrink-0 w-14 h-14 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
          <span class="text-2xl font-bold text-white">{{ rating.rating }}</span>
        </div>

        <!-- 内容 -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2 mb-1">
            <h3 class="font-semibold text-gray-900 dark:text-white truncate">{{ rating.title }}</h3>
            <span class="badge" :class="getTypeBadgeClass(rating.media_type)">
              {{ getTypeLabel(rating.media_type) }}
            </span>
          </div>
          
          <!-- 评价内容 -->
          <p v-if="rating.review" class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
            {{ rating.review }}
          </p>
          
          <!-- 时间 -->
          <p class="text-xs text-gray-400 dark:text-gray-500">
            {{ formatDate(rating.rated_at) }}
          </p>
        </div>

        <!-- 操作按钮 -->
        <div class="flex-shrink-0 flex items-center space-x-2">
          <button 
            @click="editRating(rating)"
            class="p-2 text-gray-400 hover:text-primary-500 transition-colors"
            title="编辑"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
          </button>
          <button 
            @click="confirmDelete(rating)"
            class="p-2 text-gray-400 hover:text-red-500 transition-colors"
            title="删除"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > limit" class="flex justify-center mt-8">
        <div class="flex items-center space-x-2">
          <button 
            @click="page > 1 && (page--, fetchRatings())"
            :disabled="page === 1"
            class="btn btn-secondary px-3 py-2"
          >
            上一页
          </button>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {{ page }} / {{ Math.ceil(total / limit) }}
          </span>
          <button 
            @click="page < Math.ceil(total / limit) && (page++, fetchRatings())"
            :disabled="page >= Math.ceil(total / limit)"
            class="btn btn-secondary px-3 py-2"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showEditModal = false">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          编辑评分 - {{ editingRating?.title }}
        </h2>
        
        <!-- 星级评分 -->
        <div class="mb-6">
          <div class="flex items-center justify-center space-x-1 mb-2">
            <button
              v-for="star in 10"
              :key="star"
              @click="editRatingValue = star"
              class="p-1 transition-transform hover:scale-110"
            >
              <svg 
                class="w-8 h-8 transition-colors"
                :class="star <= editRatingValue ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'"
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </button>
          </div>
          <p class="text-center text-2xl font-bold text-gray-900 dark:text-white">
            {{ editRatingValue }} / 10
          </p>
        </div>
        
        <!-- 评论 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            评价内容
          </label>
          <textarea
            v-model="editReviewText"
            class="input w-full"
            rows="4"
            placeholder="分享你的观影感受..."
          ></textarea>
        </div>
        
        <!-- 按钮 -->
        <div class="flex justify-end space-x-3">
          <button 
            @click="showEditModal = false" 
            class="btn btn-secondary"
          >
            取消
          </button>
          <button 
            @click="saveEdit" 
            :disabled="saving"
            class="btn btn-primary"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showDeleteModal = false">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-sm mx-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">确认删除</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          确定要删除对「{{ deletingRating?.title }}」的评分吗？此操作不可撤销。
        </p>
        <div class="flex justify-end space-x-3">
          <button @click="showDeleteModal = false" class="btn btn-secondary">取消</button>
          <button @click="doDelete" :disabled="deleting" class="btn bg-red-500 text-white hover:bg-red-600">
            {{ deleting ? '删除中...' : '删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { ratingsApi } from '../api'

const appStore = useAppStore()

const loading = ref(false)
const ratings = ref([])
const stats = ref(null)
const total = ref(0)
const page = ref(1)
const limit = ref(20)
const filterType = ref('')

// 编辑相关
const showEditModal = ref(false)
const editingRating = ref(null)
const editRatingValue = ref(0)
const editReviewText = ref('')
const saving = ref(false)

// 删除相关
const showDeleteModal = ref(false)
const deletingRating = ref(null)
const deleting = ref(false)

const fetchRatings = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  try {
    const params = { page: page.value, limit: limit.value }
    if (filterType.value) params.media_type = filterType.value
    
    const result = await ratingsApi.getRatings(appStore.currentEmbyUser.Id, params)
    ratings.value = result.ratings
    total.value = result.total
  } catch (e) {
    console.error('Failed to fetch ratings:', e)
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  if (!appStore.currentEmbyUser) return
  
  try {
    stats.value = await ratingsApi.getStats(appStore.currentEmbyUser.Id)
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  }
}

const getTypeLabel = (type) => {
  const labels = { movie: '电影', tv: '剧集', episode: '单集' }
  return labels[type] || type
}

const getTypeBadgeClass = (type) => {
  const classes = {
    movie: 'badge-primary',
    tv: 'badge-success',
    episode: 'badge-warning'
  }
  return classes[type] || 'badge-secondary'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

const editRating = (rating) => {
  editingRating.value = rating
  editRatingValue.value = rating.rating
  editReviewText.value = rating.review || ''
  showEditModal.value = true
}

const saveEdit = async () => {
  if (!editingRating.value || !appStore.currentEmbyUser) return
  
  saving.value = true
  try {
    await ratingsApi.updateRating(editingRating.value.id, appStore.currentEmbyUser.Id, {
      rating: editRatingValue.value,
      review: editReviewText.value || null
    })
    
    // 更新本地数据
    const idx = ratings.value.findIndex(r => r.id === editingRating.value.id)
    if (idx !== -1) {
      ratings.value[idx].rating = editRatingValue.value
      ratings.value[idx].review = editReviewText.value
    }
    
    showEditModal.value = false
    fetchStats() // 刷新统计
  } catch (e) {
    console.error('Failed to update rating:', e)
    alert('更新失败')
  } finally {
    saving.value = false
  }
}

const confirmDelete = (rating) => {
  deletingRating.value = rating
  showDeleteModal.value = true
}

const doDelete = async () => {
  if (!deletingRating.value || !appStore.currentEmbyUser) return
  
  deleting.value = true
  try {
    await ratingsApi.deleteRating(deletingRating.value.id, appStore.currentEmbyUser.Id)
    ratings.value = ratings.value.filter(r => r.id !== deletingRating.value.id)
    total.value--
    showDeleteModal.value = false
    fetchStats() // 刷新统计
  } catch (e) {
    console.error('Failed to delete rating:', e)
    alert('删除失败')
  } finally {
    deleting.value = false
  }
}

watch(filterType, () => {
  page.value = 1
  fetchRatings()
})

watch(() => appStore.currentEmbyUser, () => {
  fetchRatings()
  fetchStats()
})

onMounted(() => {
  fetchRatings()
  fetchStats()
})
</script>
