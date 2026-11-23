import { $, escapeHtml } from './dom.js';
import { request } from './api.js';
import { renderHistoryCharts } from './charts.js';
let historyRequestId = 0;
export function invalidateHistory() { historyRequestId++; }

export async function loadHistory(animalId) {
  if (!animalId) return;
  const requestId = ++historyRequestId;
  const state = $('#history-state');
  const list = $('#history-list');
  $('#history-animal-select').value = animalId;
  $('#history-meta').textContent = animalId;
  state.hidden = false;
  state.textContent = 'Cargando mediciones…';
  list.hidden = true;
  $('#history-charts').hidden = true;
  $('#history-list-title').hidden = true;
  try {
    const history = await request(`/api/v1/animals/${encodeURIComponent(animalId)}/history`);
    if (requestId !== historyRequestId) return;
    if (!history.length) { state.textContent = 'No hay mediciones registradas para este animal.'; return; }
    renderHistoryCharts(history);
    list.innerHTML = history.map((item) => `
      <div class="history-row"><div><strong>${escapeHtml(item.risk_level)}</strong><small>${new Date(item.created_at).toLocaleString('es-CO')}${typeof item.payload?.temperature === 'number' ? ` · Temperatura corporal: ${item.payload.temperature.toFixed(1)} °C` : ''}</small></div><span class="history-confidence"><small>Confianza del modelo</small><strong>${Math.round(item.probability * 100)}%</strong></span></div>`).join('');
    state.hidden = true;
    $('#history-list-title').hidden = false;
    list.hidden = false;
  } catch (error) {
    if (requestId !== historyRequestId) return;
    state.hidden = false;
    state.textContent = error.message;
    $('#history-charts').hidden = true;
    $('#history-list-title').hidden = true;
    list.hidden = true;
  }
}
