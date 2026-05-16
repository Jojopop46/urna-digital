# 🗳️ Voz ciudadana — Guía de Mejoras para Hackathon

> **Audiencia:** IA implementadora (Copilot, Claude, Cursor, GPT-4).
> **Formato:** Cada mejora es autónoma. Sigue las instrucciones en el orden indicado sin saltarte pasos.
> **Stack base:** Vue.js 3 + Vite + TypeScript (frontend) · Python + FastAPI (backend) · PostgreSQL 16 · Redis 7 · Docker Compose.

---

## ÍNDICE DE MEJORAS

| # | Mejora | Impacto | Dificultad | Tiempo estimado |
|---|--------|---------|------------|-----------------|
| 1 | ZK-Proofs ligeros (anonimato verificable) | 🔴 Crítico | Alta | 4–6 h |
| 2 | PWA Offline-First | 🟠 Alto | Media | 2–3 h |
| 3 | OTP por SMS/WhatsApp (2FA ciudadano) | 🟠 Alto | Media | 2–3 h |
| 4 | Detección de anomalías con IA (FastAPI + sklearn) | 🟠 Alto | Alta | 4–5 h |
| 5 | Soporte multilingüe (Rarámuri + Español + accesible) | 🟡 Medio | Baja | 1–2 h |
| 6 | Dashboard de resultados en tiempo real (WebSocket + D3) | 🟠 Alto | Media | 3–4 h |
| 7 | Merkle Tree auditablе (reemplaza SHA-256 lineal) | 🔴 Crítico | Alta | 3–4 h |
| 8 | Verificación de recibo con cámara (QR scan nativo) | 🟡 Medio | Baja | 1–2 h |

---

---

## MEJORA 1 — ZK-Proofs Ligeros (Anonimato Verificable)

### ¿Por qué?
El sistema actual hashea la identidad con `SHA256(salt + CURP)`. Esto es bueno pero no **prueba** que el voto fue contado sin revelar quién votó. Con Zero-Knowledge Proofs el ciudadano puede demostrar matemáticamente que emitió un voto válido sin revelar su identidad.

### Implementación paso a paso

#### Paso 1 — Instalar dependencia Python
```bash
# En el contenedor backend (requirements.txt)
pip install py_ecc==6.0.0
# py_ecc incluye BN128 curve usada por zk-SNARKs ligeros
```

#### Paso 2 — Crear módulo `zk_commitment.py` en el backend
```python
# backend/crypto/zk_commitment.py
"""
Compromiso de Pedersen simplificado sobre BN128.
El ciudadano genera un 'commitment' C = r*G + vote*H
donde r es un nonce secreto, vote es 0 o 1, G y H son puntos del grupo.
El backend verifica el commitment SIN conocer r ni vote individualmente.
"""
import secrets
from py_ecc.bn128 import G1, multiply, add, neg, curve_order, is_on_curve

def generate_commitment(vote_index: int, num_options: int) -> dict:
    """
    vote_index: índice de la opción seleccionada (0-based)
    Retorna: {commitment_hex, nullifier_hex, proof_data}
    """
    if vote_index < 0 or vote_index >= num_options:
        raise ValueError("Índice de voto fuera de rango")

    # Nonce secreto del ciudadano (nunca sale del frontend en producción)
    r = secrets.randbelow(curve_order)

    # Punto H = hash-to-point del string "URNA_DIGITAL_CHI_2025"
    # (simplificado: usamos multiply(G1, hash_value))
    H_scalar = int.from_bytes(b"URNA_DIGITAL_CHI_2025", "big") % curve_order
    H = multiply(G1, H_scalar)

    # Commitment: C = r*G + vote_index*H
    C = add(multiply(G1, r), multiply(H, vote_index))

    # Nullifier: evita doble voto sin revelar identidad
    # nullifier = SHA256(r || process_id)  — se guarda en BD, no la CURP
    import hashlib
    nullifier = hashlib.sha256(
        r.to_bytes(32, "big") + b"proceso_2025"
    ).hexdigest()

    return {
        "commitment": (hex(C[0]), hex(C[1])),  # Punto de la curva
        "nullifier": nullifier,
        "r_secret": hex(r),  # Solo para el recibo del ciudadano; NUNCA persiste en BD
    }


def verify_commitment(commitment_tuple: tuple, nullifier: str) -> bool:
    """
    Verifica que el commitment es un punto válido en BN128.
    El nullifier se busca en Redis para prevenir doble voto.
    """
    x = int(commitment_tuple[0], 16)
    y = int(commitment_tuple[1], 16)
    point = (x % curve_order, y % curve_order)
    return is_on_curve(point, b2=3)  # BN128: y²=x³+3
```

