<template>
  <div class="announcement-create">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑公告' : '发布公告' }}</h2>
    </div>

    <div class="form-container">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority">
            <el-option label="普通" :value="1" />
            <el-option label="重要" :value="2" />
            <el-option label="紧急" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布部门">
          <el-select v-model="form.department" placeholder="选择部门" clearable>
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="请输入公告内容" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ isEdit ? '保存' : '保存草稿' }}</el-button>
          <el-button type="success" :loading="submitting" @click="handlePublish" v-if="!isEdit">保存并发布</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  getAnnouncementDetail, createAnnouncement, updateAnnouncement, publishAnnouncement 
} from '@/api/announcements'
import { getDepartmentList } from '@/api/employees'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const departmentList = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  content: '',
  department: null,
  priority: 1
})

const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

async function loadDetail() {
  if (route.params.id) {
    try {
      const data = await getAnnouncementDetail(route.params.id)
      Object.assign(form, {
        title: data.title,
        content: data.content,
        department: data.department || null,
        priority: data.priority || 1
      })
    } catch {}
  }
}

async function loadDepartments() {
  try {
    const data = await getDepartmentList()
    departmentList.value = data || []
  } catch {}
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    if (isEdit.value) {
      await updateAnnouncement(route.params.id, form)
      ElMessage.success('保存成功')
    } else {
      await createAnnouncement(form)
      ElMessage.success('保存成功')
    }
    router.push('/announcements/list')
  } finally {
    submitting.value = false
  }
}

async function handlePublish() {
  try {
    await formRef.value.validate()
    submitting.value = true
    const data = await createAnnouncement({ ...form })
    await publishAnnouncement(data.id)
    ElMessage.success('发布成功')
    router.push('/announcements/list')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadDetail()
  loadDepartments()
})
</script>

<style lang="scss" scoped>
.announcement-create {
  .page-header {
    h2 {
      font-size: 20px;
      color: #303133;
      margin: 0;
    }
  }
  
  .form-container {
    background: #fff;
    padding: 32px;
    border-radius: 4px;
    max-width: 800px;
  }
}
</style>
