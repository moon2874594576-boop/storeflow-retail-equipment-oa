<template>
  <div class="employee-list">
    <div class="page-header">
      <h2>员工管理</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增员工</el-button>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" @submit.prevent="handleSearch">
        <el-form-item label="关键字">
          <el-input v-model="searchForm.keyword" placeholder="工号/姓名/手机/邮箱" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="searchForm.department" placeholder="全部" clearable>
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="在职" :value="1" />
            <el-option label="离职" :value="0" />
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
        <el-table-column prop="employee_no" label="工号" width="100" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="70">
          <template #default="{ row }">
            {{ row.gender === 1 ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="department_name" label="部门" width="130">
          <template #default="{ row }">
            {{ row.department_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="position_name" label="岗位" width="120">
          <template #default="{ row }">
            {{ row.position_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entry_date" label="入职日期" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_no">
              <el-input v-model="form.employee_no" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender">
                <el-option label="男" :value="1" />
                <el-option label="女" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期">
              <el-date-picker v-model="form.entry_date" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="form.id_card" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status">
                <el-option label="在职" :value="1" />
                <el-option label="离职" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门">
              <el-select v-model="form.department" placeholder="选择部门" clearable>
                <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="岗位">
              <el-select v-model="form.position" placeholder="选择岗位" clearable>
                <el-option v-for="pos in positionList" :key="pos.id" :label="pos.name" :value="pos.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getEmployeeList, createEmployee, updateEmployee, deleteEmployee,
  getDepartmentList, getPositionList 
} from '@/api/employees'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const tableData = ref([])
const departmentList = ref([])
const positionList = ref([])

const searchForm = reactive({
  keyword: '',
  department: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const form = reactive({
  id: null,
  employee_no: '',
  name: '',
  gender: 1,
  id_card: '',
  phone: '',
  email: '',
  department: null,
  position: null,
  entry_date: '',
  status: 1
})

const dialogTitle = computed(() => form.id ? '编辑员工' : '新增员工')

const formRules = {
  employee_no: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword,
      department: searchForm.department || '',
      status: searchForm.status || ''
    }
    const data = await getEmployeeList(params)
    tableData.value = data.results || data
    pagination.total = data.count || 0
  } finally {
    loading.value = false
  }
}

async function loadDepartments() {
  try {
    const data = await getDepartmentList()
    departmentList.value = data || []
  } catch {}
}

async function loadPositions() {
  try {
    const data = await getPositionList()
    positionList.value = data || []
  } catch {}
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.department = ''
  searchForm.status = ''
  handleSearch()
}

function handleAdd() {
  Object.assign(form, {
    id: null, employee_no: '', name: '', gender: 1, id_card: '',
    phone: '', email: '', department: null, position: null,
    entry_date: '', status: 1
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    const data = { ...form }
    if (form.id) {
      await updateEmployee(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await createEmployee(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除员工「${row.name}」吗？`, '提示', { type: 'warning' })
    await deleteEmployee(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

onMounted(() => {
  loadData()
  loadDepartments()
  loadPositions()
})
</script>

<style lang="scss" scoped>
.employee-list {
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
  
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
