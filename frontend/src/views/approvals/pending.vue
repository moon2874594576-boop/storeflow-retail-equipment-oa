<template>
  <div class="approval-pending">
    <div class="page-header">
      <h2>待我审批</h2>
    </div>

    <div class="table-container">
      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="审批标题" min-width="200" />
        <el-table-column prop="type_name" label="审批类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.type_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applicant_name" label="申请人" width="120" />
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
            <el-button type="success" link @click="handleApprove(row)">通过</el-button>
            <el-button type="danger" link @click="handleReject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="审批详情" width="600px" destroy-on-close>
      <template v-if="detailData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="审批标题" :span="2">{{ detailData.title }}</el-descriptions-item>
          <el-descriptions-item label="审批类型">{{ detailData.type_name }}</el-descriptions-item>
          <el-descriptions-item label="申请人">{{ detailData.applicant_name }}</el-descriptions-item>
          <el-descriptions-item label="申请时间" :span="2">{{ formatTime(detailData.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 20px; margin-bottom: 10px;">审批内容</h4>
        <el-descriptions :column="1" border v-if="detailData.content">
          <el-descriptions-item v-for="(value, key) in detailData.content" :key="key" :label="key">
            {{ value }}
          </el-descriptions-item>
        </el-descriptions>
      </template>

      <el-divider v-if="detailVisible" />
      
      <el-form v-if="detailVisible" ref="approvalFormRef" :model="approvalForm" label-width="80px">
        <el-form-item label="审批意见">
          <el-input v-model="approvalForm.comment" type="textarea" :rows="3" placeholder="请输入审批意见" />
        </el-form-item>
      </el-form>

      <template #footer v-if="detailVisible">
        <el-button @click="detailVisible = false">取消</el-button>
        <el-button type="success" :loading="submitting" @click="doApprove">通过</el-button>
        <el-button type="danger" :loading="submitting" @click="doReject">驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingApprovals, getApprovalDetail, approveApproval, rejectApproval } from '@/api/approvals'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const detailData = ref(null)
const approvalFormRef = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const approvalForm = reactive({
  comment: ''
})

function formatTime(time) {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
}

async function loadData() {
  loading.value = true
  try {
    const data = await getPendingApprovals({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    tableData.value = data.results || data
    pagination.total = data.count || 0
  } finally {
    loading.value = false
  }
}

async function handleDetail(row) {
  try {
    const data = await getApprovalDetail(row.id)
    detailData.value = data
    approvalForm.comment = ''
    detailVisible.value = true
  } catch {}
}

async function handleApprove(row) {
  try {
    const data = await getApprovalDetail(row.id)
    detailData.value = data
    approvalForm.comment = ''
    detailVisible.value = true
  } catch {}
}

async function handleReject(row) {
  try {
    const data = await getApprovalDetail(row.id)
    detailData.value = data
    approvalForm.comment = ''
    detailVisible.value = true
  } catch {}
}

async function doApprove() {
  try {
    submitting.value = true
    await approveApproval(detailData.value.id, { comment: approvalForm.comment })
    ElMessage.success('审批通过')
    detailVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function doReject() {
  try {
    submitting.value = true
    await rejectApproval(detailData.value.id, { comment: approvalForm.comment })
    ElMessage.success('已驳回')
    detailVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.approval-pending {
  .page-header {
    h2 {
      font-size: 20px;
      color: #303133;
      margin: 0;
    }
  }
  
  .table-container {
    background: #fff;
    padding: 16px;
    border-radius: 4px;
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
