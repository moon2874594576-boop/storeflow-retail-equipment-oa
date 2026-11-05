<template>
  <div class="approval-mine">
    <div class="page-header">
      <h2>我的审批</h2>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="关键字">
          <el-input v-model="searchForm.keyword" placeholder="审批标题" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已撤回" value="revoked" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
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
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              type="warning" 
              link 
              @click="handleRevoke(row)"
            >撤回</el-button>
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
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(detailData.status)">{{ detailData.status_display }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申请人">{{ detailData.applicant_name }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ formatTime(detailData.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin-top: 20px; margin-bottom: 10px;">审批内容</h4>
        <el-descriptions :column="1" border v-if="detailData.content">
          <el-descriptions-item v-for="(value, key) in detailData.content" :key="key" :label="key">
            {{ value }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px; margin-bottom: 10px;">审批记录</h4>
        <el-timeline v-if="detailData.records?.length">
          <el-timeline-item 
            v-for="record in detailData.records" 
            :key="record.id"
            :type="record.action === 'approve' ? 'success' : record.action === 'reject' ? 'danger' : 'info'"
          >
            <strong>{{ record.approver_name }}</strong> {{ record.action === 'approve' ? '通过' : record.action === 'reject' ? '驳回' : '发起' }}
            <p v-if="record.comment">{{ record.comment }}</p>
            <small>{{ formatTime(record.created_at) }}</small>
          </el-timeline-item>
        </el-timeline>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMyApprovals, getApprovalDetail, revokeApproval } from '@/api/approvals'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const detailData = ref(null)

const searchForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

function statusType(status) {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger', revoked: 'info' }
  return map[status] || ''
}

function formatTime(time) {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      status: searchForm.status || ''
    }
    const data = await getMyApprovals(params)
    tableData.value = data.results || data
    pagination.total = data.count || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

async function handleDetail(row) {
  try {
    const data = await getApprovalDetail(row.id)
    detailData.value = data
    detailVisible.value = true
  } catch {}
}

async function handleRevoke(row) {
  try {
    await ElMessageBox.confirm('确定要撤回此审批吗？', '提示', { type: 'warning' })
    await revokeApproval(row.id)
    ElMessage.success('撤回成功')
    loadData()
  } catch {}
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.approval-mine {
  .page-header {
    h2 {
      font-size: 20px;
      color: #303133;
      margin: 0;
    }
  }
  
  .search-bar {
    background: #fff;
    padding: 16px;
    border-radius: 4px;
    margin-bottom: 20px;
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
