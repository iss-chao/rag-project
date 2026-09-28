import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const Layout = () => import('@/layout/Layout.vue')

const routes = [
  {
    path: '/',
    redirect: '/kb'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/401',
    name: '401',
    component: () => import('@/views/401.vue')
  },
  {
    path: '/layout',
    component: Layout,
    redirect: '/kb',
    children: [
      {
        path: '/kb',
        name: 'KbList',
        component: () => import('@/views/KbList.vue'),
        meta: { title: '知识库管理',permission: ['admin', "user"] }
      },
      {
        path: '/kb/detail/:kbId',
        name: 'KbDetail',
        component: () => import('@/views/KbDetail.vue'),
        meta: { title: '知识库详情', requireAdmin: true}
      },
      {
        path: '/chat/:threadId?',
        name: 'Chat',
        component: () => import('@/views/Chat.vue'),
        meta: { title: '对话', requireAdmin: true}
      },
      {
        path: '/etl-task',
        name: 'EtlTask',
        component: () => import('@/views/EtlTask.vue'),
        meta: { title: 'ETL任务', permission: ['admin', "user"] }
      },
      {
        path: '/user-manage',
        name: 'UserManage',
        component: () => import('@/views/UserManage.vue'),
        meta: { title: '用户管理', permission: ['admin'] }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
