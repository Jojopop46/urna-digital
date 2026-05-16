<template>
  <div class="admin-container">
    <!-- Login -->
    <main v-if="!auth" class="login-wrapper">
      <div class="glass-panel login-card">
        <div class="login-icon" aria-hidden="true">🏛️</div>
        <h1>{{ $t('admin.login.title') }}</h1>
        <p>{{ $t('admin.login.subtitle') }}</p>
        <div class="form-group">
          <label for="admin-user">{{ $t('admin.login.user_label') }}</label>
          <input id="admin-user" v-model="user" type="text" class="form-input" :placeholder="$t('admin.login.user_placeholder')" @keyup.enter="login">
        </div>
        <div class="form-group">
          <label for="admin-pwd">{{ $t('admin.login.pass_label') }}</label>
          <input id="admin-pwd" v-model="pwd" type="password" class="form-input" :placeholder="$t('admin.login.pass_placeholder')" @keyup.enter="login">
        </div>
        <button @click="login" class="btn btn-primary w-full">{{ $t('admin.login.button') }}</button>
        <p v-if="loginError" class="login-error" role="alert" aria-live="assertive">{{ loginError }}</p>
      </div>
    </main>

    <!-- Dashboard -->
    <main v-else class="dashboard">
      <div class="dashboard-header">
        <div>
          <h1>{{ $t('admin.dashboard.title') }}</h1>
          <p class="header-sub">{{ $t('admin.dashboard.subtitle') }}</p>
        </div>
        <button @click="logout" class="btn btn-outline">{{ $t('admin.dashboard.logout') }}</button>
      </div>

      <div class="dashboard-grid">
        <!-- Settings -->
        <div class="settings-col">
          <div class="glass-panel card">
            <h2><span aria-hidden="true">⚙️</span> {{ $t('admin.settings.title') }}</h2>
            <label for="admin-deadline">{{ $t('admin.settings.deadline_label') }}</label>
            <input id="admin-deadline" type="datetime-local" v-model="s.dl" class="form-input">
          </div>

          <div class="glass-panel card">
            <h2><span aria-hidden="true">👤</span> {{ $t('admin.admins.title') }}</h2>
            <div class="form-group">
              <label for="new-user">{{ $t('admin.admins.user_label') }}</label>
              <input id="new-user" v-model="newUser" type="text" class="form-input" :placeholder="$t('admin.admins.user_placeholder')">
            </div>
            <div class="form-group">
              <label for="new-pwd">{{ $t('admin.admins.pass_label') }}</label>
              <input id="new-pwd" v-model="newPwd" type="password" class="form-input" :placeholder="$t('admin.admins.pass_placeholder')">
            </div>
            <button @click="createUser" class="btn btn-primary w-full" :disabled="!newUser || !newPwd || newPwd.length < 4">{{ $t('admin.admins.button') }}</button>
            <p v-if="pwdMsg" :class="['msg', pwdMsg.includes($t('admin.admins.error_exists')) ? 'msg-error' : 'msg-success']" role="status" aria-live="polite">{{ pwdMsg }}</p>
          </div>
        </div>

        <!-- Proposals -->
        <div class="proposals-col">
          <div class="section-title-row">
            <h2><span aria-hidden="true">📋</span> {{ $t('admin.proposals.title') }}</h2>
            <span class="badge-count" v-if="pending.length">{{ pending.length }}</span>
          </div>

          <transition-group name="fade" tag="div" class="proposals-list">
            <article v-for="p in pending" :key="p.id" class="glass-panel proposal-item" :aria-labelledby="'prop-title-' + p.id">
              <h3 :id="'prop-title-' + p.id">{{ p.titulo }}</h3>
              <p>{{ p.descripcion }}</p>
              <div class="proposal-meta">
                <span><span aria-hidden="true">📍</span> {{ p.municipio }}</span>
                <span><span aria-hidden="true">💰</span> {{ p.costo }}</span>
              </div>
              <div class="proposal-actions">
                <button @click="approveProposal(p.id)" class="btn btn-primary btn-sm"><span aria-hidden="true">✓</span> {{ $t('admin.proposals.approve') }}</button>
                <button @click="rejectProposal(p.id)" class="btn btn-outline btn-sm" style="color:var(--danger);border-color:var(--panel-border);"><span aria-hidden="true">✕</span> {{ $t('admin.proposals.reject') }}</button>
              </div>
            </article>
          </transition-group>

          <div v-if="!pending.length" class="glass-panel empty-card" role="status" aria-live="polite">
            <div class="empty-icon" aria-hidden="true">🎉</div>
            <p>{{ $t('admin.proposals.empty') }}</p>
          </div>
        </div>
      </div>

      <!-- Live Chart -->
      <LiveResultsChart process-id="proceso_2025" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUrnaStore } from '../stores/useUrnaStore';
