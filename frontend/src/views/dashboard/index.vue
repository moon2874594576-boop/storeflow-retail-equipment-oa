<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">员工总数</p>
              <h2 class="stat-value">{{ stats.employees }}</h2>
              <p class="stat-trend up">↑ 本月新增 {{ stats.newEmployees }} 人</p>
            </div>
            <div class="stat-icon blue">
              <el-icon :size="40"><Avatar /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">待审批</p>
              <h2 class="stat-value">{{ stats.pendingApprovals }}</h2>
              <p class="stat-trend">{{ stats.pendingApprovals > 0 ? '需要处理' : '暂无待办' }}</p>
            </div>
            <div class="stat-icon orange">
              <el-icon :size="40"><DocumentChecked /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">未读公告</p>
              <h2 class="stat-value">{{ stats.unreadAnnouncements }}</h2>
              <p class="stat-trend">{{ stats.unreadAnnouncements > 0 ? '有新消息' : '已全部阅读' }}</p>
            </div>
            <div class="stat-icon green">
              <el-icon :size="40"><Bell /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">我的审批</p>
              <h2 class="stat-value">{{ stats.myApprovals }}</h2>
              <p class="stat-trend">查看历史记录</p>
            </div>
            <div class="stat-icon purple">
              <el-icon :size="40"><Document /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近公告</span>
              <el-button type="primary" link @click="$router.push('/announcements/list')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentAnnouncements" stripe style="width: 100%">
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="publisher_name" label="发布人" width="120" />
            <el-table-column prop="published_at" label="发布时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.published_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>待办事项</span>
            </div>
          </template>
          <div class="todo-list">
            <div 
              v-for="item in todoList" 
              :key="item.title" 
              class="todo-item"
              @click="handleTodoClick(item)"
            >
              <el-icon :size="20" :color="item.color"><component :is="item.icon" /></el-icon>
              <div class="todo-info">
                <p class="todo-title">{{ item.title }}</p>
                <p class="todo-desc">{{ item.desc }}</p>
              </div>
              <el-icon :size="16" color="#c0c4cc"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷入口</span>
            </div>
          </template>
          <div class="quick-access">
            <div 
              v-for="item in quickAccess" 
              :key="item.path" 
              class="quick-item"
              @click="$router.push(item.path)"
            >
              <div class="quick-icon" :style="{ background: item.color }">
                <el-icon :size="28" color="#fff"><component :is="item.icon" /></el-icon>
              </div>
              <span class="quick-label">{{ item.label }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getEmployeeList } from '@/api/employees'
import { getMyApprovals, getPendingApprovals } from '@/api/approvals'
import { getAnnouncementList, getUnreadCount } from '@/api/announcements'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const stats = reactive({
  employees: 0,
  newEmployees: 3,
  pendingApprovals: 0,
  unreadAnnouncements: 0,
  myApprovals: 0
})

const recentAnnouncements = ref([])

const todoList = ref([
  { title: '待审批 2 条', desc: '点击处理待审批任务', icon: 'DocumentChecked', color: '#E6A23C', path: '/approvals/pending' },
  { title: '请假申请', desc: '发起请假流程', icon: 'Calendar', color: '#409EFF', path: '/approvals/create' },
  { title: '报销申请', desc: '提交费用报销', icon: 'Money', color: '#67C23A', path: '/approvals/create' }
])

const quickAccess = [
  { label: '发起审批', path: '/approvals/create', icon: 'Edit', color: '#409EFF' },
  { label: '我的审批', path: '/approvals/mine', icon: 'Document', color: '#67C23A' },
  { label: '发布公告', path: '/announcements/create', icon: 'Plus', color: '#E6A23C' },
  { label: '员工管理', path: '/employees/list', icon: 'Avatar', color: '#909399' },
  { label: '部门管理', path: '/employees/departments', icon: 'OfficeBuilding', color: '#F56C6C' },
  { label: '个人中心', path: '/profile', icon: 'User', color: '#8B5CF6' }
]

function formatTime(time) {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
}

function handleTodoClick(item) {
  router.push(item.path)
}

async function loadStats() {
  try {
    const [employeesData, pendingData, myApprovalsData, announcementsData, unreadData] = await Promise.all([
      getEmployeeList({ page_size: 1 }),
      getPendingApprovals({ page_size: 1 }),
      getMyApprovals({ page_size: 1 }),
      getAnnouncementList({ status: 1, page_size: 5 }),
      getUnreadCount()
    ])
    stats.employees = employeesData.count || 0
    stats.pendingApprovals = pendingData.count || 0
    stats.myApprovals = myApprovalsData.count || 0
    stats.unreadAnnouncements = unreadData.unread || 0
    recentAnnouncements.value = announcementsData.results || []
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-info {
    .stat-label {
      font-size: 14px;
      color: #909399;
      margin: 0 0 8px;
    }
    
    .stat-value {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
      margin: 0 0 4px;
    }
    
    .stat-trend {
      font-size: 12px;
      color: #c0c4cc;
      margin: 0;
      
      &.up {
        color: #67C23A;
      }
    }
  }
  
  .stat-icon {
    width: 72px;
    height: 72px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.blue { background: #ecf5ff; color: #409EFF; }
    &.orange { background: #fdf6ec; color: #E6A23C; }
    &.green { background: #f0f9eb; color: #67C23A; }
    &.purple { background: #f3e8ff; color: #8B5CF6; }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.todo-list {
  .todo-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover {
      background: #f5f7fa;
    }
    
    .todo-info {
      flex: 1;
      
      .todo-title {
        font-size: 14px;
        color: #303133;
        margin: 0 0 2px;
      }
      
      .todo-desc {
        font-size: 12px;
        color: #909399;
        margin: 0;
      }
    }
  }
}

.quick-access {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 20px;
  
  .quick-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: transform 0.2s;
    
    &:hover {
      transform: translateY(-4px);
    }
    
    .quick-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .quick-label {
      font-size: 13px;
      color: #606266;
    }
  }
}
</style>
