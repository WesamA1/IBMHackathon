/**
 * api.js — shared fetch wrapper for all frontend pages.
 * Reads BASE_URL from window.HB_API_URL if set, otherwise defaults to
 * same-origin /api/v1 (works when FastAPI serves the static files).
 *
 * Usage:
 *   import { api } from './api.js';
 *   const updates = await api.get('/updates');
 *   const task    = await api.post('/tasks', { title: '...', ... });
 *   await api.patch('/tasks/3', { status: 'done' });
 *   await api.delete('/tasks/3');
 */

const BASE = (window.HB_API_URL ?? '') + '/api/v1';

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(BASE + path, opts);
  if (res.status === 204) return null;
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  get:    (path)        => request('GET',    path),
  post:   (path, body)  => request('POST',   path, body),
  patch:  (path, body)  => request('PATCH',  path, body),
  delete: (path)        => request('DELETE', path),
};

/** Convenience: show a pixel-style toast on API error */
export function apiError(err) {
  console.error('[API]', err.message);
  const toast = document.createElement('div');
  toast.textContent = `API ERROR: ${err.message}`;
  toast.style.cssText = `
    position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);
    background:#1a0000;border:2px solid #ff5555;color:#ff5555;
    padding:0.6rem 1.2rem;font-family:'Press Start 2P',monospace;
    font-size:0.45rem;z-index:9999;letter-spacing:1px;
    box-shadow:0 0 12px rgba(255,85,85,0.4);
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
