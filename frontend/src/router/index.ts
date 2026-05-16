import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/transparencia', component: () => import('../views/Transparencia.vue') },
  { path: '/verificar', component: () => import('../views/Verificar.vue') },
  { path: '/urna', component: () => import('../views/UrnaWizard.vue') },
  { path: '/proposals', component: () => import('../views/Proposals.vue') },
  { path: '/admin', component: () => import('../views/Admin.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
