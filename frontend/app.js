const API_URL = 'http://127.0.0.1:8000';
const $ = (selector) => document.querySelector(selector);

function showToast(message) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2800);
}

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `La solicitud falló (${response.status}).`);
  }
  return response.json();
}

function renderAnimals(animals) {
  $('#animal-total').textContent = animals.length;
  const state = $('#animals-state');
  const list = $('#animals-list');
  if (!animals.length) { state.textContent = 'No hay animales registrados todavía.'; list.hidden = true; return; }
  state.hidden = true;
  list.hidden = false;
  list.innerHTML = animals.map((animal) => `
    <div class="animal-row">
      <div><div class="animal-name">${animal.animal_id}</div><div class="animal-detail">${animal.breed} · ${animal.age_months} meses · ${animal.weight_kg} kg · ${animal.owner}</div></div>
      <span class="risk-pill low">en seguimiento</span>
    </div>`).join('');
}

function renderAlerts(alerts) {
  $('#alert-total').textContent = alerts.length;
  $('#nav-alert-count').textContent = alerts.length;
  $('#alert-summary').textContent = alerts.length ? `${alerts.length} pendientes` : 'Sin alertas';
  const state = $('#alerts-state');
  const list = $('#alerts-list');
  if (!alerts.length) { state.textContent = 'No hay alertas registradas.'; list.hidden = true; return; }
  state.hidden = true;
  list.hidden = false;
  list.innerHTML = alerts.slice(0, 5).map((alert) => `
    <div class="alert-row"><span class="alert-marker"></span><div><strong>${alert.animal_id} · Riesgo ${alert.risk_level}</strong><small>${new Date(alert.created_at).toLocaleString('es-CO')}</small></div><span class="alert-status">${alert.status.replaceAll('_', ' ')}</span></div>`).join('');
  $('#latest-risk').textContent = alerts[0].risk_level;
  $('#latest-probability').textContent = 'última alerta registrada';
}

async function loadDashboard() {
  try {
    const [animals, alerts] = await Promise.all([request('/api/v1/animals'), request('/api/v1/alerts')]);
    renderAnimals(animals);
    renderAlerts(alerts);
  } catch (error) {
    $('#animals-state').textContent = error.message;
    $('#alerts-state').textContent = 'No fue posible consultar las alertas.';
    showToast('La API no está disponible.');
  }
}

async function simulate() {
  const button = $('#simulate-button');
  const result = $('#simulation-result');
  button.disabled = true;
  button.textContent = 'Ejecutando...';
  try {
    const scenario = $('#scenario-select').value;
    const data = await request('/api/v1/simulations', { method: 'POST', body: JSON.stringify({ scenario, seed: 42 }) });
    result.hidden = false;
    result.innerHTML = `<strong>${data.prediction.risk_level}</strong><small>Probabilidad ${Math.round(data.prediction.probability * 100)}% · ${scenario.replaceAll('_', ' ')}</small>`;
    showToast('Lectura simulada procesada.');
  } catch (error) { showToast(error.message); } finally { button.disabled = false; button.innerHTML = '<span aria-hidden="true">◉</span> Ejecutar simulación'; }
}

async function createAnimal(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const error = $('#form-error');
  const data = Object.fromEntries(new FormData(form));
  data.age_months = Number(data.age_months);
  data.weight_kg = Number(data.weight_kg);
  try {
    await request('/api/v1/animals', { method: 'POST', body: JSON.stringify(data) });
    $('#animal-dialog').close();
    form.reset();
    error.hidden = true;
    await loadDashboard();
    showToast('Animal registrado correctamente.');
  } catch (requestError) { error.textContent = requestError.message; error.hidden = false; }
}

$('#today').textContent = new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date());
$('#refresh-button').addEventListener('click', loadDashboard);
$('#simulate-button').addEventListener('click', simulate);
$('#new-animal-button').addEventListener('click', () => $('#animal-dialog').showModal());
$('#animal-form').addEventListener('submit', createAnimal);
loadDashboard();
