<template><div class="page-heading"><div><span class="eyebrow">YOUR ACCOUNT</span><h1>个人设置</h1><p>查看身份与权限，妥善维护工作账号。</p></div></div><div class="profile-grid"><section class="panel"><div class="panel-heading"><h3>当前账号</h3><Icon name="user" /></div><dl class="info-grid"><div><dt>显示名称</dt><dd>{{ session.user?.display_name || session.user?.username }}</dd></div><div><dt>工作账号</dt><dd>{{ session.user?.username }}</dd></div><div><dt>业务角色</dt><dd>{{ roleNames[session.user?.role] }}</dd></div><div><dt>所属门店</dt><dd>{{ session.user?.store_name || '总部' }}</dd></div></dl><p class="muted">角色和门店由系统管理员维护。修改账号信息不会改变已经产生的流转记录。</p></section><section class="panel"><div class="panel-heading"><h3>修改密码</h3><Icon name="shield" /></div><el-form ref="formRef" :model="form" :rules="rules" label-position="top"><el-form-item label="当前密码" prop="old_password"><el-input v-model="form.old_password" type="password" show-password autocomplete="current-password" /></el-form-item><el-form-item label="新密码" prop="new_password"><el-input v-model="form.new_password" type="password" show-password autocomplete="new-password" /></el-form-item><el-form-item label="确认新密码" prop="confirmation"><el-input v-model="form.confirmation" type="password" show-password autocomplete="new-password" /></el-form-item><el-button type="primary" :loading="saving" @click="save">更新密码</el-button></el-form></section></div></template>
<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useSession } from '../stores/session'
import { roleNames } from '../utils/format'
import { post, report } from '../api/client'
import Icon from '../ui/Icon.vue'
const session = useSession(), router = useRouter(), saving = ref(false), formRef = ref(), form = reactive({ old_password: '', new_password: '', confirmation: '' })
const rules = { old_password: [{ required: true, message: '请输入当前密码' }], new_password: [{ required: true, min: 8, message: '请使用至少8位新密码' }], confirmation: [{ validator: (_, value, callback) => value === form.new_password && value ? callback() : callback(new Error('两次输入的新密码不一致')) }] }
async function save() { if (saving.value || !await formRef.value.validate().catch(() => false)) return; saving.value = true; try { await post('auth/change_password/', { old_password: form.old_password, new_password: form.new_password }); session.clear(); ElMessage.success('密码已更新，请使用新密码登录。'); router.replace('/login') } catch (e) { report(e) } finally { saving.value = false } }
</script>
