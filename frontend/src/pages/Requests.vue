<template>
  <div class="page-heading"><div><span class="eyebrow">DEVICE REQUESTS</span><h1>{{ session.user?.role === 'employee' ? '我的借用' : '借用申请' }}</h1><p>需求、进度与交接记录，集中在一张申请单。</p></div><div class="heading-actions"><el-button @click="download" :loading="exporting"><Icon name="download" /> 导出记录</el-button><el-button v-if="session.user?.role === 'employee'" type="primary" @click="openCreate"><Icon name="plus" /> 发起借用</el-button></div></div>
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" class="mb20" />
  <section class="panel"><div class="filter-bar"><el-input v-model="filters.q" placeholder="搜索单号、用途或申请人" clearable class="search-input" @keyup.enter="search"><template #prefix><Icon name="search" /></template></el-input><el-select v-model="filters.status" placeholder="全部状态" clearable @change="search"><el-option v-for="(label, value) in requestStates" :key="value" :label="label" :value="value" /></el-select><el-button @click="search">查询</el-button><el-button link @click="reset">重置</el-button><span class="result-count">共 {{ count }} 条记录</span></div><div v-loading="loading"><RequestTable :items="items" /></div><div class="pagination"><el-pagination :current-page="page" :page-size="20" :total="count" layout="total, prev, pager, next" @current-change="value => { page = value; load() }" /></div></section>
  <div class="context-note"><Icon name="shield" /> {{ session.user?.role === 'employee' ? '仅展示你本人发起的申请。' : session.user?.role === 'manager' ? '仅展示当前门店的申请，其他门店的数据由后端隔离。' : '所有流转操作均保留操作者与处理时间。' }}</div>
  <el-dialog v-model="creating" title="发起设备借用" width="520px" :close-on-click-modal="false"><p class="dialog-intro">每张申请借用一台设备。审批通过后，由设备管理员分配具体设备。</p><el-form ref="formRef" :model="form" :rules="rules" label-position="top"><el-form-item label="设备类别" prop="category_id"><el-select v-model="form.category_id" placeholder="请选择设备类别" class="full-width"><el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" /></el-select></el-form-item><el-form-item label="业务用途" prop="purpose"><el-input v-model="form.purpose" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="例如：周末盘点需要使用扫码枪，预计借用7天。" /></el-form-item><el-form-item label="预计归还日期" prop="due_date"><el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" class="full-width" :disabled-date="date => date < new Date(new Date().setHours(0, 0, 0, 0))" /></el-form-item></el-form><template #footer><el-button @click="creating = false">取消</el-button><el-button :loading="saving" @click="save(false)">保存草稿</el-button><el-button type="primary" :loading="saving" @click="save(true)">保存并提交</el-button></template></el-dialog>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useSession } from '../stores/session'
import { get, post, rows, report, exportRequests } from '../api/client'
import { requestStates, nextWeek } from '../utils/format'
import Icon from '../ui/Icon.vue'
import RequestTable from '../ui/RequestTable.vue'
const session = useSession(), route = useRoute(), router = useRouter(), items = ref([]), count = ref(0), page = ref(1), loading = ref(false), error = ref(''), creating = ref(false), saving = ref(false), exporting = ref(false), categories = ref([]), formRef = ref()
const filters = reactive({ q: '', status: '' }), form = reactive({ category_id: null, purpose: '', due_date: nextWeek() })
const rules = { category_id: [{ required: true, message: '请选择设备类别', trigger: 'change' }], purpose: [{ required: true, whitespace: true, message: '请填写具体业务用途', trigger: 'blur' }], due_date: [{ required: true, message: '请选择预计归还日期', trigger: 'change' }] }
async function load() { loading.value = true; error.value = ''; try { const data = await get('requests/', { ...filters, page: page.value }); items.value = rows(data); count.value = data.count ?? items.value.length } catch (e) { error.value = e.userMessage } finally { loading.value = false } }
function search() { page.value = 1; load() }
function reset() { filters.q = ''; filters.status = ''; search() }
async function openCreate() { form.category_id = null; form.purpose = ''; form.due_date = nextWeek(); creating.value = true; try { categories.value = rows(await get('categories/')) } catch (e) { report(e) } }
async function save(submit) {
  if (saving.value || !await formRef.value.validate().catch(() => false)) return
  saving.value = true
  try { const request = await post('requests/', form); creating.value = false; if (submit) { try { await post(`requests/${request.id}/submit/`) } catch (e) { ElMessage.warning(`草稿已保存，提交未成功：${e.userMessage}`); router.push(`/requests/${request.id}`); return } } ElMessage.success(submit ? '申请已提交，等待店长审批。' : '草稿已保存。'); router.push(`/requests/${request.id}`) } catch (e) { report(e) } finally { saving.value = false }
}
async function download() { exporting.value = true; try { await exportRequests() } catch (e) { report(e) } finally { exporting.value = false } }
onMounted(() => { if (route.query.status) filters.status = String(route.query.status); load(); if (route.query.new && session.user?.role === 'employee') openCreate() })
</script>
