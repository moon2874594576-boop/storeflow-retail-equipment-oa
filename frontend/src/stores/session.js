import { defineStore } from 'pinia'
import { ref } from 'vue'
import { get, post } from '../api/client'
export const useSession = defineStore('session', () => {
  const token = ref(localStorage.getItem('storeflow_token') || ''), user = ref(null)
  function setUser(value) { user.value = value; localStorage.setItem('storeflow_user', JSON.stringify(value)) }
  async function login(credentials) { const result = await post('auth/login/', credentials); token.value = result.access; localStorage.setItem('storeflow_token', result.access); setUser(result.user) }
  async function restore() { setUser(await get('auth/me/')) }
  function clear() { token.value = ''; user.value = null; localStorage.removeItem('storeflow_token'); localStorage.removeItem('storeflow_user') }
  return { token, user, login, restore, clear }
})
