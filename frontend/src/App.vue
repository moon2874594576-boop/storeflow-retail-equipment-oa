<template><div v-if="initializing" class="boot-screen"><div class="brand-mark">S</div><p>正在恢复工作台…</p></div><router-view v-else /></template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSession } from './stores/session'
const session = useSession(), router = useRouter(), route = useRoute(), initializing = ref(true)
onMounted(async () => {
  if (session.token) { try { await session.restore(); if (route.path === '/login') router.replace('/') } catch { session.clear(); router.replace('/login') } }
  else if (route.path !== '/login') router.replace('/login')
  initializing.value = false
})
</script>
