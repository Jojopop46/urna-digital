const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let adminToken: string | null = null

export function setAdminToken(token: string | null) {
  adminToken = token
}

export function getAdminToken(): string | null {
  return adminToken
}

async function request(path: string, options: RequestInit = {}) {
  const url = `${API_URL}${path}`
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (adminToken) {
    headers['Authorization'] = `Bearer ${adminToken}`
  }

  const res = await fetch(url, { ...options, headers })

  if (res.status === 429) {
    throw new Error('Demasiadas solicitudes. Intenta más tarde.')
  }
  if (res.status === 401) {
    throw new Error('No autorizado')
  }
  if (res.status === 403) {
    throw new Error('Acceso denegado')
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({ detail: 'Error del servidor' }))
    throw new Error(data.detail || 'Error del servidor')
  }

  if (res.status === 204) return null
  return res.json()
}

export const api = {
  get: (path: string) => request(path, { method: 'GET' }),
  post: (path: string, body: unknown) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  patch: (path: string, body: unknown) => request(path, { method: 'PATCH', body: JSON.stringify(body) }),
}