#### Paso 3 — Nuevo endpoint FastAPI `/api/v1/vote/commit`
```python
# backend/routers/vote.py  (agregar endpoint)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from crypto.zk_commitment import generate_commitment, verify_commitment
import redis.asyncio as aioredis

router = APIRouter(prefix="/api/v1/vote")

class CommitRequest(BaseModel):
    process_id: str
    vote_index: int
    num_options: int
    identity_hash: str  # SHA256(salt+CURP) — identidad ya anonimizada

class CommitResponse(BaseModel):
    commitment_x: str
    commitment_y: str
    nullifier: str
    receipt_token: str  # JWT firmado con el commitment para el recibo PDF

@router.post("/commit", response_model=CommitResponse)
async def commit_vote(body: CommitRequest, redis: aioredis.Redis = Depends(get_redis)):
    # 1. Verificar que el nullifier no exista (previene doble voto)
    existing = await redis.get(f"nullifier:{body.identity_hash}")
    if existing:
        raise HTTPException(status_code=409, detail="Voto ya emitido para este proceso.")

    # 2. Generar commitment ZK
    zk = generate_commitment(body.vote_index, body.num_options)

    # 3. Guardar SOLO el nullifier en Redis (TTL = duración del proceso)
    await redis.setex(
        f"nullifier:{body.identity_hash}",
        86400 * 3,  # 3 días
        zk["nullifier"]
    )

    # 4. Minar en blockchain (el voto es el commitment, no el índice plano)
    await mine_to_chain(zk["commitment"], body.process_id)

    return CommitResponse(
        commitment_x=zk["commitment"][0],
        commitment_y=zk["commitment"][1],
        nullifier=zk["nullifier"],
        receipt_token=generate_receipt_jwt(zk["nullifier"])
    )
```

#### Paso 4 — Ajuste en frontend Vue.js
```typescript
// src/stores/voting.ts  (Pinia store)
import { defineStore } from 'pinia'

interface ZKCommitment {
  commitment_x: string
  commitment_y: string
  nullifier: string
  receipt_token: string
}

export const useVotingStore = defineStore('voting', {
  state: () => ({
    commitment: null as ZKCommitment | null,
    step: 'identity' as 'identity' | 'selection' | 'confirmation' | 'receipt'
  }),
  actions: {
    async submitVote(processId: string, voteIndex: number, numOptions: number, identityHash: string) {
      const res = await fetch('/api/v1/vote/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ process_id: processId, vote_index: voteIndex, num_options: numOptions, identity_hash: identityHash })
      })
      if (!res.ok) throw new Error(await res.text())
      this.commitment = await res.json()
      this.step = 'receipt'
    }
  }
})
```

#### Paso 5 — Prueba de integración
```bash
# Desde la raíz del proyecto
pytest backend/tests/test_zk_commitment.py -v
# El test debe verificar:
# 1. Commitment válido en BN128 ✓
# 2. Doble envío retorna 409 ✓
# 3. Nullifier distinto para cada proceso ✓
```

---

---

## MEJORA 2 — PWA Offline-First

### ¿Por qué?
En municipios rurales de Chihuahua (Sierra Tarahumara) la conectividad es intermitente. El ciudadano debe poder avanzar hasta la pantalla de confirmación sin internet y solo necesitar conexión en el momento de emitir el voto.

### Implementación paso a paso

#### Paso 1 — Instalar Vite PWA Plugin
```bash
cd frontend
npm install -D vite-plugin-pwa workbox-window
```

#### Paso 2 — Configurar `vite.config.ts`
```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        // Cachear assets estáticos (JS, CSS, fuentes)
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        // Estrategia: primero cache para assets, network para API
        runtimeCaching: [
          {
            urlPattern: /^\/api\/v1\/proceso\//,
            handler: 'CacheFirst',
            options: {
              cacheName: 'proceso-data',
              expiration: { maxAgeSeconds: 60 * 60 * 24 }  // 24h
            }
          },
          {
            urlPattern: /^\/api\/v1\/vote\//,
            handler: 'NetworkOnly'  // Los votos SIEMPRE por red
          }
        ]
      },
      manifest: {
        name: 'Voz ciudadana',
        short_name: 'UrnaDigital',
        description: 'Plataforma de participación ciudadana',
        theme_color: '#1a237e',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      }
    })
  ]
})
```

