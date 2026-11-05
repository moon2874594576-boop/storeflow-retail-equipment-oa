<template>
  <div class="department-list">
    <div class="page-header">
      <h2>部门管理</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd(null)">新增部门</el-button>
    </div>

    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" row-key="id" :tree-props="{ children: 'children' }" default-expand-all>
        <el-table-column prop="name" label="部门名称" min-width="200" />
        <el-table-column prop="code" label="部门编码" width="120" />
        <el-table-column prop="parent_name" label="上级部门" width="150">
          <template #default="{ row }">
            {{ row.parent_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="manager_name" label="负责人" width="120">
          <template #default="{ row }">
            {{ row.manager_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleAdd(row.id)">新增子部门</el-button>
            <el-button type="warning" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="form.parent" placeholder="无（顶级部门）" clearable>
            <el-option v-for="dept in flatDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
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
import { getDepartmentTree, createDepartment, updateDepartment, deleteDepartment } from '@/api/employees'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const tableData = ref([])
const flatData = ref([])

const form = reactive({
  id: null,
  name: '',
  code: '',
  parent: null,
  sort: 0
})

const dialogTitle = computed(() => form.id ? '编辑部门' : '新增部门')

const formRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }]
}

const flatDepartments = computed(() => {
  const result = []
  function flatten(list) {
    list.forEach(item => {
      result.push({ id: item.id, name: item.name })
      if (item.children && item.children.length) {
        flatten(item.children)
      }
    })
  }
  flatten(flatData.value)
  return result
})

async function loadData() {
  loading.value = true
  try {
    const data = await getDepartmentTree()
    tableData.value = data || []
  } finally {
    loading.value = false
  }
}

async function loadFlatData() {
  try {
    const data = await getDepartmentTree()
    flatData.value = data || []
  } catch {}
}

function handleAdd(parentId) {
  Object.assign(form, { id: null, name: '', code: '', parent: parentId, sort: 0 })
  dialogVisible.value = true
}

function handleEdit(row) {
  Object.assign(form, {
    id: row.id,
    name: row.name,
    code: row.code,
    parent: row.parent || null,
    sort: row.sort || 0
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    if (form.id) {
      await updateDepartment(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createDepartment(form)
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
    await ElMessageBox.confirm(`确定删除部门「${row.name}」吗？`, '提示', { type: 'warning' })
    await deleteDepartment(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

onMounted(() => {
  loadData()
  loadFlatData()
})
</script>

<style lang="scss" scoped>
.department-list {
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
