import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

// 发布新版本后，已打开页面可能还持有旧的分块地址；只自动恢复一次，避免刷新循环。
function recoverUpdatedAssets() {
  const lastAttempt = Number(sessionStorage.getItem('storeflow_asset_reload') || 0)
  if (Date.now() - lastAttempt > 30000) {
    sessionStorage.setItem('storeflow_asset_reload', String(Date.now()))
    window.location.reload()
  } else {
    ElMessage.error({ message: '应用资源加载未完成，请确认服务运行后刷新页面。', duration: 0, showClose: true })
  }
}
window.addEventListener('vite:preloadError', event => { event.preventDefault(); recoverUpdatedAssets() })
const router = createRouter({ history: createWebHistory(), scrollBehavior: (to, from, saved) => saved || { left: 0, top: 0 }, routes: [
  { path: '/login', component: () => import('../pages/Login.vue'), meta: { title: '登录' } },
  { path: '/', component: () => import('../pages/Shell.vue'), children: [
    { path: '', component: () => import('../pages/Dashboard.vue'), meta: { title: '工作台' } },
    { path: 'requests', component: () => import('../pages/Requests.vue'), meta: { title: '借用申请' } },
    { path: 'requests/:id', component: () => import('../pages/RequestDetail.vue'), meta: { title: '申请详情' } },
    { path: 'assets', component: () => import('../pages/Assets.vue'), meta: { title: '设备台账', roles: ['admin', 'custodian'] } },
    { path: 'analytics', component: () => import('../pages/Analytics.vue'), meta: { title: '数据洞察' } },
    { path: 'audit', component: () => import('../pages/Audit.vue'), meta: { title: '流转审计', roles: ['admin', 'custodian'] } },
    { path: 'settings', component: () => import('../pages/Settings.vue'), meta: { title: '系统管理', roles: ['admin'] } },
    { path: 'help', component: () => import('../pages/Help.vue'), meta: { title: '使用指南' } },
    { path: 'profile', component: () => import('../pages/Profile.vue'), meta: { title: '个人设置' } },
    { path: ':pathMatch(.*)*', component: () => import('../pages/NotFound.vue'), meta: { title: '页面不存在' } },
  ] },
] })
router.beforeEach(to => {
  document.title = `${to.meta.title || '工作台'} · StoreFlow 门店设备流转`
  if (to.path !== '/login' && !localStorage.getItem('storeflow_token')) return '/login'
  let user; try { user = JSON.parse(localStorage.getItem('storeflow_user') || 'null') } catch { user = null }
  if (to.meta.roles && user && !to.meta.roles.includes(user.role)) return '/'
})
router.onError(error => {
  if (/Failed to fetch dynamically imported module|Importing a module script failed|Loading chunk|Unable to preload CSS/.test(error.message)) recoverUpdatedAssets()
})
export default router
