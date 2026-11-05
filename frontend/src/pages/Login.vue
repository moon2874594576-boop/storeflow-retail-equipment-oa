<template>
  <div class="login-page"><section class="login-story"><a class="brand" href="/login"><span class="brand-mark">S</span><span>StoreFlow<small>门店设备流转工作台</small></span></a><div class="story-main"><span class="eyebrow light">LESS WAITING. BETTER FLOW.</span><h1>让每一台设备，<br>去向清晰。</h1><p>从一张借用申请，到一次安心归还。<br>连接门店与设备管理，让协作有序发生。</p><div class="flow-illustration"><div><Icon name="list" /><span>申请</span><small>说明业务需要</small></div><b>→</b><div><Icon name="check" /><span>审批</span><small>确认与分配</small></div><b>→</b><div><Icon name="box" /><span>交接</span><small>签收与归还</small></div></div><div class="story-stamp"><span class="stamp-dot"></span> 每一次流转，都可追溯</div></div><div class="story-footer">一个面向零售门店的轻量设备借用系统</div></section>
    <section class="login-form-area"><div class="login-card"><span class="eyebrow">WELCOME TO YOUR WORKSPACE</span><h2>欢迎回来</h2><p class="muted">使用你的工作账号，进入设备流转工作台。</p><el-alert v-if="error" :title="error" type="error" show-icon :closable="false" class="mb20" /><el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="login"><el-form-item label="工作账号" prop="username"><el-input v-model="form.username" placeholder="请输入账号" size="large" autocomplete="username" /></el-form-item><el-form-item label="登录密码" prop="password"><el-input v-model="form.password" type="password" show-password placeholder="请输入密码" size="large" autocomplete="current-password" @keyup.enter="login" /></el-form-item><el-button type="primary" size="large" class="full-width login-submit" :loading="loading" @click="login">进入工作台 <Icon name="arrow" /></el-button></el-form><p class="login-tip"><Icon name="shield" /> 账号权限由管理员配置，操作将保留流转记录。</p><div v-if="demoMode" class="demo-accounts"><div class="section-mini">演示角色 <span>点击填入账号</span></div><div class="demo-grid"><button v-for="account in demoAccounts" :key="account.username" @click="form.username = account.username"><strong>{{ account.label }}</strong><small>{{ account.username }}</small></button></div><p>演示密码见 README；如已修改，请使用实际配置。全部门店与设备均为模拟数据。</p></div><div class="login-copyright">StoreFlow / 门店设备借用与归还</div></div></section></div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '../stores/session'
import { get } from '../api/client'
import Icon from '../ui/Icon.vue'
const router = useRouter(), session = useSession(), formRef = ref(), loading = ref(false), error = ref(''), demoMode = ref(false)
const form = reactive({ username: '', password: '' }), rules = { username: [{ required: true, message: '请输入工作账号', trigger: 'blur' }], password: [{ required: true, message: '请输入登录密码', trigger: 'blur' }] }
const demoAccounts = [{ username: 'employee_a', label: '门店员工' }, { username: 'manager_a', label: '门店店长' }, { username: 'custodian', label: '设备管理员' }, { username: 'admin', label: '系统管理员' }]
async function login() {
  if (loading.value || !await formRef.value.validate().catch(() => false)) return
  loading.value = true; error.value = ''
  try { await session.login(form); await router.replace('/') } catch (e) { error.value = e.userMessage || '登录失败，请核对账号和密码。' } finally { loading.value = false }
}
onMounted(async () => { try { demoMode.value = !!(await get('health/')).demo_mode } catch { error.value = '服务暂时未就绪。请确认项目已启动，再刷新页面。' } })
</script>
