import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'users/list',
        name: 'UserList',
        component: () => import('@/views/users/list.vue'),
        meta: { title: '用户列表', icon: 'User', requiresAuth: true }
      },
      {
        path: 'users/roles',
        name: 'RoleList',
        component: () => import('@/views/users/roles.vue'),
        meta: { title: '角色管理', icon: 'UserFilled', requiresAuth: true }
      },
      {
        path: 'employees/list',
        name: 'EmployeeList',
        component: () => import('@/views/employees/list.vue'),
        meta: { title: '员工列表', icon: 'Avatar', requiresAuth: true }
      },
      {
        path: 'employees/departments',
        name: 'DepartmentList',
        component: () => import('@/views/employees/departments.vue'),
        meta: { title: '部门管理', icon: 'OfficeBuilding', requiresAuth: true }
      },
      {
        path: 'employees/positions',
        name: 'PositionList',
        component: () => import('@/views/employees/positions.vue'),
        meta: { title: '岗位管理', icon: 'Medal', requiresAuth: true }
      },
      {
        path: 'approvals/create',
        name: 'ApprovalCreate',
        component: () => import('@/views/approvals/create.vue'),
        meta: { title: '发起审批', icon: 'Edit', requiresAuth: true }
      },
      {
        path: 'approvals/mine',
        name: 'ApprovalMine',
        component: () => import('@/views/approvals/mine.vue'),
        meta: { title: '我的审批', icon: 'Document', requiresAuth: true }
      },
      {
        path: 'approvals/pending',
        name: 'ApprovalPending',
        component: () => import('@/views/approvals/pending.vue'),
        meta: { title: '待我审批', icon: 'DocumentChecked', requiresAuth: true }
      },
      {
        path: 'approvals/types',
        name: 'ApprovalTypeList',
        component: () => import('@/views/approvals/types.vue'),
        meta: { title: '审批类型', icon: 'Setting', requiresAuth: true }
      },
      {
        path: 'announcements/list',
        name: 'AnnouncementList',
        component: () => import('@/views/announcements/list.vue'),
        meta: { title: '公告列表', icon: 'Bell', requiresAuth: true }
      },
      {
        path: 'announcements/create',
        name: 'AnnouncementCreate',
        component: () => import('@/views/announcements/create.vue'),
        meta: { title: '发布公告', icon: 'Plus', requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心', icon: 'User', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const whiteList = ['/login']

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (whiteList.includes(to.path)) {
    if (userStore.isLoggedIn()) {
      next('/')
    } else {
      next()
    }
  } else {
    if (userStore.isLoggedIn()) {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

export default router