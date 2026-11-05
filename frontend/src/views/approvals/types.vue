<template>
  <div class="approval-types">
    <div class="page-header">
      <h2>审批类型配置</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增审批类型</el-button>
    </div>

    <div class="table-container">
      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="code" label="编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="表单字段数" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.fields?.length || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        
        <el-form-item label="表单字段">
          <div class="fields-container">
            <div v-for="(field, index) in form.fields" :key="index" class="field-item">
              <el-row :gutter="10">
                <el-col :span="6">
                  <el-input v-model="field.key" placeholder="字段key" />
                </el-col>
                <el-col :span="6">
                  <el-input v-model="field.label" placeholder="字段名称" />
                </el-col>
                <el-col :span="5">
                  <el-select v-model="field.type" placeholder="类型">
                    <el-option label="文本" value="text" />
                    <el-option label="多行文本" value="textarea" />
                    <el-option label="数字" value="number" />
                    <el-option label="日期" value="date" />
                    <el-option label="下拉选择" value="select" />
                  </el-select>
                </el-col>
                <el-col :span="6">
                  <el-input 
                    v-if="field.type === 'select'" 
                    v-model="field.options" 
                    placeholder="选项(逗号分隔)"
                  />
                </el-col>
                <el-col :span="1">
                  <el-button type="danger" :icon="Delete" circle @click="removeField(index)" />
                </el-col>
              </el-row>
            </div>
            <el-button type="primary" link :icon="Plus" @click="addField">添加字段</el-button>
          </div>
        </el-form-item>

        <el-form-item label="审批人">
          <el-select v-model="form.approvers" multiple placeholder="选择审批人">
            <el-option v-for="user in userList" :key="user.id" :label="user.username" :value="user.id" />
          </el-select>
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
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getApprovalTypeList, createApprovalType, updateApprovalType, deleteApprovalType } from '@/api/approvals'
import { getUserList } from '@/api/users'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const tableData = ref([])
const userList = ref([])

const form = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  fields: [],
  approvers: []
})

const dialogTitle = computed(() => form.id ? '编辑审批类型' : '新增审批类型')

const formRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }]
}

async function loadData() {
  loading.value = true
  try {
    const data = await getApprovalTypeList()
    tableData.value = data || []
  } finally {
    loading.value = false
  }
}

async function loadUsers() {
  try {
    const data = await getUserList({ page_size: 100 })
    userList.value = data.results || []
  } catch {}
}

function addField() {
  form.fields.push({ key: '', label: '', type: 'text', options: '' })
}

function removeField(index) {
  form.fields.splice(index, 1)
}

function handleAdd() {
  Object.assign(form, { id: null, name: '', code: '', description: '', fields: [], approvers: [] })
  dialogVisible.value = true
}

function handleEdit(row) {
  const fields = (row.fields || []).map(f => ({
    ...f,
    options: Array.isArray(f.options) ? f.options.join(',') : (f.options || '')
  }))
  Object.assign(form, {
    ...row,
    fields,
    approvers: row.approvers || []
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    const data = {
      ...form,
      fields: form.fields.map(f => ({
        ...f,
        options: f.options ? f.options.split(',').map(o => o.trim()).filter(Boolean) : []
      }))
    }
    if (form.id) {
      await updateApprovalType(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await createApprovalType(data)
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
    await ElMessageBox.confirm(`确定删除「${row.name}」吗？`, '提示', { type: 'warning' })
    await deleteApprovalType(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

onMounted(() => {
  loadData()
  loadUsers()
})
</script>

<style lang="scss" scoped>
.approval-types {
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
  
  .fields-container {
    width: 100%;
    
    .field-item {
      margin-bottom: 10px;
    }
  }
}
</style>
