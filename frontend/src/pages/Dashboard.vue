<template>
  <div class="page-heading"><div><span class="eyebrow">WORKSPACE OVERVIEW</span><h1>让流转，井然有序<span class="heading-dot">.</span></h1><p>{{ greeting }}，{{ session.user?.display_name || session.user?.username }}。{{ scopeText }}，从这里开始今天的工作。</p></div><div class="heading-actions"><el-button @click="load" :loading="loading"><Icon name="refresh" /> 刷新数据</el-button><el-button v-if="session.user?.role === 'employee'" type="primary" @click="router.push('/requests?new=1')"><Icon name="plus" /> 发起借用</el-button></div></div>
  <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" class="mb20" />
  <div class="hero-banner"><div><span class="banner-kicker">每一步，都能找到下一步</span><h2>{{ roleHeadline }}</h2><p>{{ roleSummary }}</p><el-button class="hero-button" @click="router.push('/requests')">{{ session.user?.role === 'employee' ? '查看我的借用' : '进入申请列表' }} <Icon name="arrow" /></el-button></div><div class="hero-visual" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="device-card"><Icon name="box" /><span>设备有去向</span><small>交接有记录</small><i><Icon name="check" /></i></div><div class="visual-tag"><span></span> 流转状态实时同步</div></div></div>
  <div class="metric-grid" v-loading="loading"><div v-for="metric in metricCards" :key="metric.key" class="metric-card"><div class="metric-top"><span>{{ metric.label }}</span><div class="metric-icon" :class="metric.tone"><Icon :name="metric.icon" /></div></div><div class="metric-number">{{ data.metrics?.[metric.key] ?? '—' }}<small>{{ metric.unit || '项' }}</small></div><p>{{ metric.note }}</p></div></div>
  <div class="dashboard-columns"><section class="panel recent-panel"><div class="panel-heading"><div><h3>最近的借用申请</h3><p>按当前账号可见范围展示</p></div><router-link to="/requests" class="text-link">查看全部 →</router-link></div><RequestTable :items="data.recent || []" /></section><section class="panel guide-panel"><span class="eyebrow">FLOW GUIDE</span><h3>一次完整的设备借用</h3><ol class="flow-guide"><li v-for="(step, index) in guide" :key="step.title"><span>{{ String(index + 1).padStart(2, '0') }}</span><div><strong>{{ step.title }}</strong><small>{{ step.text }}</small></div></li></ol><router-link to="/help" class="guide-link">了解操作与异常处理 <Icon name="arrow" /></router-link></section></div>
</template>
<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '../stores/session'
import { get } from '../api/client'
import Icon from '../ui/Icon.vue'
import RequestTable from '../ui/RequestTable.vue'
const session = useSession(), router = useRouter(), loading = ref(false), error = ref(''), data = ref({})
const greeting = new Date().getHours() < 12 ? '上午好' : '下午好'
const scopeText = computed(() => session.user?.role === 'employee' ? '关注你的借用进度' : session.user?.role === 'manager' ? '掌握本门店的设备需求' : '连接门店需求与设备资源')
const roleHeadline = computed(() => ({ employee: '需要的设备，从这里出发。', manager: '看清需求，让审批更有依据。', custodian: '设备交到谁手里，一目了然。', admin: '清晰的权限，是有序协作的开始。' }[session.user?.role]))
const roleSummary = computed(() => ({ employee: '申请、签收、归还，沿着一条清晰的时间线完成。', manager: '查看员工用途和借期，及时处理待办申请。', custodian: '分配空闲设备，登记交接，让每次归还得到确认。', admin: '管理门店与成员，查看设备流转和操作记录。' }[session.user?.role]))
const metricCards = [{ key: 'pending', label: '待处理事项', icon: 'clock', tone: 'amber', note: '当前角色需要推进的申请' }, { key: 'active', label: '正在借用', icon: 'box', tone: 'teal', note: '已签收、尚未完成归还' }, { key: 'overdue', label: '逾期未归还', icon: 'list', tone: 'red', note: '超过预计归还日期的借用' }, { key: 'avg_approval_hours', label: '平均审批耗时', icon: 'chart', tone: 'slate', unit: '小时', note: '从提交申请到审批决定' }]
const guide = [{ title: '说明需求', text: '员工选择设备类别与预计归还日期' }, { title: '审批与发放', text: '店长审批，管理员分配具体设备' }, { title: '签收与使用', text: '核对设备编号，确认实际收到' }, { title: '归还与验收', text: '检查设备状况，完成这次交接' }]
async function load() { loading.value = true; error.value = ''; try { data.value = await get('dashboard/') } catch (e) { error.value = e.userMessage } finally { loading.value = false } }
onMounted(load)
</script>
