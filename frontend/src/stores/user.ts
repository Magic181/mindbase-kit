import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type UserProfile } from '@/api/auth'
import { clearTokens, saveTokens } from '@/api/index'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const profile = ref<UserProfile | null>(null)
  const isLoggedIn = ref(!!token.value)

  function setAuth(access: string, refresh: string) {
    token.value = access
    isLoggedIn.value = true
    saveTokens(access, refresh)
  }

  async function fetchProfile() {
    const { data } = await authApi.me()
    profile.value = data
    return data
  }

  async function login(username: string, password: string) {
    const { data } = await authApi.login({ username, password })
    setAuth(data.access, data.refresh)
    await fetchProfile()
  }

  async function register(username: string, email: string, password: string) {
    const { data } = await authApi.register({ username, email, password })
    setAuth(data.access, data.refresh)
    await fetchProfile()
  }

  function logout() {
    token.value = ''
    profile.value = null
    isLoggedIn.value = false
    clearTokens()
  }

  return {
    token,
    profile,
    isLoggedIn,
    login,
    register,
    logout,
    fetchProfile,
    setAuth,
  }
})
