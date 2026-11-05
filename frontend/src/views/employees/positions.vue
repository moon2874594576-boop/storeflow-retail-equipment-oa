<template>
  <div class="position-list">
    <div class="page-header">
      <h2>岗位管理</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增岗位</el-button>
    </div>

    <div class="table-container">
      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="岗位名称" width="150" />
        <el-table-column prop="code" label="岗位编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="岗位名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="岗位编码" prop="code">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
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
import { getPositionList, createPosition, updatePosition, deletePosition } from '@/api/employees'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const tableData = ref([])

const form = reactive({
  id: null,
  name: '',
  code: '',
  description: ''
})

const dialogTitle = computed(() => form.id ? '编辑岗位' : '新增岗位')

const formRules = {
  name: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入岗位编码', trigger: 'blur' }]
}

async function loadData() {
  loading.value = true
  try {
    const data = await getPositionList()
    tableData.value = data || []
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  Object.assign(form, { id: null, name: '', code: '', description: '' })
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
    if (form.id) {
      await updatePosition(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createPosition(form)
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
    await ElMessageBox.confirm(`确定删除岗位「${row.name}」吗？`, '提示', { type: 'warning' })
    await deletePosition(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.position-list {
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
  
  .table-container {
    background: #fff;
    padding: 16px;
    border-radius: 4px;
  }
}
</style>