#### Paso 3 — Componente banner de estado de red
```vue
<!-- src/components/NetworkStatus.vue -->
<template>
  <Transition name="slide-down">
    <div v-if="!isOnline" class="network-banner" role="alert" aria-live="assertive">
      <span>⚠️ Sin conexión — Tu selección está guardada. Conéctate para emitir tu voto.</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isOnline = ref(navigator.onLine)

const handleOnline = () => { isOnline.value = true }
const handleOffline = () => { isOnline.value = false }

onMounted(() => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})
onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script>

<style scoped>
.network-banner {
  position: fixed; top: 0; left: 0; right: 0;
  background: #f59e0b; color: #1c1917;
  padding: 0.75rem 1rem; text-align: center;
  font-weight: 600; z-index: 9999;
}
.slide-down-enter-active, .slide-down-leave-active { transition: transform 0.3s ease; }
.slide-down-enter-from, .slide-down-leave-to { transform: translateY(-100%); }
</style>
```

#### Paso 4 — Bloquear botón "Emitir" si no hay red
```typescript
// En el componente de Confirmación (ConfirmStep.vue)
import { useOnline } from '@vueuse/core'

const isOnline = useOnline()
// En el template:
// <button :disabled="!isOnline" @click="submitVote">Confirmar y emitir</button>
// <p v-if="!isOnline" class="sr-only" aria-live="polite">
//   Necesitas conexión a internet para emitir tu voto
// </p>
```

---

---

## MEJORA 3 — OTP por SMS/WhatsApp (Segundo Factor)

### ¿Por qué?
La validación actual (INE/CURP) es un solo factor. Agregar un OTP de 6 dígitos enviado al número de celular registrado en el padrón blinda contra suplantación de identidad.

### Implementación paso a paso

#### Paso 1 — Instalar Twilio SDK
```bash
# backend/requirements.txt — agregar:
twilio==8.12.0
```

#### Paso 2 — Servicio OTP en Python
```python
# backend/services/otp_service.py
import secrets
import hashlib
from datetime import timedelta
from twilio.rest import Client as TwilioClient
import redis.asyncio as aioredis

TWILIO_SID = "ACxxx"       # Variable de entorno
TWILIO_TOKEN = "xxxxx"     # Variable de entorno
TWILIO_FROM = "+1800XXXXXX" # Número Twilio

async def send_otp(phone_number: str, process_id: str, redis: aioredis.Redis) -> str:
    """Genera, almacena y envía OTP de 6 dígitos. Retorna el hash para verificación."""
    otp = str(secrets.randbelow(900000) + 100000)  # 100000–999999
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    # Almacenar hash en Redis con TTL de 5 minutos
    key = f"otp:{process_id}:{phone_number}"
    await redis.setex(key, 300, otp_hash)

    # Enviar por SMS (cambiar a WhatsApp con "whatsapp:+52..." como from_)
    client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        to=phone_number,
        from_=TWILIO_FROM,
        body=f"Tu código de verificación Voz ciudadana: {otp}\nVálido 5 minutos. No lo compartas."
    )
    return otp_hash  # Solo para testing; en producción no retornar

async def verify_otp(phone_number: str, process_id: str, otp_input: str, redis: aioredis.Redis) -> bool:
    """Verifica OTP. Elimina la clave tras un intento exitoso (OTP de un solo uso)."""
    key = f"otp:{process_id}:{phone_number}"
    stored_hash = await redis.get(key)
    if not stored_hash:
        return False  # Expirado o inexistente
    input_hash = hashlib.sha256(otp_input.encode()).hexdigest()
    if input_hash == stored_hash:
        await redis.delete(key)  # Invalidar OTP tras uso
        return True
    return False
```

#### Paso 3 — Endpoints FastAPI
```python
# backend/routers/auth.py
from pydantic import BaseModel, constr
from services.otp_service import send_otp, verify_otp

class OTPRequest(BaseModel):
    curp: str
    phone_last4: str  # Solo últimos 4 dígitos para UX; el número real viene del padrón
    process_id: str

class OTPVerify(BaseModel):
    process_id: str
    identity_hash: str
    otp_code: constr(min_length=6, max_length=6)

@router.post("/auth/send-otp")
async def request_otp(body: OTPRequest, redis = Depends(get_redis)):
    # Obtener número completo del padrón (PostgreSQL) validando CURP
    phone = await db.get_phone_by_curp(body.curp)
    if not phone or not phone.endswith(body.phone_last4):
        raise HTTPException(400, "Datos no coinciden con el padrón.")
    await send_otp(phone, body.process_id, redis)
    return {"message": "Código enviado.", "masked_phone": f"***-***-{body.phone_last4}"}

@router.post("/auth/verify-otp")
async def verify(body: OTPVerify, redis = Depends(get_redis)):
    phone = await db.get_phone_by_identity_hash(body.identity_hash)
    ok = await verify_otp(phone, body.process_id, body.otp_code, redis)
    if not ok:
        raise HTTPException(401, "Código incorrecto o expirado.")
    # Generar JWT de sesión de votación (exp: 30 min)
    token = generate_voting_jwt(body.identity_hash, body.process_id)
    return {"voting_token": token}
```

