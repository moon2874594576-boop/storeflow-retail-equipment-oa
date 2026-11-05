import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getProfile } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const userInfo = ref(null)
  const permissions = ref([])

  async function login(loginForm) {
    const data = await loginApi(loginForm)
    token.value = data.access
    refreshToken.value = data.refresh
    userInfo.value = data.user
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    return data
  }

  async function fetchUserInfo() {
    const data = await getProfile()
    userInfo.value = data
    return data
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    permissions.value = []
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function isLoggedIn() {
    return !!token.value
  }

  return {
    token,
    refreshToken,
    userInfo,
    permissions,
    login,
    fetchUserInfo,
    logout,
    isLoggedIn
  }
})