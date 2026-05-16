<template>
  <div class="admin-container">
    <!-- Login -->
    <div v-if="!auth" class="login-wrapper">
      <div class="glass-panel login-card">
        <div class="login-icon">🏛️</div>
        <h2>Panel Administrativo IEE</h2>
        <p>Acceso exclusivo para personal autorizado del Instituto.</p>
        <div class="form-group">
          <label>Usuario</label>
          <input v-model="user" type="text" class="form-input" placeholder="Ej. IEE1" @keyup.enter="login">
        </div>
        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="pwd" type="password" class="form-input" placeholder="Contraseña" @keyup.enter="login">
        </div>
        <button @click="login" class="btn btn-primary w-full">Ingresar al Sistema</button>
        <p v-if="loginError" class="login-error">{{ loginError }}</p>
      </div>
    </div>

    <!-- Dashboard -->
    <div v-else class="dashboard">
      <div class="dashboard-header">
        <div>
          <h2>Panel de Administración</h2>
          <p class="header-sub">Gestión de propuestas y monitoreo de votación</p>
        </div>
        <button @click="logout" class="btn btn-outline">Cerrar Sesión</button>
      </div>

      <div class="dashboard-grid">
        <!-- Settings -->
        <div class="settings-col">
          <div class="glass-panel card">
            <h3>⚙️ Configuración</h3>
            <label>Fecha límite de votación</label>
            <input type="datetime-local" v-model="s.dl" class="form-input">
          </div>

          <div class="glass-panel card">
            <h3>👤 Administradores</h3>
            <div class="form-group">
              <label>Nuevo usuario</label>
              <input v-model="newUser" type="text" class="form-input" placeholder="Ej. IEE2">
            </div>
            <div class="form-group">
              <label>Contraseña</label>
              <input v-model="newPwd" type="password" class="form-input" placeholder="Mínimo 4 caracteres">
            </div>
            <button @click="createUser" class="btn btn-primary w-full" :disabled="!newUser || !newPwd || newPwd.length < 4">Crear administrador</button>
            <p v-if="pwdMsg" :class="['msg', pwdMsg.includes('ya existe') ? 'msg-error' : 'msg-success']">{{ pwdMsg }}</p>
          </div>
        </div>

        <!-- Proposals -->
        <div class="proposals-col">
          <div class="section-title-row">
            <h3>📋 Propuestas Pendientes</h3>
            <span class="badge-count" v-if="pending.length">{{ pending.length }}</span>
          </div>

          <transition-group name="fade" tag="div" class="proposals-list">
            <div v-for="p in pending" :key="p.id" class="glass-panel proposal-item">
              <h4>{{ p.titulo }}</h4>
              <p>{{ p.descripcion }}</p>
              <div class="proposal-meta">
                <span>📍 {{ p.municipio }}</span>
                <span>💰 {{ p.costo }}</span>
              </div>
              <div class="proposal-actions">
                <button @click="p.status='approved'" class="btn btn-primary btn-sm">✓ Aprobar</button>
                <button @click="p.status='rejected'" class="btn btn-outline btn-sm" style="color:var(--danger);border-color:var(--panel-border);">✕ Rechazar</button>
              </div>
            </div>
          </transition-group>

          <div v-if="!pending.length" class="glass-panel empty-card">
            <div class="empty-icon">🎉</div>
            <p>No hay propuestas pendientes</p>
          </div>
        </div>
      </div>

      <!-- Live Chart -->
      <LiveResultsChart process-id="proceso_2025" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useUrnaStore } from '../stores/useUrnaStore';
import LiveResultsChart from '../components/admin/LiveResultsChart.vue'

const s = useUrnaStore();
const user = ref('');
const pwd = ref('');
const newUser = ref('');
const newPwd = ref('');
const loginError = ref('');
const pwdMsg = ref('');
const auth = ref(localStorage.getItem('auth')==='1');

let adminUsers = JSON.parse(localStorage.getItem('admin_users') || '[]');
if (adminUsers.length === 0) {
  adminUsers = [{ username: 'IEE1', password: '1234' }];
  localStorage.setItem('admin_users', JSON.stringify(adminUsers));
}

const pending = computed(() => s.props.filter((x:any) => x.status==='pending'));

const login = () => {
  loginError.value = '';
  const users = JSON.parse(localStorage.getItem('admin_users') || '[]');
  const validUser = users.find((u:any) => u.username === user.value && u.password === pwd.value);
  if(validUser){
    auth.value=true;
    localStorage.setItem('auth','1');
  } else {
    loginError.value = 'Usuario o contraseña incorrectos';
  }
};

const logout = () => {
  auth.value = false;
  localStorage.removeItem('auth');
  user.value = '';
  pwd.value = '';
};

const createUser = () => {
  if (newUser.value && newPwd.value.length >= 4) {
    const users = JSON.parse(localStorage.getItem('admin_users') || '[]');
    if (users.find((u:any) => u.username === newUser.value)) {
      pwdMsg.value = 'El usuario ya existe.';
      return;
    }
    users.push({ username: newUser.value, password: newPwd.value });
    localStorage.setItem('admin_users', JSON.stringify(users));
    pwdMsg.value = `Usuario ${newUser.value} creado exitosamente.`;
    newUser.value = '';
    newPwd.value = '';
    setTimeout(() => pwdMsg.value = '', 4000);
  }
};
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
.login-card h2 { font-size: 1.4rem; font-weight: 800; }
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
.dashboard-header h2 { font-size: 1.5rem; font-weight: 800; }
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
.card h3 {
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
.section-title-row h3 { font-size: 1.1rem; font-weight: 700; }
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
.proposal-item h4 { color: var(--primary); font-size: 1.05rem; font-weight: 700; }
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
