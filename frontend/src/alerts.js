import { $, escapeHtml } from './dom.js';

export function renderAlerts(alerts) {
  $('#alert-total').textContent = alerts.length;
  $('#nav-alert-count').textContent = alerts.length;
  $('#popover-alert-count').textContent = `${alerts.length} registradas`;
  $('#alert-summary').textContent = alerts.length ? `${alerts.length} registradas` : 'Sin alertas';
  const state = $('#alerts-state');
  const list = $('#alerts-list');
  const popoverList = $('#alert-popover-list');
  if (!alerts.length) {
    state.hidden = false;
    state.textContent = 'No hay alertas registradas. Aquí aparecerán las lecturas que requieren revisión.';
    list.hidden = true;
    popoverList.innerHTML = '<p>No hay alertas registradas.</p>';
    $('#latest-risk').textContent = '—';
    $('#latest-probability').textContent = 'sin alertas registradas';
    return;
  }
  state.hidden = true;
  list.hidden = false;
  list.innerHTML = alerts.map((alert) => `
    <div class="alert-row"><div><strong>${escapeHtml(alert.animal_id)}: riesgo ${escapeHtml(alert.risk_level)}</strong><small>${new Date(alert.created_at).toLocaleString('es-CO')}</small></div><span class="alert-status">${escapeHtml(alert.status.replaceAll('_', ' '))}</span></div>`).join('');
  popoverList.innerHTML = alerts.slice(0, 4).map((alert) => `<a href="#alertas"><strong>${escapeHtml(alert.animal_id)}: riesgo ${escapeHtml(alert.risk_level)}</strong><small>${new Date(alert.created_at).toLocaleString('es-CO')}</small></a>`).join('');
  $('#latest-risk').textContent = alerts[0].risk_level;
  $('#latest-probability').textContent = 'última alerta registrada';
}
