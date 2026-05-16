<template>
  <div class="admin-dashboard" style="max-width:1000px;margin:0 auto;padding:2rem;">
    <!-- Login Section -->
    <div v-if="!auth" class="glass-panel login-card">
      <div style="text-align:center;margin-bottom:2rem;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>
        <h2 style="margin-top:1rem;">Acceso Administrativo IEE</h2>
      </div>
      <div class="form-group" style="margin-bottom:1rem;">
        <label>Usuario</label>
        <input v-model="user" type="text" class="form-input" placeholder="Ej. IEE1" @keyup.enter="login">
      </div>
      <div class="form-group" style="margin-bottom:1.5rem;">
        <label>Contraseña</label>
        <input v-model="pwd" type="password" class="form-input" placeholder="Contraseña" @keyup.enter="login">
      </div>
      <button @click="login" class="btn btn-primary w-full">Ingresar al Sistema</button>
      <p v-if="loginError" style="color:var(--danger);margin-top:1rem;text-align:center;font-weight:600;">{{ loginError }}</p>
    </div>

    <!-- Admin Dashboard -->
    <div v-else>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem;flex-wrap:wrap;gap:1rem;">
        <h2>Panel de Administración IEE</h2>
        <button @click="logout" class="btn btn-outline" style="padding:0.5rem 1rem;">Cerrar Sesión</button>
      </div>

      <div class="dashboard-grid">
        <!-- Settings Column -->
        <div class="settings-col">
          <div class="glass-panel" style="padding:1.5rem;margin-bottom:1.5rem;">
            <h3 style="margin-bottom:1rem;font-size:1.1rem;">Configuración de Votación</h3>
            <label style="font-size:0.9rem;">Fecha Límite Votación:</label>
            <input type="datetime-local" v-model="s.dl" class="form-input" style="margin-top:0.5rem;">
          </div>

          <div class="glass-panel" style="padding:1.5rem;">
            <h3 style="margin-bottom:1rem;font-size:1.1rem;">Gestión de Administradores</h3>
            <div class="form-group" style="margin-bottom:1rem;">
              <label style="font-size:0.9rem;">Nuevo Usuario</label>
              <input v-model="newUser" type="text" class="form-input" style="margin-top:0.5rem;" placeholder="Ej. IEE2">
            </div>
            <div class="form-group" style="margin-bottom:1rem;">
              <label style="font-size:0.9rem;">Contraseña de Usuario</label>
              <input v-model="newPwd" type="password" class="form-input" style="margin-top:0.5rem;" placeholder="Mínimo 4 caracteres">
            </div>
            <button @click="createUser" class="btn btn-primary w-full" :disabled="!newUser || !newPwd || newPwd.length < 4">Añadir Administrador</button>
            <p v-if="pwdMsg" style="color:var(--success);margin-top:0.5rem;font-size:0.9rem;font-weight:600;">{{ pwdMsg }}</p>
          </div>
        </div>

        <!-- Proposals Column -->
        <div class="proposals-col">
          <h3 style="margin-bottom:1rem;">Propuestas Pendientes de Aprobación</h3>
          <transition-group name="fade" tag="div" style="display:flex;flex-direction:column;gap:1rem;">
            <div v-for="p in pending" :key="p.id" class="glass-panel" style="padding:1.5rem;display:flex;flex-direction:column;">
              <h4 style="color:var(--primary);margin-bottom:0.5rem;font-size:1.1rem;">{{p.titulo}}</h4>
              <p style="color:var(--text-muted);font-size:0.95rem;margin-bottom:1rem;line-height:1.5;">{{p.descripcion}}</p>
              <div style="display:flex;gap:0.5rem;margin-top:auto;">
                <button @click="p.status='approved'" class="btn btn-primary" style="flex:1;">Aprobar</button>
                <button @click="p.status='rejected'" class="btn btn-outline" style="flex:1;color:var(--danger);border-color:var(--panel-border);">Rechazar</button>
              </div>
            </div>
          </transition-group>
          <div v-if="!pending.length" class="glass-panel" style="padding:2rem;text-align:center;color:var(--text-muted);">
            No hay propuestas pendientes para revisar.
          </div>
        </div>
      </div>

      <!-- Live Results Chart -->
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

// Setup credentials if not exist
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
.login-card { max-width:400px; margin:4rem auto; padding:2.5rem; }
@media (max-width: 768px) { .login-card { margin: 2rem auto; padding: 1.5rem; } }
.form-input { width:100%; padding:0.8rem 1rem; border:1px solid var(--panel-border); border-radius:6px; background:transparent; color:var(--text-main); transition:all 0.2s; font-family:inherit; }
.form-input:focus { outline:none; border-color:var(--primary); box-shadow:0 0 0 3px rgba(0, 91, 171, 0.15); }
.dashboard-grid { display:grid; grid-template-columns:300px 1fr; gap:2rem; align-items:start; }
@media (max-width:768px) { .dashboard-grid { grid-template-columns:1fr; } }
label { display:block; margin-bottom:0.3rem; font-weight:600; color:var(--text-main); }
.w-full { width:100%; }
</style>
