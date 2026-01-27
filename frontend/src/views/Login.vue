<template>
  <div class="min-h-screen bg-background-100 dark:bg-dark-400 flex">
    <!-- 左侧品牌区域 -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-500 relative overflow-hidden">
      <!-- 装饰性背景图形 -->
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-20 left-20 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-20 right-20 w-80 h-80 bg-cta-500 rounded-full blur-3xl"></div>
      </div>

      <!-- 品牌内容 -->
      <div class="relative z-10 flex flex-col justify-center items-center w-full px-12">
        <div class="w-24 h-24 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center mb-8 shadow-xl">
          <svg class="w-14 h-14 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
          </svg>
        </div>
        <h1 class="text-5xl font-code font-bold text-white mb-4 tracking-tight">Emby Tracker</h1>
        <p class="text-xl text-white/80 font-sans text-center max-w-md">
          现代化媒体库管理与观影追踪平台
        </p>

        <!-- 特性列表 -->
        <div class="mt-16 space-y-4 text-white/90">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
            <span>智能观影统计与分析</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
            <span>多平台数据同步</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
            <span>个性化推荐系统</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8">
      <div class="w-full max-w-md">
        <!-- 移动端 Logo -->
        <div class="lg:hidden text-center mb-8">
          <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center mx-auto mb-4 shadow-lg">
            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-code font-semibold text-gradient">Emby Tracker</h1>
        </div>

        <!-- 登录卡片 -->
        <div class="card p-8 md:p-10">
          <div class="mb-8">
            <h2 class="text-3xl font-code font-semibold text-text-400 mb-2">
              {{ needInit ? '初始化账户' : '欢迎回来' }}
            </h2>
            <p class="text-text-600">
              {{ needInit ? '首次使用，请创建管理员账户' : '登录以继续使用 Emby Tracker' }}
            </p>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-text-400 mb-2">
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
              <label class="block text-sm font-medium text-text-400 mb-2">
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

            <div v-if="errorMsg" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 rounded-lg text-sm">
              <div class="flex items-center">
                <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                </svg>
                {{ errorMsg }}
              </div>
            </div>

            <button
              type="submit"
              class="w-full btn btn-primary py-3 text-base font-medium shadow-lg hover:shadow-xl transition-shadow"
              :disabled="loading"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ needInit ? '创建管理员' : '登录' }}
            </button>
          </form>

          <div v-if="needInit" class="mt-6 p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-primary-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-primary-700 dark:text-primary-300">
                首次使用需要初始化管理员账户。请使用环境变量中配置的用户名和密码。
              </p>
            </div>
          </div>
        </div>

        <!-- 页脚 -->
        <p class="mt-8 text-center text-sm text-text-600">
          &copy; 2026 Emby Tracker. All rights reserved.
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
      await authApi.initAdmin()
    }

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