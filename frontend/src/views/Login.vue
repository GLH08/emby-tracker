<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-purple-600 px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center mx-auto mb-4">
          <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-white">Emby Tracker</h1>
        <p class="text-white/70 mt-2">媒体库管理与观影追踪</p>
      </div>

      <!-- 登录表单 -->
      <div class="bg-white dark:bg-dark-200 rounded-2xl shadow-xl p-8">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          {{ needInit ? '初始化管理员' : '登录' }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              用户名
            </label>
            <input 
              v-model="username"
              type="text"
              required
              class="input"
              placeholder="请输入用户名"
              :disabled="loading"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              密码
            </label>
            <input 
              v-model="password"
              type="password"
              required
              class="input"
              placeholder="请输入密码"
              :disabled="loading"
            />
          </div>

          <div v-if="errorMsg" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
            {{ errorMsg }}
          </div>

          <button 
            type="submit"
            class="w-full btn btn-primary py-3 text-lg"
            :disabled="loading"
          >
            <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ needInit ? '创建管理员' : '登录' }}
          </button>
        </form>

        <p v-if="needInit" class="mt-4 text-sm text-gray-500 dark:text-gray-400 text-center">
          首次使用，请使用环境变量中配置的管理员账户登录
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { authApi } from '../api'

const router = useRouter()
const appStore = useAppStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')
const needInit = ref(false)

const checkInit = async () => {
  try {
    const result = await authApi.checkInit()
    needInit.value = !result.initialized
  } catch (e) {
    console.error('Failed to check init:', e)
  }
}

const handleSubmit = async () => {
  if (!username.value || !password.value) return
  
  loading.value = true
  errorMsg.value = ''
  
  try {
    if (needInit.value) {
      // 初始化管理员
      await authApi.initAdmin()
    }
    
    // 登录
    await appStore.login(username.value, password.value)
    await appStore.init()
    router.push('/')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

onMounted(checkInit)
</script>
