const API_URL = ['5173', '5174'].includes(window.location.port) ? `${window.location.protocol}//${window.location.hostname}:8000` : window.location.origin;
let generation = 0;
let onUnauthorized = null;
export function invalidateRequests() { generation++; }
export function setUnauthorizedHandler(handler) { onUnauthorized = handler; }

export async function request(path, options = {}) {
  const requestGeneration = generation;
  const response = await fetch(`${API_URL}${path}`, { credentials: 'include', headers: { 'Content-Type': 'application/json' }, ...options });
  if (requestGeneration !== generation) throw new Error('La sesión ha cambiado.');
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    if (response.status === 401 && !path.startsWith('/api/v1/auth/')) onUnauthorized?.();
    throw new Error(typeof detail.detail === 'string' ? detail.detail : 'Revisa los campos e inténtalo de nuevo.');
  }
  return response.json();
}
