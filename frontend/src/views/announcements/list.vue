<template>
  <div class="announcement-list">
    <div class="page-header">
      <h2>公告列表</h2>
      <el-button type="primary" :icon="Plus" @click="$router.push('/announcements/create')">发布公告</el-button>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="关键字">
          <el-input v-model="searchForm.keyword" placeholder="标题/内容" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="草稿" :value="0" />
            <el-option label="已发布" :value="1" />
            <el-option label="已撤回" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="全部" clearable>
            <el-option label="普通" :value="1" />
            <el-option label="重要" :value="2" />
            <el-option label="紧急" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" @row-click="handleRowClick">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="标题" min-width="200">
          <template #default="{ row }">
            <div class="title-cell">
              <el-tag v-if="row.priority === 3" type="danger" size="small">紧急</el-tag>
              <el-tag v-else-if="row.priority === 2" type="warning" size="small">重要</el-tag>
              <span>{{ row.title }}</span>
              <el-tag v-if="!row.is_read" type="info" size="small" style="margin-left: 8px">未读</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="publisher_name" label="发布人" width="120" />
        <el-table-column prop="department_name" label="部门" width="120">
          <template #default="{ row }">
            {{ row.department_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : row.status === 0 ? 'info' : 'warning'">
              {{ row.status === 1 ? '已发布' : row.status === 0 ? '草稿' : '已撤回' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.published_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" @click.stop>
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 0" type="success" link @click="handlePublish(row)">发布</el-button>
            <el-button v-if="row.status === 1" type="warning" link @click="handleRevoke(row)">撤回</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="detailVisible" title="公告详情" width="600px" destroy-on-close>
      <template v-if="detailData">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="标题">{{ detailData.title }}</el-descriptions-item>
          <el-descriptions-item label="发布人">{{ detailData.publisher_name }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ detailData.department_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="detailData.priority === 3 ? 'danger' : detailData.priority === 2 ? 'warning' : 'info'">
              {{ detailData.priority_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailData.status === 1 ? 'success' : 'info'">
              {{ detailData.status_display }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 16px;">
          <h4>公告内容</h4>
          <div class="announcement-content">{{ detailData.content }}</div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getAnnouncementList, getAnnouncementDetail, 
  publishAnnouncement, revokeAnnouncement, 
  deleteAnnouncement, readAnnouncement 
} from '@/api/announcements'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const detailVisible = ref(false)
const detailData = ref(null)

const searchForm = reactive({
  keyword: '',
  status: '',
  priority: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

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
      status: searchForm.status !== '' ? searchForm.status : '',
      priority: searchForm.priority !== '' ? searchForm.priority : ''
    }
    const data = await getAnnouncementList(params)
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
  searchForm.priority = ''
  handleSearch()
}

async function handleView(row) {
  try {
    const data = await getAnnouncementDetail(row.id)
    detailData.value = data
    detailVisible.value = true
    if (row.status === 1 && !row.is_read) {
      await readAnnouncement(row.id)
    }
  } catch {}
}

function handleRowClick(row) {
  handleView(row)
}

async function handlePublish(row) {
  try {
    await ElMessageBox.confirm('确定发布此公告吗？', '提示')
    await publishAnnouncement(row.id)
    ElMessage.success('发布成功')
    loadData()
  } catch {}
}

async function handleRevoke(row) {
  try {
    await ElMessageBox.confirm('确定撤回此公告吗？', '提示', { type: 'warning' })
    await revokeAnnouncement(row.id)
    ElMessage.success('已撤回')
    loadData()
  } catch {}
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除公告「${row.title}」吗？`, '提示', { type: 'warning' })
    await deleteAnnouncement(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.announcement-list {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
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
  
  .title-cell {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .announcement-content {
    white-space: pre-wrap;
    line-height: 1.8;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 4px;
  }
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
