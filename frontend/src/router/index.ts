import { createRouter, createWebHistory } from 'vue-router'
import { nextTick } from 'vue'
import i18n from '../i18n'

const routes = [
  { path: '/', component: () => import('../views/Home.vue'), meta: { titleKey: 'nav.home' } },
  { path: '/transparencia', component: () => import('../views/Transparencia.vue'), meta: { titleKey: 'nav.transparency' } },
  { path: '/verificar', component: () => import('../views/Verificar.vue'), meta: { titleKey: 'nav.verify' } },
  { path: '/urna', component: () => import('../views/UrnaWizard.vue'), meta: { titleKey: 'nav.vote' } },
  { path: '/proposals', component: () => import('../views/Proposals.vue'), meta: { titleKey: 'nav.proposals' } },
  { path: '/admin', component: () => import('../views/Admin.vue'), meta: { titleKey: 'nav.admin' } },
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  const titleKey = to.meta?.titleKey as string | undefined
  const pageTitle = titleKey ? i18n.global.t(titleKey) : 'Urna Digital'
  nextTick(() => {
    document.title = `${pageTitle} — Urna Digital`
  })
})
