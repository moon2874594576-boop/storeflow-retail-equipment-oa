<template>
  <div class="app-shell">
    <div v-if="mobileOpen" class="sidebar-shade" @click="mobileOpen = false"></div>
    <aside class="sidebar" :class="{ open: mobileOpen }">
      <router-link to="/" class="brand"><span class="brand-mark">S</span><span>StoreFlow<small>门店设备流转工作台</small></span></router-link>
      <div class="workspace-label">OPERATIONS / 运营空间</div>
      <nav aria-label="主导航"><router-link v-for="item in nav" :key="item.to" :to="item.to" :class="{ selected: selected(item.to) }" @click="mobileOpen = false"><Icon :name="item.icon" /><span>{{ item.label }}</span><span v-if="item.to === '/'" class="nav-dot"></span></router-link></nav>
      <div class="sidebar-bottom"><div class="scope-note"><Icon name="shield" /><div>每一次交接，都有记录<small>权限按角色与门店生效</small></div></div><router-link to="/help" class="sidebar-guide">需要帮助？查看操作指南 <span>↗</span></router-link><div class="version">STOREFLOW · 1.0</div></div>
    </aside>
    <div class="main-area">
      <header class="topbar"><div class="topbar-left"><button class="icon-button mobile-menu" aria-label="展开导航" @click="mobileOpen = !mobileOpen"><Icon name="menu" /></button><span class="breadcrumb">运营空间 <span>/</span> <strong>{{ route.meta.title }}</strong></span></div><div class="topbar-right"><span class="environment" v-if="demoMode"><i></i> 本地演示环境</span><span class="topbar-divider"></span><router-link to="/profile" class="user-chip"><span class="avatar">{{ (session.user?.display_name || session.user?.username || 'S').slice(0, 1) }}</span><span>{{ session.user?.display_name || session.user?.username }}<small>{{ roleNames[session.user?.role] }}</small></span></router-link><button class="icon-button" title="退出登录" aria-label="退出登录" @click="logout"><Icon name="logout" /></button></div></header>
      <main class="page-content"><router-view /></main>
      <footer class="site-footer"><span>StoreFlow · 让设备流转清晰有序</span><span>数据按当前账号权限展示 · 北京时间</span></footer>
    </div>
  </div>
</template>
<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useSession } from '../stores/session'
import { roleNames } from '../utils/format'
import { get } from '../api/client'
import Icon from '../ui/Icon.vue'
const session = useSession(), route = useRoute(), router = useRouter(), mobileOpen = ref(false), demoMode = ref(false)
const nav = computed(() => {
  const role = session.user?.role, entries = [{ to: '/', label: '工作台', icon: 'grid' }, { to: '/requests', label: role === 'employee' ? '我的借用' : '借用申请', icon: 'list' }]
  if (['admin', 'custodian'].includes(role)) entries.push({ to: '/assets', label: '设备台账', icon: 'box' })
  entries.push({ to: '/analytics', label: '数据洞察', icon: 'chart' })
  if (['admin', 'custodian'].includes(role)) entries.push({ to: '/audit', label: '流转审计', icon: 'shield' })
  if (role === 'admin') entries.push({ to: '/settings', label: '系统管理', icon: 'settings' })
  entries.push({ to: '/help', label: '使用指南', icon: 'help' }); return entries
})
function selected(to) { return to === '/' ? route.path === '/' : route.path.startsWith(to) }
function logout() { session.clear(); router.replace('/login') }
function expired() { logout(); ElMessage.warning('登录已失效，请重新登录。') }
onMounted(async () => { window.addEventListener('storeflow:expired', expired); try { demoMode.value = !!(await get('health/')).demo_mode } catch {} })
onUnmounted(() => window.removeEventListener('storeflow:expired', expired))
</script>
