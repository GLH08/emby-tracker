<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full"></div>
    </div>

    <template v-else-if="list">
      <!-- 列表头部 -->
      <div class="mb-8">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center space-x-3">
              <router-link to="/lists" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
              </router-link>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">{{ list.name }}</h1>
              <span v-if="list.is_public" class="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded">
                公开
              </span>
            </div>
            <p v-if="list.description" class="text-gray-500 dark:text-gray-400 mt-2">{{ list.description }}</p>
            <p class="text-sm text-gray-400 mt-2">{{ list.items.length }} 个项目</p>
          </div>
          
          <!-- 操作按钮 -->
          <div v-if="list.is_owner" class="flex items-center space-x-2">
            <button @click="showEditModal = true" class="btn-secondary">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              编辑
            </button>
            <button @click="confirmDelete" class="btn-secondary text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="list.items.length === 0" class="text-center py-20">
        <svg class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
        </svg>
        <p class="text-gray-500 dark:text-gray-400">列表还是空的</p>
        <p class="text-sm text-gray-400 mt-2">在电影或剧集详情页添加到此列表</p>
      </div>

      <!-- 列表项 -->
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <div
          v-for="item in list.items"
          :key="item.id"
          class="group relative"
        >
          <router-link :to="`/tmdb/${item.media_type}/${item.tmdb_id}`">
            <div class="aspect-[2/3] rounded-xl overflow-hidden bg-gray-100 dark:bg-dark-100">
              <img
                v-if="item.poster_path"
                :src="`${appStore.tmdbImageBaseUrl}/w342${item.poster_path}`"
                :alt="item.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
                </svg>
              </div>
            </div>
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white truncate">{{ item.title }}</h3>
            <p class="text-xs text-gray-500">{{ item.year }} · {{ item.media_type === 'movie' ? '电影' : '剧集' }}</p>
          </router-link>
          
          <!-- 删除按钮 -->
          <button
            v-if="list.is_owner"
            @click="removeItem(item.id)"
            class="absolute top-2 right-2 w-8 h-8 bg-black/60 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-white hover:bg-red-500"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </template>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showEditModal = false">
      <div class="bg-white dark:bg-dark-200 rounded-2xl p-6 w-full max-w-md mx-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">编辑列表</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">列表名称</label>
            <input v-model="editForm.name" type="text" class="input w-full" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">描述</label>
            <textarea v-model="editForm.description" class="input w-full" rows="3"></textarea>
          </div>
          
          <div class="flex items-center">
            <input v-model="editForm.is_public" type="checkbox" id="edit_is_public" class="mr-2" />
            <label for="edit_is_public" class="text-sm text-gray-700 dark:text-gray-300">公开列表</label>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button @click="showEditModal = false" class="btn-secondary">取消</button>
          <button @click="updateList" class="btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { listsApi } from '../api'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const loading = ref(true)
const list = ref(null)
const showEditModal = ref(false)
const editForm = ref({
  name: '',
  description: '',
  is_public: false,
})

const fetchList = async () => {
  if (!appStore.currentEmbyUser) return
  
  loading.value = true
  try {
    const result = await listsApi.getList(route.params.id, appStore.currentEmbyUser.Id)
    list.value = result
    editForm.value = {
      name: result.name,
      description: result.description || '',
      is_public: result.is_public,
    }
  } catch (e) {
    console.error('获取列表失败:', e)
  } finally {
    loading.value = false
  }
}

const updateList = async () => {
  if (!appStore.currentEmbyUser) return
  
  try {
    await listsApi.updateList(route.params.id, appStore.currentEmbyUser.Id, editForm.value)
    showEditModal.value = false
    await fetchList()
  } catch (e) {
    console.error('更新列表失败:', e)
  }
}

const confirmDelete = async () => {
  if (!confirm('确定要删除这个列表吗？此操作不可撤销。')) return
  
  try {
    await listsApi.deleteList(route.params.id, appStore.currentEmbyUser.Id)
    router.push('/lists')
  } catch (e) {
    console.error('删除列表失败:', e)
  }
}

const removeItem = async (itemId) => {
  if (!appStore.currentEmbyUser) return
  
  try {
    await listsApi.removeItem(route.params.id, itemId, appStore.currentEmbyUser.Id)
    await fetchList()
  } catch (e) {
    console.error('移除项目失败:', e)
  }
}

onMounted(fetchList)
</script>