#### Paso 4 — Paso adicional en el Wizard (Vue.js)
```typescript
// src/router/index.ts — agregar ruta intermedia
{ path: '/verificar-otp', name: 'OTPStep', component: () => import('@/views/OTPStep.vue') }

// src/views/OTPStep.vue — componente mínimo
// Input de 6 dígitos → llama a POST /auth/verify-otp
// Si OK → router.push('/seleccion')
// Si falla → mostrar error con aria-live="assertive"
```

---

---

## MEJORA 4 — Detección de Anomalías con IA

### ¿Por qué?
Un flujo de votos normal sigue patrones estadísticos predecibles. Picos repentinos desde rangos de IP, concentración geográfica anómala o cadencias de voto imposiblemente rápidas indican ataques o fraude automatizado.

### Implementación paso a paso

#### Paso 1 — Instalar dependencias
```bash
# backend/requirements.txt
scikit-learn==1.4.2
numpy==1.26.4
pandas==2.2.2
```

#### Paso 2 — Modelo de detección (Isolation Forest)
```python
# backend/services/anomaly_detector.py
"""
Isolation Forest para detección de anomalías en tiempo real.
Features por ventana de 60 segundos:
  - votes_per_minute: tasa de votos
  - unique_ips: cantidad de IPs distintas
  - avg_time_between_votes: tiempo promedio entre votos (segundos)
  - top_ip_concentration: % de votos desde la IP más activa
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

MODEL_PATH = "models/anomaly_model.pkl"
SCALER_PATH = "models/anomaly_scaler.pkl"

def train_baseline_model():
    """
    Entrena con datos sintéticos de comportamiento normal.
    En producción: reemplazar con datos históricos reales.
    """
    np.random.seed(42)
    n_normal = 1000
    # Comportamiento normal: 10–80 votos/min, 8–60 IPs únicas, etc.
    X_normal = np.column_stack([
        np.random.randint(10, 80, n_normal),      # votes_per_minute
        np.random.randint(8, 60, n_normal),        # unique_ips
        np.random.uniform(1.5, 8.0, n_normal),     # avg_time_between_votes
        np.random.uniform(0.02, 0.15, n_normal),   # top_ip_concentration
    ])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_normal)
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_scaled)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    return model, scaler

def detect_anomaly(features: dict) -> dict:
    """
    features: {votes_per_minute, unique_ips, avg_time_between_votes, top_ip_concentration}
    Retorna: {is_anomaly: bool, score: float, severity: str}
    """
    if not os.path.exists(MODEL_PATH):
        train_baseline_model()
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    X = np.array([[
        features["votes_per_minute"],
        features["unique_ips"],
        features["avg_time_between_votes"],
        features["top_ip_concentration"]
    ]])
    X_scaled = scaler.transform(X)
    score = model.decision_function(X_scaled)[0]
    prediction = model.predict(X_scaled)[0]  # -1 = anomalía, 1 = normal
    is_anomaly = prediction == -1
    severity = "critical" if score < -0.3 else "warning" if score < -0.1 else "normal"
    return {"is_anomaly": is_anomaly, "score": float(score), "severity": severity}
```

#### Paso 3 — Tarea periódica con Redis (cada 60s)
```python
# backend/tasks/anomaly_task.py
import asyncio
from services.anomaly_detector import detect_anomaly
from services.websocket_manager import broadcast_alert

async def run_anomaly_check(redis, process_id: str):
    """Corre cada 60 segundos durante el proceso activo."""
    while True:
        await asyncio.sleep(60)
        # Recopilar métricas de la ventana actual desde Redis
        votes_count = int(await redis.get(f"stats:{process_id}:votes_last_min") or 0)
        unique_ips = int(await redis.scard(f"stats:{process_id}:ips_last_min") or 0)
        avg_time = float(await redis.get(f"stats:{process_id}:avg_time") or 3.0)
        top_ip_votes = int(await redis.get(f"stats:{process_id}:top_ip_votes") or 0)
        top_concentration = (top_ip_votes / votes_count) if votes_count > 0 else 0

        result = detect_anomaly({
            "votes_per_minute": votes_count,
            "unique_ips": unique_ips,
            "avg_time_between_votes": avg_time,
            "top_ip_concentration": top_concentration
        })

        if result["is_anomaly"]:
            # Emitir alerta por WebSocket al panel de administración
            await broadcast_alert({
                "type": "ANOMALY_DETECTED",
                "severity": result["severity"],
                "score": result["score"],
                "process_id": process_id,
                "timestamp": asyncio.get_event_loop().time()
            })
        # Resetear ventana
        await redis.delete(f"stats:{process_id}:votes_last_min")
        await redis.delete(f"stats:{process_id}:ips_last_min")
```

