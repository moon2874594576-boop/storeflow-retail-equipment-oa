import axios from 'axios'
import { ElMessage } from 'element-plus'
const client = axios.create({ baseURL: '/api/', timeout: 15000 })
client.interceptors.request.use(config => {
  const token = localStorage.getItem('storeflow_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
function errorText(data) {
  if (!data) return ''
  if (typeof data === 'string') return data.length < 200 ? data : ''
  if (data.detail || data.error || data.message) return data.detail || data.error || data.message
  return Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join('；') : String(v)}`).join('；')
}
client.interceptors.response.use(res => res, error => {
  error.userMessage = errorText(error.response?.data) || (error.code === 'ECONNABORTED' ? '请求超时，请确认服务状态后重试。' : '暂时无法连接服务，请检查本地服务是否启动。')
  if (error.response?.status === 401 && !error.config.url.includes('auth/login')) {
    localStorage.removeItem('storeflow_token'); localStorage.removeItem('storeflow_user')
    window.dispatchEvent(new Event('storeflow:expired'))
  }
  return Promise.reject(error)
})
export async function get(url, params) { return (await client.get(url, { params })).data }
export async function post(url, data = {}) { return (await client.post(url, data)).data }
export async function patch(url, data) { return (await client.patch(url, data)).data }
export function report(error) { ElMessage.error(error.userMessage || error.message || '操作未完成，请重试。') }
export function rows(data) { return Array.isArray(data) ? data : (data?.results || []) }
export async function exportRequests() {
  const response = await client.get('requests/export/', { responseType: 'blob' })
  const url = URL.createObjectURL(response.data), anchor = document.createElement('a')
  anchor.href = url; anchor.download = `StoreFlow-借用记录-${new Date().toISOString().slice(0, 10)}.csv`; anchor.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
