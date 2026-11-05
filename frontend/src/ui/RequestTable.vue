<template><el-table :data="items" class="business-table" @row-click="open" empty-text="暂无符合条件的申请" row-class-name="clickable-row">
  <el-table-column label="申请单 / 设备需求" min-width="205"><template #default="{ row }"><div class="cell-title">{{ row.number }}</div><div class="cell-sub">{{ row.category_name }}<span v-if="row.asset_code"> · {{ row.asset_code }}</span></div></template></el-table-column>
  <el-table-column label="申请人 / 门店" min-width="155"><template #default="{ row }"><div>{{ row.applicant_name }}</div><div class="cell-sub">{{ row.store_name }}</div></template></el-table-column>
  <el-table-column label="处理进度" min-width="155"><template #default="{ row }"><StatusPill :status="row.status" /><span v-if="row.overdue" class="overdue-small">已逾期</span></template></el-table-column>
  <el-table-column label="预计归还" min-width="120"><template #default="{ row }"><span :class="{ 'danger-text': row.overdue }">{{ day(row.due_date) }}</span></template></el-table-column>
  <el-table-column label="" width="88" align="right" fixed="right"><template #default="{ row }"><el-button link type="primary" @click.stop="open(row)">查看 →</el-button></template></el-table-column>
</el-table></template>
<script setup>
import { useRouter } from 'vue-router'
import { day } from '../utils/format'
import StatusPill from './StatusPill.vue'
defineProps({ items: { type: Array, default: () => [] } })
const router = useRouter()
function open(row) { router.push(`/requests/${row.id}`) }
</script>