#### Paso 4 — Alerta visual en panel admin (Vue.js)
```vue
<!-- src/components/admin/AnomalyAlert.vue -->
<template>
  <div v-if="alert" :class="['alert-banner', `alert-${alert.severity}`]" role="alert" aria-live="assertive">
    <strong>⚠️ Anomalía detectada</strong> — Score: {{ alert.score.toFixed(3) }}
    <button @click="dismissAlert">Descartar</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const alert = ref(null)
const ws = new WebSocket('/ws/audit')
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data)
  if (msg.type === 'ANOMALY_DETECTED') alert.value = msg
}
const dismissAlert = () => { alert.value = null }
</script>
```

---

---

## MEJORA 5 — Soporte Multilingüe (Rarámuri + Español Fácil)

### ¿Por qué?
Chihuahua tiene la mayor población indígena de México (Rarámuri/Tarahumara). Un sistema de votación que no habla su idioma viola su derecho a la participación.

### Implementación paso a paso

#### Paso 1 — Instalar vue-i18n
```bash
cd frontend
npm install vue-i18n@9
```

#### Paso 2 — Crear archivos de traducción
```
frontend/src/locales/
├── es.json          # Español estándar
├── es-easy.json     # Español Lectura Fácil
└── rar.json         # Rarámuri (Tarahumara)
```

```json
// src/locales/es.json
{
  "identity": {
    "title": "Ingresa tu credencial",
    "curp_label": "CURP o Clave Electoral (INE)",
    "submit": "Continuar"
  },
  "confirmation": {
    "title": "Confirma tu voto",
    "warning": "Esta acción no puede deshacerse.",
    "submit": "Confirmar y emitir voto"
  },
  "receipt": {
    "title": "¡Tu voto fue registrado!",
    "download": "Descargar recibo PDF"
  }
}
```

```json
// src/locales/es-easy.json  (Lectura Fácil — frases cortas, palabras simples)
{
  "identity": {
    "title": "Escribe tu número de credencial",
    "curp_label": "Tu CURP o número de la credencial de elector",
    "submit": "Siguiente"
  },
  "confirmation": {
    "title": "¿Es tu voto?",
    "warning": "Revisa bien. No podrás cambiar tu voto.",
    "submit": "Sí, este es mi voto"
  },
  "receipt": {
    "title": "¡Votaste!",
    "download": "Guarda tu comprobante"
  }
}
```

```json
// src/locales/rar.json  (Rarámuri — frases básicas, colaborar con hablantes nativos)
{
  "identity": {
    "title": "Anéguame nasí repá sihurúame",
    "curp_label": "CURP ó INE repási",
    "submit": "Mapu"
  },
  "confirmation": {
    "title": "¿Né repá nakí?",
    "warning": "Jiká repá kití simí.",
    "submit": "Eé, né repá"
  },
  "receipt": {
    "title": "¡Repá simí!",
    "download": "Repá PDF simí"
  }
}
```

#### Paso 3 — Configurar i18n en `main.ts`
```typescript
// frontend/src/main.ts
import { createI18n } from 'vue-i18n'
import es from './locales/es.json'
import esEasy from './locales/es-easy.json'
import rar from './locales/rar.json'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'es',
  fallbackLocale: 'es',
  messages: { es, 'es-easy': esEasy, rar }
})

app.use(i18n)
```

#### Paso 4 — Selector de idioma accesible
```vue
<!-- src/components/LanguageSwitcher.vue -->
<template>
  <div class="lang-switcher" role="navigation" aria-label="Seleccionar idioma">
    <button
      v-for="lang in langs"
      :key="lang.code"
      :aria-pressed="locale === lang.code"
      :aria-label="`Cambiar idioma a ${lang.name}`"
      @click="setLang(lang.code)"
    >{{ lang.label }}</button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()
const langs = [
  { code: 'es', label: 'Español', name: 'Español estándar' },
  { code: 'es-easy', label: 'Fácil', name: 'Español fácil de leer' },
  { code: 'rar', label: 'Rarámuri', name: 'Idioma Rarámuri' }
]
const setLang = (code: string) => {
  locale.value = code
  localStorage.setItem('lang', code)
}
</script>
```

---

---

## MEJORA 6 — Dashboard de Resultados en Tiempo Real

### ¿Por qué?
El panel administrativo actual solo muestra logs. Visualizar el flujo de votos en un gráfico en tiempo real mejora la confianza pública y la capacidad de respuesta del IEE.

