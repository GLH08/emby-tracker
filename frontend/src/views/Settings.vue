<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-8">设置</h1>

    <div class="space-y-8">
      <!-- 账户信息 -->
      <section class="card p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">账户信息</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ appStore.currentSystemUser?.username }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ appStore.isAdmin ? '管理员' : '访客' }}
              </p>
            </div>
            <button @click="showChangePassword = true" class="btn btn-secondary">
              修改密码
            </button>
          </div>
        </div>
      </section>

      <!-- Emby 用户选择 -->
      <section class="card p-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Emby 用户</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">选择要查看的 Emby 用户媒体库</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            v-for="user in appStore.allowedEmbyUsers"
            :key="user.Id"
            @click="selectEmbyUser(user)"
            class="flex items-center space-x-3 p-4 rounded-xl border-2 transition-colors"
            :class="appStore.currentEmbyUser?.Id === user.Id 
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
              : 'border-gray-200 dark:border-dark-100 hover:border-gray-300 dark:hover:border-dark-200'"
          >
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-purple-400 flex items-center justify-center text-white font-medium">
              {{ user.Name?.charAt(0) }}
            </div>
            <div class="text-left">
              <p class="font-medium text-gray-900 dark:text-white">{{ user.Name }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ appStore.currentEmbyUser?.Id === user.Id ? '当前选中' : '点击切换' }}
              </p>
            </div>
          </button>
        </div>
      </section>

      <!-- 访客管理（仅管理员） -->
      <section v-if="appStore.isAdmin" class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">轮播海报管理</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">自定义首页轮播展示的影片</p>
          </div>
          <button @click="showAddHero = true" class="btn btn-primary">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            添加
          </button>
        </div>

        <div v-if="loadingHero" class="text-center py-8">
          <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
        </div>

        <div v-else-if="heroSlides.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          暂无自定义轮播，将使用最近添加的影片
        </div>

        <div v-else class="space-y-3">
          <div 
            v-for="(slide, index) in heroSlides"
            :key="slide.id"
            class="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-100 rounded-xl"
          >
            <div class="flex items-center space-x-4">
              <div class="flex flex-col space-y-1">
                <button 
                  @click="moveHeroSlide(index, -1)"
                  :disabled="index === 0"
                  class="p-1 rounded hover:bg-gray-200 dark:hover:bg-dark-200 disabled:opacity-30"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                  </svg>
                </button>
                <button 
                  @click="moveHeroSlide(index, 1)"
                  :disabled="index === heroSlides.length - 1"
                  class="p-1 rounded hover:bg-gray-200 dark:hover:bg-dark-200 disabled:opacity-30"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </button>
              </div>
              <img 
                v-if="slide.backdrop_url"
                :src="slide.backdrop_url"
                class="w-24 h-14 object-cover rounded"
              />
              <div>
                <p class="font-medium text-gray-900 dark:text-white">{{ slide.title }}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ slide.media_type === 'Series' ? '剧集' : '电影' }}
                  <span v-if="!slide.is_active" class="text-yellow-500 ml-2">（已禁用）</span>
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button 
                @click="toggleHeroActive(slide)" 
                class="btn-ghost p-2 rounded-lg"
                :class="slide.is_active ? 'text-green-500' : 'text-gray-400'"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path v-if="slide.is_active" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path v-if="slide.is_active" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
              <button @click="deleteHeroSlide(slide)" class="btn-ghost p-2 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 访客管理（仅管理员） -->
      <section v-if="appStore.isAdmin" class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">访客管理</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">管理访客账户及其权限</p>
          </div>
          <button @click="showCreateGuest = true" class="btn btn-primary">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            添加访客
          </button>
        </div>

        <div v-if="loadingGuests" class="text-center py-8">
          <div class="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
        </div>

        <div v-else-if="guests.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          暂无访客账户
        </div>

        <div v-else class="space-y-3">
          <div 
            v-for="guest in guests"
            :key="guest.id"
            class="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-100 rounded-xl"
          >
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ guest.username }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                可访问 {{ guest.allowed_emby_users?.length || 0 }} 个 Emby 用户
              </p>
            </div>
            <div class="flex items-center space-x-2">
              <button @click="editGuest(guest)" class="btn-ghost p-2 rounded-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button @click="deleteGuest(guest)" class="btn-ghost p-2 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 退出登录 -->
      <section class="card p-6">
        <button @click="handleLogout" class="btn btn-secondary w-full">
          退出登录
        </button>
      </section>
    </div>

    <!-- 修改密码弹窗 -->
    <div 
      v-if="showChangePassword"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="showChangePassword = false"
    >
      <div class="bg-white dark:bg-dark-200 rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">修改密码</h3>
        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">原密码</label>
            <input v-model="passwordForm.oldPassword" type="password" required class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">新密码</label>
            <input v-model="passwordForm.newPassword" type="password" required class="input" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">确认新密码</label>
            <input v-model="passwordForm.confirmPassword" type="password" required class="input" />
          </div>
          <div v-if="passwordError" class="text-red-500 text-sm">{{ passwordError }}</div>
          <div class="flex space-x-3">
            <button type="button" @click="showChangePassword = false" class="btn btn-secondary flex-1">取消</button>
            <button type="submit" class="btn btn-primary flex-1" :disabled="changingPassword">
              {{ changingPassword ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 创建/编辑访客弹窗 -->
    <div 
      v-if="showCreateGuest || editingGuest"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeGuestModal"
    >

    <!-- 添加轮播弹窗 -->
    <div 
      v-if="showAddHero"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="showAddHero = false; heroSearchQuery = ''; heroSearchResults = []"
    >
      <div class="bg-white dark:bg-dark-200 rounded-2xl shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden">
        <div class="p-6 border-b border-gray-100 dark:border-dark-100">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">添加轮播海报</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">搜索媒体库中的影片添加到轮播</p>
        </div>
        <div class="p-6">
          <div class="flex space-x-3 mb-4">
            <input 
              v-model="heroSearchQuery"
              type="text"
              placeholder="输入影片名称搜索..."
              class="input flex-1"
              @keyup.enter="searchHeroMedia"
            />
            <button @click="searchHeroMedia" class="btn btn-primary" :disabled="searchingHero">
              {{ searchingHero ? '搜索中...' : '搜索' }}
            </button>
          </div>
          
          <div class="max-h-96 overflow-y-auto space-y-2">
            <div 
              v-for="item in heroSearchResults"
              :key="item.id"
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-100 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-200 cursor-pointer"
              @click="addHeroSlide(item)"
            >
              <div class="flex items-center space-x-3">
                <img 
                  :src="appStore.getEmbyImageUrl(item.id, 'Primary', 100)"
                  class="w-12 h-16 object-cover rounded"
                />
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ item.name }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ item.type === 'Series' ? '剧集' : '电影' }}
                    <span v-if="item.year"> · {{ item.year }}</span>
                  </p>
                </div>
              </div>
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
            </div>
            
            <div v-if="heroSearchResults.length === 0 && heroSearchQuery && !searchingHero" class="text-center py-8 text-gray-500">
              未找到相关影片
            </div>
          </div>
        </div>
        <div class="p-6 border-t border-gray-100 dark:border-dark-100">
          <button 
            @click="showAddHero = false; heroSearchQuery = ''; heroSearchResults = []" 
            class="btn btn-secondary w-full"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
      <div class="bg-white dark:bg-dark-200 rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-100 dark:border-dark-100">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ editingGuest ? '编辑访客' : '添加访客' }}
          </h3>
        </div>
        <form @submit.prevent="handleSaveGuest" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">用户名</label>
            <input 
              v-model="guestForm.username" 
              type="text" 
              required 
              class="input"
              :disabled="!!editingGuest"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ editingGuest ? '新密码（留空不修改）' : '密码' }}
            </label>
            <input 
              v-model="guestForm.password" 
              type="password" 
              :required="!editingGuest"
              class="input" 
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">可访问的 Emby 用户</label>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <label 
                v-for="user in appStore.embyUsers"
                :key="user.Id"
                class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-dark-100 cursor-pointer"
              >
                <input 
                  type="checkbox"
                  :value="user.Id"
                  v-model="guestForm.allowedEmbyUsers"
                  class="w-4 h-4 text-primary-500 rounded"
                />
                <span class="text-gray-900 dark:text-white">{{ user.Name }}</span>
              </label>
            </div>
          </div>

          <div v-if="guestError" class="text-red-500 text-sm">{{ guestError }}</div>
          
          <div class="flex space-x-3 pt-4">
            <button type="button" @click="closeGuestModal" class="btn btn-secondary flex-1">取消</button>
            <button type="submit" class="btn btn-primary flex-1" :disabled="savingGuest">
              {{ savingGuest ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import { authApi, heroApi, embyApi } from '../api'

const router = useRouter()
const appStore = useAppStore()

// 访客列表
const guests = ref([])
const loadingGuests = ref(false)

// 轮播管理
const heroSlides = ref([])
const loadingHero = ref(false)
const showAddHero = ref(false)
const heroSearchQuery = ref('')
const heroSearchResults = ref([])
const searchingHero = ref(false)

// 修改密码
const showChangePassword = ref(false)
const changingPassword = ref(false)
const passwordError = ref('')
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// 访客管理
const showCreateGuest = ref(false)
const editingGuest = ref(null)
const savingGuest = ref(false)
const guestError = ref('')
const guestForm = reactive({
  username: '',
  password: '',
  allowedEmbyUsers: [],
})

const selectEmbyUser = (user) => {
  appStore.setCurrentEmbyUser(user)
}

const handleLogout = () => {
  appStore.logout()
  router.push('/login')
}

const handleChangePassword = async () => {
  passwordError.value = ''
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的密码不一致'
    return
  }
  
  changingPassword.value = true
  try {
    await authApi.changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    showChangePassword.value = false
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    alert('密码修改成功')
  } catch (e) {
    passwordError.value = e.response?.data?.detail || '修改失败'
  } finally {
    changingPassword.value = false
  }
}

const fetchGuests = async () => {
  if (!appStore.isAdmin) return
  loadingGuests.value = true
  try {
    guests.value = await authApi.getGuests()
  } catch (e) {
    console.error('Failed to fetch guests:', e)
  } finally {
    loadingGuests.value = false
  }
}

const editGuest = (guest) => {
  editingGuest.value = guest
  guestForm.username = guest.username
  guestForm.password = ''
  guestForm.allowedEmbyUsers = [...(guest.allowed_emby_users || [])]
}

const closeGuestModal = () => {
  showCreateGuest.value = false
  editingGuest.value = null
  guestForm.username = ''
  guestForm.password = ''
  guestForm.allowedEmbyUsers = []
  guestError.value = ''
}

const handleSaveGuest = async () => {
  guestError.value = ''
  savingGuest.value = true
  
  try {
    if (editingGuest.value) {
      await authApi.updateGuest(editingGuest.value.id, {
        password: guestForm.password || undefined,
        allowed_emby_users: guestForm.allowedEmbyUsers,
      })
    } else {
      await authApi.createGuest({
        username: guestForm.username,
        password: guestForm.password,
        allowed_emby_users: guestForm.allowedEmbyUsers,
      })
    }
    closeGuestModal()
    fetchGuests()
  } catch (e) {
    guestError.value = e.response?.data?.detail || '保存失败'
  } finally {
    savingGuest.value = false
  }
}

const deleteGuest = async (guest) => {
  if (!confirm(`确定要删除访客 "${guest.username}" 吗？`)) return
  
  try {
    await authApi.deleteGuest(guest.id)
    fetchGuests()
  } catch (e) {
    alert('删除失败')
  }
}

// 轮播管理方法
const fetchHeroSlides = async () => {
  loadingHero.value = true
  try {
    heroSlides.value = await heroApi.getSlides(false)
  } catch (e) {
    console.error('Failed to fetch hero slides:', e)
  } finally {
    loadingHero.value = false
  }
}

const searchHeroMedia = async () => {
  if (!heroSearchQuery.value.trim() || !appStore.currentEmbyUser) return
  
  searchingHero.value = true
  try {
    const result = await embyApi.getItems(appStore.currentEmbyUser.Id, {
      search_term: heroSearchQuery.value,
      limit: 20,
      include_item_types: 'Movie,Series',
    })
    heroSearchResults.value = result.items || []
  } catch (e) {
    console.error('Search failed:', e)
  } finally {
    searchingHero.value = false
  }
}

const addHeroSlide = async (item) => {
  try {
    await heroApi.createSlide({
      emby_id: item.id,
      title: item.name,
      overview: item.overview || '',
      backdrop_url: item.backdrop_image_tag 
        ? appStore.getEmbyImageUrl(item.id, 'Backdrop', 1920)
        : appStore.getEmbyImageUrl(item.id, 'Primary', 1920),
      media_type: item.type,
      sort_order: heroSlides.value.length,
    })
    showAddHero.value = false
    heroSearchQuery.value = ''
    heroSearchResults.value = []
    fetchHeroSlides()
  } catch (e) {
    alert(e.response?.data?.detail || '添加失败')
  }
}

const toggleHeroActive = async (slide) => {
  try {
    await heroApi.updateSlide(slide.id, { is_active: !slide.is_active })
    fetchHeroSlides()
  } catch (e) {
    alert('更新失败')
  }
}

const deleteHeroSlide = async (slide) => {
  if (!confirm(`确定要删除轮播 "${slide.title}" 吗？`)) return
  
  try {
    await heroApi.deleteSlide(slide.id)
    fetchHeroSlides()
  } catch (e) {
    alert('删除失败')
  }
}

const moveHeroSlide = async (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= heroSlides.value.length) return
  
  const slides = [...heroSlides.value]
  const temp = slides[index]
  slides[index] = slides[newIndex]
  slides[newIndex] = temp
  
  try {
    await heroApi.reorderSlides(slides.map(s => s.id))
    fetchHeroSlides()
  } catch (e) {
    alert('排序失败')
  }
}

onMounted(() => {
  fetchGuests()
  fetchHeroSlides()
})
</script>
