<template>
  <div class="approval-create">
    <div class="page-header">
      <h2>发起审批</h2>
    </div>

    <div class="form-container">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="审批类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择审批类型" @change="handleTypeChange">
            <el-option v-for="type in typeList" :key="type.id" :label="type.name" :value="type.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="审批标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入审批标题" />
        </el-form-item>

        <template v-if="currentType">
          <el-form-item 
            v-for="field in currentType.fields" 
            :key="field.key" 
            :label="field.label"
            :prop="`content.${field.key}`"
          >
            <el-input 
              v-if="field.type === 'text'" 
              v-model="form.content[field.key]" 
              :placeholder="`请输入${field.label}`"
            />
            <el-input 
              v-else-if="field.type === 'textarea'" 
              v-model="form.content[field.key]" 
              type="textarea" 
              :rows="4"
              :placeholder="`请输入${field.label}`"
            />
            <el-input 
              v-else-if="field.type === 'number'" 
              v-model.number="form.content[field.key]" 
              type="number"
              :placeholder="`请输入${field.label}`"
            />
            <el-date-picker 
              v-else-if="field.type === 'date'" 
              v-model="form.content[field.key]" 
              type="date"
              value-format="YYYY-MM-DD"
              :placeholder="`请选择${field.label}`"
            />
            <el-select 
              v-else-if="field.type === 'select'" 
              v-model="form.content[field.key]" 
              :placeholder="`请选择${field.label}`"
            >
              <el-option 
                v-for="option in field.options" 
                :key="option" 
                :label="option" 
                :value="option" 
              />
            </el-select>
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">提交审批</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getApprovalTypeList, createApproval } from '@/api/approvals'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const typeList = ref([])

const form = reactive({
  type: null,
  title: '',
  content: {}
})

const currentType = computed(() => {
  return typeList.value.find(t => t.id === form.type)
})

const formRules = {
  type: [{ required: true, message: '请选择审批类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入审批标题', trigger: 'blur' }]
}

async function loadTypes() {
  try {
    const data = await getApprovalTypeList()
    typeList.value = data || []
  } catch {}
}

function handleTypeChange() {
  form.content = {}
  if (currentType.value) {
    currentType.value.fields.forEach(field => {
      if (field.type === 'number') {
        form.content[field.key] = 0
      } else {
        form.content[field.key] = ''
      }
    })
  }
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true
    await createApproval({
      type: form.type,
      title: form.title,
      content: form.content
    })
    ElMessage.success('审批提交成功')
    router.push('/approvals/mine')
  } finally {
    submitting.value = false
  }
}

function handleReset() {
  formRef.value?.resetFields()
  form.content = {}
}

onMounted(() => {
  loadTypes()
})
</script>

<style lang="scss" scoped>
.approval-create {
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
    max-width: 700px;
  }
}
</style>
