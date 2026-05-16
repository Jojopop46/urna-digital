<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero-section">
      <div class="glass-panel hero-card">
        <div class="hero-badge">🔒 Seguro · Transparente · Accesible</div>
        <h1>{{ $t('home.title') }}</h1>
        <p class="hero-subtitle">{{ $t('home.subtitle') }}</p>
        <div class="hero-actions">
          <router-link to="/urna" class="btn btn-primary hero-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            {{ $t('home.vote') }}
          </router-link>
          <router-link to="/transparencia" class="btn btn-outline hero-btn">
            {{ $t('home.results') }}
          </router-link>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features-section">
      <div class="features-grid">
        <div class="glass-panel feature-card">
          <div class="feature-icon" style="background: var(--primary-light); color: var(--primary);">🔐</div>
          <h3>Voto Anónimo</h3>
          <p>Tu identidad está protegida con tecnología de conocimiento cero. Nadie puede vincular tu voto contigo.</p>
        </div>
        <div class="glass-panel feature-card">
          <div class="feature-icon" style="background: var(--secondary-light); color: var(--secondary);">🌐</div>
          <h3>Transparencia Total</h3>
          <p>Cada voto se registra en una blockchain pública auditable. Puedes verificar tu voto cuando quieras.</p>
        </div>
        <div class="glass-panel feature-card">
          <div class="feature-icon" style="background: var(--warning-light); color: var(--warning);">📱</div>
          <h3>Funciona Sin Internet</h3>
          <p>En zonas rurales puedes preparar tu voto offline y emitirlo cuando recuperes conexión.</p>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="how-section">
      <h2 class="section-title">¿Cómo funciona?</h2>
      <div class="steps-row">
        <div class="step-item">
          <div class="step-num">1</div>
          <h4>Identifícate</h4>
          <p>Ingresa tu CURP y resuelve el CAPTCHA</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-num">2</div>
          <h4>Elige</h4>
          <p>Selecciona la propuesta que más te convenga</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-num">3</div>
          <h4>Confirma</h4>
          <p>Revisa tu selección y emite tu voto</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-num">4</div>
          <h4>Verifica</h4>
          <p>Guarda tu recibo y comprueba en la blockchain</p>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="glass-panel cta-card">
        <h2>Tu voto cuenta</h2>
        <p>Participa en la construcción de un Chihuahua más democrático y transparente.</p>
        <router-link to="/urna" class="btn btn-primary">Comenzar a Votar</router-link>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home { display: flex; flex-direction: column; gap: 2.5rem; }

/* Hero */
.hero-section { text-align: center; }
.hero-card {
  padding: 3.5rem 2rem;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--primary-light);
  color: var(--primary);
  padding: 0.375rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}
.hero-card h1 {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  color: var(--primary);
  line-height: 1.15;
  letter-spacing: -0.02em;
}
.hero-subtitle {
  font-size: clamp(1.05rem, 2.5vw, 1.25rem);
  color: var(--text-muted);
  max-width: 600px;
  line-height: 1.6;
}
.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.5rem;
}
.hero-btn {
  min-width: 180px;
  padding: 1rem 2rem;
  font-size: 1.05rem;
}

/* Features */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}
.feature-card {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: center;
}
.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto;
}
.feature-card h3 {
  font-size: 1.15rem;
  font-weight: 700;
}
.feature-card p {
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.6;
}

/* How it works */
.how-section { text-align: center; }
.section-title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 800;
  margin-bottom: 2rem;
  color: var(--text-main);
}
.steps-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  max-width: 160px;
  text-align: center;
}
.step-num {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}
.step-item h4 {
  font-weight: 700;
  font-size: 1rem;
}
.step-item p {
  font-size: 0.85rem;
  color: var(--text-muted);
}
.step-arrow {
  font-size: 1.5rem;
  color: var(--primary);
  font-weight: 700;
}
@media (max-width: 768px) {
  .step-arrow { display: none; }
  .steps-row { gap: 1.5rem; }
}

/* CTA */
.cta-card {
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--panel-bg) 100%);
  border-color: var(--primary);
}
.cta-card h2 {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--primary);
}
.cta-card p {
  color: var(--text-muted);
  max-width: 500px;
}
</style>
