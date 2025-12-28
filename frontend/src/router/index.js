import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/movies',
    name: 'Movies',
    component: () => import('../views/Movies.vue'),
  },
  {
    path: '/shows',
    name: 'Shows',
    component: () => import('../views/Shows.vue'),
  },
  {
    path: '/library/:id',
    name: 'Library',
    component: () => import('../views/Library.vue'),
  },
  {
    path: '/movie/:id',
    name: 'MovieDetail',
    component: () => import('../views/MediaDetail.vue'),
    props: route => ({ id: route.params.id, type: 'movie' }),
  },
  {
    path: '/show/:id',
    name: 'ShowDetail',
    component: () => import('../views/MediaDetail.vue'),
    props: route => ({ id: route.params.id, type: 'show' }),
  },
  {
    path: '/person/:id',
    name: 'Person',
    component: () => import('../views/Person.vue'),
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: () => import('../views/Watchlist.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('../views/Stats.vue'),
  },
  {
    path: '/discover',
    name: 'Discover',
    component: () => import('../views/Discover.vue'),
  },
  {
    path: '/tmdb/movie/:id',
    name: 'TmdbMovieDetail',
    component: () => import('../views/TmdbDetail.vue'),
    props: route => ({ id: route.params.id, type: 'movie' }),
  },
  {
    path: '/tmdb/tv/:id',
    name: 'TmdbTvDetail',
    component: () => import('../views/TmdbDetail.vue'),
    props: route => ({ id: route.params.id, type: 'tv' }),
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: () => import('../views/Calendar.vue'),
  },
  {
    path: '/progress',
    name: 'Progress',
    component: () => import('../views/Progress.vue'),
  },
  {
    path: '/lists',
    name: 'Lists',
    component: () => import('../views/Lists.vue'),
  },
  {
    path: '/list/:id',
    name: 'ListDetail',
    component: () => import('../views/ListDetail.vue'),
  },
  {
    path: '/yearly-review',
    name: 'YearlyReview',
    component: () => import('../views/YearlyReview.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isPublic = to.meta.public
  
  if (!isPublic && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
