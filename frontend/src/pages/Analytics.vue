<template>
  <div class="page-heading"><div><span class="eyebrow">OPERATIONS INSIGHTS</span><h1>数据洞察</h1><p>从真实流转记录出发，了解设备使用与处理效率。</p></div><div class="heading-actions"><el-button @click="load" :loading="loading"><Icon name="refresh" /> 刷新</el-button><el-button type="primary" @click="download" :loading="exporting"><Icon name="download" /> 导出明细</el-button></div></div><el-alert v-if="error" :title="error" type="error" show-icon :closable="false" class="mb20" />
  <div class="metric-grid" v-loading="loading"><div v-for="card in cards" :key="card.key" class="metric-card"><div class="metric-top"><span>{{ card.label }}</span><Icon :name="card.icon" /></div><div class="metric-number">{{ data.metrics?.[card.key] ?? '—' }}<small>{{ card.unit }}</small></div><p>{{ card.note }}</p></div></div>
  <div class="analytics-columns"><section class="panel"><div class="panel-heading"><div><h3>申请状态分布</h3><p>当前可见申请的实时状态</p></div><Icon name="chart" /></div><div class="distribution"><div v-for="entry in distribution" :key="entry.name" class="distribution-row"><div class="bar-label"><span>{{ entry.name }}</span><strong>{{ entry.value }}</strong></div><div class="bar-track"><div :style="{ width: `${entry.value / maxDistribution * 100}%` }"></div></div></div><el-empty v-if="!distribution.length" description="暂无申请数据" :image-size="70" /></div></section><section class="panel"><div class="panel-heading"><div><h3>近期申请趋势</h3><p>按申请创建日期统计</p></div><span class="chart-legend"><i></i> 申请数量</span></div><div v-if="(data.trend || []).length" class="trend-chart"><div class="chart-bars"><div v-for="entry in data.trend" :key="entry.date" class="chart-bar-col"><span>{{ entry.count }}</span><div :style="{ height: `${Math.max(3, entry.count / maxTrend * 145)}px` }"></div><small>{{ String(entry.date).slice(5) }}</small></div></div></div><el-empty v-else description="暂无趋势数据" :image-size="70" /></section></div>
  <section class="panel metric-definition"><div class="panel-heading"><h3>指标口径</h3><span class="muted">统计范围跟随账号权限</span></div><div class="definition-grid"><div><strong>正在借用</strong><p>已签收、尚未完成归还验收的申请。待验收设备继续保持占用。</p></div><div><strong>逾期未归还</strong><p>预计归还日期已过，状态仍为借用中或待归还验收；按北京时间自然日判断。</p></div><div><strong>平均审批耗时</strong><p>已作出审批决定的申请，从提交到决定的平均小时数，不包含仍待审批的申请。</p></div><div><strong>空闲设备</strong><p>当前可用于发放的设备。交接中、借用中、待验收及待维修设备不计入。</p></div></div></section>
</template>
<script setup>
import { computed, ref, onMounted } from 'vue'
import { get, exportRequests, report } from '../api/client'
import { requestStates } from '../utils/format'
import Icon from '../ui/Icon.vue'
const data = ref({}), loading = ref(false), exporting = ref(false), error = ref('')
const cards = [{ key: 'active', label: '正在借用', unit: '项', note: '仍在流转中的已签收借用', icon: 'box' }, { key: 'overdue', label: '逾期未归还', unit: '项', note: '需关注的超期设备', icon: 'clock' }, { key: 'inspection', label: '待归还验收', unit: '项', note: '等待管理员检查与确认', icon: 'shield' }, { key: 'avg_approval_hours', label: '平均审批耗时', unit: '小时', note: '已作出决定的申请', icon: 'chart' }]
const distribution = computed(() => (data.value.by_status || []).map(entry => ({ name: requestStates[entry.name] || entry.name, value: Number(entry.value) || 0 })))
const maxDistribution = computed(() => Math.max(1, ...distribution.value.map(entry => entry.value))), maxTrend = computed(() => Math.max(1, ...(data.value.trend || []).map(entry => entry.count)))
async function load() { loading.value = true; error.value = ''; try { data.value = await get('dashboard/') } catch (e) { error.value = e.userMessage } finally { loading.value = false } }
async function download() { exporting.value = true; try { await exportRequests() } catch (e) { report(e) } finally { exporting.value = false } }
onMounted(load)
</script>
