<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="profile-card">
          <template #header>
            <span>头像信息</span>
          </template>
          <div class="avatar-section">
            <el-avatar :size="100" :src="userStore.userInfo?.avatar">
              {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <h3>{{ userStore.userInfo?.username }}</h3>
            <p class="role">{{ userStore.userInfo?.role_name || '普通用户' }}</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>基本信息</span>
          </template>
          <el-form ref="profileFormRef" :model="profileForm" :rules="profileRules" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="handleSaveProfile">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="handleChangePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateProfile, changePassword } from '@/api/auth'

const userStore = useUserStore()
const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const submitting = ref(false)

const profileForm = reactive({
  username: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const profileRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

async function loadProfile() {
  if (userStore.userInfo) {
    profileForm.username = userStore.userInfo.username
    profileForm.email = userStore.userInfo.email
    profileForm.phone = userStore.userInfo.phone
  }
}

async function handleSaveProfile() {
  try {
    await profileFormRef.value.validate()
    submitting.value = true
    await updateProfile({
      email: profileForm.email,
      phone: profileForm.phone
    })
    userStore.fetchUserInfo()
    ElMessage.success('保存成功')
  } finally {
    submitting.value = false
  }
}

async function handleChangePassword() {
  try {
    await passwordFormRef.value.validate()
    submitting.value = true
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功')
    passwordFormRef.value?.resetFields()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style lang="scss" scoped>
.profile-page {
  .page-header {
    h2 {
      font-size: 20px;
      color: #303133;
      margin: 0;
    }
  }
  
  .profile-card {
    text-align: center;
    
    .avatar-section {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      
      h3 {
        margin: 0;
        color: #303133;
      }
      
      .role {
        margin: 0;
        color: #909399;
        font-size: 14px;
      }
    }
  }
}
</style>