import { api, setAdminToken, getAdminToken } from '../services/api';
import LiveResultsChart from '../components/admin/LiveResultsChart.vue'

const { t } = useI18n();
const s = useUrnaStore();
const user = ref('');
const pwd = ref('');
const newUser = ref('');
const newPwd = ref('');
const loginError = ref('');
const pwdMsg = ref('');
const auth = ref(!!getAdminToken());
const pending = ref<any[]>([]);

const loadPending = async () => {
  try {
    pending.value = await api.get('/api/v1/proposals/pending');
  } catch {
    pending.value = [];
  }
};

const login = async () => {
  loginError.value = '';
  try {
    const data = await api.post('/api/v1/admin/login', { username: user.value, password: pwd.value });
    setAdminToken(data.access_token);
    auth.value = true;
    await loadPending();
  } catch {
    loginError.value = t('admin.login.error');
  }
};

const logout = () => {
  setAdminToken(null);
  auth.value = false;
  user.value = '';
  pwd.value = '';
  pending.value = [];
};

const createUser = async () => {
  if (!newUser.value || newPwd.value.length < 4) return;
  pwdMsg.value = '';
  try {
    await api.post('/api/v1/admin/users', { username: newUser.value, password: newPwd.value });
    pwdMsg.value = t('admin.admins.success', { user: newUser.value });
    newUser.value = '';
    newPwd.value = '';
    setTimeout(() => pwdMsg.value = '', 4000);
  } catch (e: any) {
    pwdMsg.value = e.message || t('admin.admins.error_exists');
  }
};

const approveProposal = async (id: number) => {
  try {
    await api.patch(`/api/v1/proposals/${id}`, { status: 'approved' });
    await loadPending();
  } catch {
    // ignorar
  }
};

const rejectProposal = async (id: number) => {
  try {
    await api.patch(`/api/v1/proposals/${id}`, { status: 'rejected' });
    await loadPending();
  } catch {
    // ignorar
  }
};

onMounted(async () => {
  if (auth.value) await loadPending();
});
</script>

<style scoped>
.admin-container { max-width: 1100px; margin: 0 auto; }

/* Login */
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 1rem;
}
.login-card {
  max-width: 420px;
  width: 100%;
  padding: 2.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.login-icon { font-size: 3rem; }
.login-card h1 { font-size: 1.4rem; font-weight: 800; }
.login-card p { color: var(--text-muted); font-size: 0.9375rem; }
.form-group { text-align: left; }
.form-group label { display: block; margin-bottom: 0.375rem; font-weight: 600; font-size: 0.875rem; }
.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid var(--panel-border);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-main);
  transition: var(--transition);
  font-family: inherit;
}
.form-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-light); }
.login-error { color: var(--danger); font-weight: 600; font-size: 0.9375rem; }

/* Dashboard */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.dashboard-header h1 { font-size: 1.5rem; font-weight: 800; }
.header-sub { color: var(--text-muted); font-size: 0.9375rem; }

.dashboard-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.5rem;
  align-items: start;
  margin-bottom: 1.5rem;
}

.card {
  padding: 1.5rem;
  margin-bottom: 1rem;
}
.card h2 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.proposals-col {}
.section-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.section-title-row h2 { font-size: 1.1rem; font-weight: 700; }
.badge-count {
  background: var(--primary);
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.proposals-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.proposal-item {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.proposal-item h3 { color: var(--primary); font-size: 1.05rem; font-weight: 700; }
.proposal-item p { color: var(--text-muted); font-size: 0.9375rem; line-height: 1.5; }
.proposal-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}
.proposal-actions {
  display: flex;
  gap: 0.5rem;
}
.btn-sm { padding: 0.5rem 1rem; font-size: 0.875rem; }

.empty-card {
  padding: 2.5rem;
  text-align: center;
  color: var(--text-muted);
}
.empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }

.msg { margin-top: 0.75rem; font-size: 0.875rem; font-weight: 600; }
.msg-success { color: var(--secondary); }
.msg-error { color: var(--danger); }

@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .login-card { padding: 1.5rem; }
}
</style>
