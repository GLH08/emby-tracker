<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">我的列表</h1>
      <button @click="showCreateModal = true" class="btn-primary">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        创建列表
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="lists.length === 0" class="text-center py-20">
      <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
      </svg>
      <p class="text-gray-500 dark:text-gray-400 mb-4">还没有创建任何列表</p>
      <button @click="showCreateModal = true" class="btn-primary">创建第一个列表</button>
    </div>

    <!-- 列表网格 -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <router-link
        v-for="list in lists"
        :key="list.id"
        :to="`/list/${list.id}`"
        class="card overflow-hidden hover:shadow-lg transition-shadow group"
      >
        <!-- 封面 -->
        <div class="aspect-video bg-gradient-to-br from-primary-500 to-purple-600 relative">
          <img
            v-if="list.cover_image"
            :src="list.cover_image"
            :alt="list.name"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center">
            <svg class="w-12 h-12 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
          </div>
          <!-- 公开标记 -->
          <div v-if="list.is_public" class="absolute top-2 right-2 px-2 py-0.5 bg-green-500 text-white text-xs rounded">
            公开
          </div>
        </div>
        
        <!-- 信息 -->
        <div class="p-4">
          <h3 class="font-semibold text-gray-900 dark:text-white group-hover:text-primary-500 transition-colors">
            {{ list.name }}
          </h3>
          <p v-if="list.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
            {{ list.description }}
          </p>
          <div class="flex items-center justify-between mt-3 text-sm text-gray-400">
            <span>{{ list.item_count }} 个项目</span>
            <span>{{ formatDate(list.created_at) }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <!-- 创建列表弹窗 -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showCreateModal = false">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">创建新列表</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">列表名称</label>
            <input v-model="newList.name" type="text" class="input w-full" placeholder="例如：2024年必看电影" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">描述（可选）</label>
            <textarea v-model="newList.description" class="input w-full" rows="3" placeholder="简单描述这个列表..."></textarea>
          </div>
          
          <div class="flex items-center">
            <input v-model="newList.is_public" type="checkbox" id="is_public" class="mr-2" />
            <label for="is_public" class="text-sm text-gray-700 dark:text-gray-300">公开列表（可通过链接分享）</label>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button @click="showCreateModal = false" class="btn-secondary">取消</button>
          <button @click="createList" :disabled="!newList.name" class="btn-primary">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { listsApi } from '../api'

const appStore = useAppStore()
const loading = ref(true)
const lists = ref([])
const showCreateModal = ref(false)
const newList = ref({
  name: '',
  description: '',
  is_public: false,
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const fetchLists = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  try {
    const result = await listsApi.getLists(appStore.currentEmbyUser.Id)
    lists.value = result.lists || []
  } catch (e) {
    console.error('获取列表失败:', e)
  } finally {
    loading.value = false
  }
}

const createList = async () => {
  if (!newList.value.name || !appStore.currentEmbyUser) return
  
  try {
    await listsApi.createList(appStore.currentEmbyUser.Id, newList.value)
    showCreateModal.value = false
    newList.value = { name: '', description: '', is_public: false }
    await fetchLists()
  } catch (e) {
    console.error('创建列表失败:', e)
  }
}

onMounted(fetchLists)
</script>