### Implementación paso a paso

#### Paso 1 — Instalar D3.js
```bash
cd frontend
npm install d3@7
```

#### Paso 2 — Componente `LiveResultsChart.vue`
```vue
<!-- src/components/admin/LiveResultsChart.vue -->
<template>
  <div class="chart-container" aria-label="Gráfica de resultados en tiempo real">
    <h2>Resultados en vivo — Proceso {{ processId }}</h2>
    <svg ref="svgRef" :width="width" :height="height" role="img" :aria-label="ariaLabel" />
    <p class="sr-only" aria-live="polite">{{ ariaLabel }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps<{ processId: string }>()
const svgRef = ref<SVGSVGElement | null>(null)
const width = 700; const height = 400
const margin = { top: 20, right: 30, bottom: 40, left: 60 }

interface VoteData { option: string; count: number }
const data = ref<VoteData[]>([])
const ariaLabel = ref('Sin datos aún.')

// Conectar WebSocket para actualizaciones
const ws = new WebSocket(`/ws/results/${props.processId}`)
ws.onmessage = (e) => {
  data.value = JSON.parse(e.data)
  renderChart()
}

function renderChart() {
  if (!svgRef.value || !data.value.length) return
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  const x = d3.scaleBand()
    .domain(data.value.map(d => d.option))
    .range([margin.left, width - margin.right])
    .padding(0.3)

  const y = d3.scaleLinear()
    .domain([0, d3.max(data.value, d => d.count) ?? 10])
    .nice()
    .range([height - margin.bottom, margin.top])

  // Barras
  svg.append('g').selectAll('rect')
    .data(data.value).join('rect')
    .attr('x', d => x(d.option)!)
    .attr('y', d => y(d.count))
    .attr('height', d => y(0) - y(d.count))
    .attr('width', x.bandwidth())
    .attr('fill', '#3b82f6')
    .attr('rx', 4)

  // Ejes
  svg.append('g').attr('transform', `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x))
  svg.append('g').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(6))

  ariaLabel.value = data.value.map(d => `${d.option}: ${d.count} votos`).join(', ')
}

onMounted(renderChart)
</script>
```

#### Paso 3 — Endpoint WebSocket de resultados (FastAPI)
```python
# backend/routers/results_ws.py
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json

@router.websocket("/ws/results/{process_id}")
async def results_stream(websocket: WebSocket, process_id: str):
    await websocket.accept()
    try:
        while True:
            # Consultar conteos actuales desde PostgreSQL
            rows = await db.fetch(
                "SELECT option_label, COUNT(*) as count FROM votes "
                "WHERE process_id=$1 GROUP BY option_label ORDER BY option_label",
                process_id
            )
            payload = [{"option": r["option_label"], "count": r["count"]} for r in rows]
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(5)  # Actualizar cada 5 segundos
    except WebSocketDisconnect:
        pass
```

---

---

## MEJORA 7 — Merkle Tree Auditable (Reemplaza SHA-256 Lineal)

### ¿Por qué?
La blockchain lineal actual requiere recorrer toda la cadena para verificar un voto. Un Merkle Tree permite verificación logarítmica O(log n): el ciudadano solo necesita una "Merkle Proof" de ~10 hashes para demostrar que su voto está en el árbol con millones de votos.

### Implementación paso a paso

#### Paso 1 — Módulo `merkle_tree.py`
```python
# backend/crypto/merkle_tree.py
import hashlib
from typing import Optional

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

class MerkleTree:
    def __init__(self, leaves: list[str]):
        """leaves: lista de hashes de votos individuales."""
        if not leaves:
            raise ValueError("El árbol no puede estar vacío")
        # Si número impar, duplicar el último (estándar Bitcoin)
        self.leaves = leaves if len(leaves) % 2 == 0 else leaves + [leaves[-1]]
        self.tree = self._build()

    def _build(self) -> list[list[str]]:
        tree = [self.leaves[:]]
        while len(tree[-1]) > 1:
            level = tree[-1]
            next_level = []
            for i in range(0, len(level), 2):
                combined = sha256(level[i] + level[i + 1])
                next_level.append(combined)
            if len(next_level) % 2 != 0 and len(next_level) > 1:
                next_level.append(next_level[-1])
            tree.append(next_level)
        return tree

    @property
    def root(self) -> str:
        return self.tree[-1][0]

    def get_proof(self, leaf_index: int) -> list[dict]:
        """Genera la prueba de inclusión para el voto en leaf_index."""
        proof = []
        idx = leaf_index
        for level in self.tree[:-1]:
            sibling_idx = idx + 1 if idx % 2 == 0 else idx - 1
            sibling_idx = min(sibling_idx, len(level) - 1)
            direction = "right" if idx % 2 == 0 else "left"
            proof.append({"hash": level[sibling_idx], "direction": direction})
            idx //= 2
        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: list[dict], root: str) -> bool:
        """Verifica que leaf_hash pertenece al árbol con la raíz dada."""
        current = leaf_hash
        for step in proof:
            if step["direction"] == "right":
                current = sha256(current + step["hash"])
            else:
                current = sha256(step["hash"] + current)
        return current == root
