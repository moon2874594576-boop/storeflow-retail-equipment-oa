<template>
  <div class="role-list">
    <div class="page-header">
      <h2>角色管理</h2>
      <el-button type="primary" :icon="Plus" @click="handleAdd">新增角色</el-button>
    </div>

    <div class="table-container">
      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="权限数" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.permissions?.length || 0 }}</el-tag>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="权限">
          <el-tree
            ref="treeRef"
            :data="permissionTree"
            :props="{ label: 'name', children: 'children' }"
            show-checkbox
            node-key="code"
            :default-checked-keys="form.permission_ids"
            :check-strictly="false"
          />
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
import { getRoleList, createRole, updateRole, deleteRole, getPermissionList } from '@/api/users'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const treeRef = ref(null)
const tableData = ref([])
const permissionList = ref([])
const permissionTree = ref([])

const form = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  permission_ids: []
})

const dialogTitle = computed(() => form.id ? '编辑角色' : '新增角色')

const formRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

async function loadData() {
  loading.value = true
  try {
    const data = await getRoleList()
    tableData.value = data || []
  } finally {
    loading.value = false
  }
}

async function loadPermissions() {
  try {
    const data = await getPermissionList()
    permissionList.value = data || []
    buildPermissionTree()
  } catch {}
}

function buildPermissionTree() {
  const modules = {}
  permissionList.value.forEach(perm => {
    if (!modules[perm.module]) {
      modules[perm.module] = {
        name: perm.module,
        code: perm.module,
        children: []
      }
    }
    modules[perm.module].children.push({
      ...perm,
      name: `${perm.name}`
    })
  })
  permissionTree.value = Object.values(modules)
}

function handleAdd() {
  Object.assign(form, { id: null, name: '', code: '', description: '', permission_ids: [] })
  dialogVisible.value = true
}

function handleEdit(row) {
  Object.assign(form, {
    ...row,
    permission_ids: row.permissions?.map(p => p.code) || []
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    const checkedKeys = treeRef.value?.getCheckedKeys() || []
    const permissionCodes = checkedKeys.filter(key => {
      return !permissionTree.value.some(m => m.code === key)
    })
    form.permission_ids = permissionCodes
    
    if (form.id) {
      await updateRole(form.id, {
        name: form.name,
        description: form.description,
        permission_ids: permissionCodes
      })
      ElMessage.success('更新成功')
    } else {
      await createRole({
        name: form.name,
        code: form.code,
        description: form.description,
        permission_ids: permissionCodes
      })
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
    await ElMessageBox.confirm(`确定删除角色「${row.name}」吗？`, '提示', { type: 'warning' })
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

onMounted(() => {
  loadData()
  loadPermissions()
})
</script>

<style lang="scss" scoped>
.role-list {
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