```

#### Paso 2 — Integrar en el flujo de votación
```python
# backend/services/blockchain.py — modificar función mine_block
from crypto.merkle_tree import MerkleTree

async def finalize_process_merkle(process_id: str, db, redis):
    """Se llama al cerrar el proceso. Construye el Merkle Tree final."""
    # Obtener todos los hashes de voto del proceso
    rows = await db.fetch(
        "SELECT vote_hash FROM votes WHERE process_id=$1 ORDER BY created_at",
        process_id
    )
    leaf_hashes = [r["vote_hash"] for r in rows]
    tree = MerkleTree(leaf_hashes)

    # Guardar raíz en BD (firmada con HMAC para exportación)
    await db.execute(
        "UPDATE electoral_processes SET merkle_root=$1, finalized_at=NOW() WHERE id=$2",
        tree.root, process_id
    )

    # Guardar árbol completo en Redis para consultas rápidas de pruebas
    import json
    await redis.setex(
        f"merkle:{process_id}",
        86400 * 30,
        json.dumps({"root": tree.root, "tree": tree.tree})
    )
    return tree.root
```

#### Paso 3 — Endpoint de verificación con Merkle Proof
```python
@router.get("/transparencia/verificar/{vote_hash}")
async def verify_vote(vote_hash: str, process_id: str, redis = Depends(get_redis), db = Depends(get_db)):
    # Obtener índice del voto
    row = await db.fetchrow(
        "SELECT leaf_index FROM votes WHERE vote_hash=$1 AND process_id=$2",
        vote_hash, process_id
    )
    if not row:
        raise HTTPException(404, "Voto no encontrado.")

    # Reconstruir prueba desde Redis
    import json
    cached = await redis.get(f"merkle:{process_id}")
    if not cached:
        raise HTTPException(503, "Árbol Merkle no disponible aún.")

    merkle_data = json.loads(cached)
    tree = MerkleTree.__new__(MerkleTree)
    tree.tree = merkle_data["tree"]
    tree.leaves = tree.tree[0]
    proof = tree.get_proof(row["leaf_index"])

    is_valid = MerkleTree.verify_proof(vote_hash, proof, merkle_data["root"])
    return {
        "vote_hash": vote_hash,
        "merkle_root": merkle_data["root"],
        "proof": proof,
        "verified": is_valid,
        "message": "Voto verificado en el escrutinio oficial." if is_valid else "Hash no encontrado."
    }
```

---

---

## MEJORA 8 — Verificación de Recibo con Cámara (QR Scan Nativo)

### ¿Por qué?
Actualmente el ciudadano debe copiar y pegar el hash manualmente. Permitir escanear el QR del recibo directamente desde la plataforma de verificación hace la auditoría ciudadana accesible para cualquier persona.

### Implementación paso a paso

#### Paso 1 — Instalar librería QR
```bash
cd frontend
npm install @zxing/browser@0.1.4
```

#### Paso 2 — Componente `QRScanner.vue`
```vue
<!-- src/views/Transparencia/QRScanner.vue -->
<template>
  <div class="scanner-page">
    <h1>Verificar mi voto</h1>
    <p>Escanea el código QR de tu recibo o ingresa el hash manualmente.</p>

    <div class="scanner-actions">
      <button v-if="!scanning" @click="startScan" :aria-expanded="scanning">
        📷 Escanear QR con cámara
      </button>
      <button v-else @click="stopScan">Cancelar</button>
    </div>

    <video v-show="scanning" ref="videoRef" aria-label="Vista de cámara para escaneo QR" />

    <div class="manual-input">
      <label for="hashInput">O ingresa el hash de tu recibo:</label>
      <input id="hashInput" v-model="manualHash" type="text" placeholder="abc123..." />
      <button @click="verifyHash(manualHash)">Verificar</button>
    </div>

    <div v-if="result" :class="['result', result.verified ? 'success' : 'error']" role="status" aria-live="polite">
      <span v-if="result.verified">✅ Tu voto está incluido en el escrutinio oficial.</span>
      <span v-else>❌ Hash no encontrado. Contacta al IEE.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { BrowserQRCodeReader } from '@zxing/browser'

const videoRef = ref<HTMLVideoElement | null>(null)
const scanning = ref(false)
const manualHash = ref('')
const result = ref<{ verified: boolean } | null>(null)
let codeReader: BrowserQRCodeReader | null = null
let controls: { stop: () => void } | null = null

async function startScan() {
  scanning.value = true
  codeReader = new BrowserQRCodeReader()
  controls = await codeReader.decodeFromVideoDevice(undefined, videoRef.value!, (res, err) => {
    if (res) {
      verifyHash(res.getText())
      stopScan()
    }
  })
}

function stopScan() {
  controls?.stop()
  scanning.value = false
}

async function verifyHash(hash: string) {
  const res = await fetch(`/transparencia/verificar/${hash}?process_id=proceso_2025`)
  const data = await res.json()
  result.value = { verified: data.verified }
}
</script>
```

---

---

## CONFIGURACIÓN DE DOCKER COMPOSE (Actualizada con todas las mejoras)

```yaml
# docker-compose.yml (fragmento actualizado)
version: '3.9'

services:
  backend:
    build: ./backend
    environment:
      - TWILIO_SID=${TWILIO_SID}
      - TWILIO_TOKEN=${TWILIO_TOKEN}
      - DATABASE_URL=postgresql://urna:urna@postgres:5432/urna_digital
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend/models:/app/models  # Persistir modelos ML
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    # El build de Vite ya genera el Service Worker para PWA

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: urna
      POSTGRES_PASSWORD: urna
      POSTGRES_DB: urna_digital

  redis:
    image: redis:7-alpine
    command: redis-server --save 60 1  # Persistencia básica
```

---

## CHECKLIST DE IMPLEMENTACIÓN PARA HACKATHON

Marca cada ítem al completarlo:

```
FASE 1 — Base (Horas 1-4)
[ ] Clonar repositorio y levantar docker-compose up -d
[ ] Verificar que todos los servicios responden (health checks)
[ ] Ejecutar pytest backend/tests/ — todos los tests base pasan

FASE 2 — Seguridad y Autenticación (Horas 4-8)
[ ] Mejora 3: OTP SMS implementado y probado
[ ] Mejora 1: ZK Commitment generando correctamente en BN128
[ ] pytest backend/tests/test_zk_commitment.py ✓
[ ] pytest backend/tests/test_otp.py ✓

FASE 3 — Infraestructura de Datos (Horas 8-12)
[ ] Mejora 7: MerkleTree construye y verifica correctamente
[ ] pytest backend/tests/test_merkle.py ✓
[ ] Endpoint /transparencia/verificar/{hash} devuelve proof válida

FASE 4 — Frontend y UX (Horas 12-18)
[ ] Mejora 2: PWA instalable desde Chrome/Safari
[ ] Mejora 5: Selector de idioma funciona (es / es-easy / rar)
[ ] Mejora 8: QR Scanner abre cámara y decodifica hash
[ ] Lighthouse Accessibility Score ≥ 90

FASE 5 — IA y Tiempo Real (Horas 18-24)
[ ] Mejora 4: Isolation Forest entrenado, run_anomaly_check corriendo
[ ] Mejora 6: Dashboard D3 actualiza en tiempo real vía WebSocket
[ ] Alerta de anomalía visible en panel admin al simular ataque

DEMO FINAL
[ ] Flujo completo ciudadano: Identidad → OTP → Selección → Confirmación → Recibo PDF
[ ] Escanear QR del recibo → "Voto verificado ✅"
[ ] Simular pico de tráfico → Alerta de anomalía en panel admin
[ ] Demostrar Merkle Proof en Postman
[ ] Cambiar idioma a Rarámuri → Wizard en idioma nativo
```

---

## RESUMEN EJECUTIVO PARA PITCH

> **Voz ciudadana** pasa de ser un sistema de voto electrónico funcional a una plataforma de democracia digital de clase mundial mediante 8 mejoras concretas:
>
> 🔐 **ZK-Proofs** — Anonimato matemáticamente demostrable, no basado en confianza.
> 📡 **PWA Offline** — Funciona en la Sierra Tarahumara sin internet estable.
> 📱 **OTP 2FA** — Doble factor que previene suplantación de identidad.
> 🤖 **IA Antifraude** — Detección automática de patrones anómalos en tiempo real.
> 🗣️ **Rarámuri + Español Fácil** — Accesibilidad real para comunidades indígenas.
> 📊 **Dashboard Live** — Transparencia visual en tiempo real para el IEE y la ciudadanía.
> 🌳 **Merkle Tree** — Verificación logarítmica, estándar internacional de integridad.
> 📷 **QR Scan** — Auditoría ciudadana con un clic desde el celular.
