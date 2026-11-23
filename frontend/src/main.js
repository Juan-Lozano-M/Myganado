import { $, showToast } from './dom.js';
import { request, invalidateRequests, setUnauthorizedHandler } from './api.js';
import { renderAnimals, configureAnimals, simulate, createAnimal, openAnimalDialog, updateBreedField, renderSimulationAvailability } from './animals.js';
import { renderAlerts } from './alerts.js';
import { loadHistory, invalidateHistory } from './history.js';
import { bindNavigation, closeAlertPopover, updateNavigation } from './navigation.js';
let sessionUser = null;
let registering = false;

async function loadDashboard() {
  if (!sessionUser) return;
  $('#refresh-button').disabled = true;
  $('#connection-title').textContent = 'Actualizando';
  $('#connection-detail').textContent = 'Consultando animales y alertas…';
  try {
    const [animals, alerts] = await Promise.all([request('/api/v1/animals'), request('/api/v1/alerts')]);
    const species = await request('/api/v1/catalogs/species');
    const speciesLabels = Object.fromEntries(species.map((item) => [item.id, item.label]));
    animals.forEach((animal) => { animal.species_label = speciesLabels[animal.species] || 'Bovina adulta (vaca)'; });
    renderAnimals(animals, sessionUser.role);
    renderAlerts(alerts);
    $('.status-strip').classList.remove('is-error');
    $('#connection-title').textContent = 'Datos actualizados';
    $('#connection-detail').textContent = `Última consulta a las ${new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}`;
    if (animals.length) await loadHistory($('#animal-select').value);
    else {
      $('#history-meta').textContent = 'Sin animales';
      $('#history-state').hidden = false;
      $('#history-state').textContent = sessionUser.role === 'veterinario' ? 'Pide al propietario que comparta un animal con tu correo.' : 'Registra un animal para comenzar su seguimiento.';
      $('#history-list').hidden = true;
      $('#history-list').replaceChildren();
      $('#history-charts').hidden = true;
      $('#history-list-title').hidden = true;
      $('#share-animal').textContent = 'Sin seleccionar';
    }
  } catch (error) {
    $('.status-strip').classList.add('is-error');
    $('#connection-title').textContent = 'Sin conexión';
    $('#connection-detail').textContent = 'No se pudieron actualizar los datos. Intenta actualizar de nuevo.';
    $('#animals-state').hidden = false;
    $('#alerts-state').hidden = false;
    $('#vet-animals-state').hidden = false;
    $('#vet-animals-list').hidden = true;
    $('#animals-state').textContent = error.message;
    $('#alerts-state').textContent = 'No fue posible consultar las alertas.';
    $('#vet-animals-state').textContent = 'No fue posible consultar los animales compartidos. Actualiza los datos para reintentar.';
    $('#alert-popover-list').innerHTML = '<p>No fue posible consultar las alertas. Actualiza los datos para reintentar.</p>';
    showToast('La API no está disponible.');
  } finally { $('#refresh-button').disabled = false; }
}
export function init() {
  bindNavigation(() => sessionUser);
  configureAnimals(loadDashboard);
  setUnauthorizedHandler(showLogin);
  $('#today').textContent = new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date());
$('#refresh-button').addEventListener('click', loadDashboard);
$('#simulate-button').addEventListener('click', simulate);
$('#new-animal-button').addEventListener('click', openAnimalDialog);
$('#animal-select').addEventListener('change', (event) => {
  $('#history-animal-select').value = event.target.value;
  loadHistory(event.target.value);
});
$('#animal-select').addEventListener('change', renderSimulationAvailability);
$('#history-animal-select').addEventListener('change', (event) => {
  $('#animal-select').value = event.target.value;
  loadHistory(event.target.value);
  renderSimulationAvailability();
});
$('#vet-animal-select').addEventListener('change', (event) => { $('#share-animal').textContent = event.target.value || 'Sin seleccionar'; });
$('#animal-form').addEventListener('submit', createAnimal);
$('#species-select').addEventListener('change', updateBreedField);
$('.close-button').type = 'button';
$('.close-button').addEventListener('click', () => $('#animal-dialog').close());
function showLogin() {
  invalidateRequests();
  invalidateHistory();
  sessionUser = null;
  $('.app-shell').hidden = true;
  $('#auth-screen').hidden = false;
  if ($('#animal-dialog').open) $('#animal-dialog').close();
  $('#animal-form').reset();
  $('#auth-form').reset();
  setRegistrationMode(false);
  $('#vet-email').value = '';
  ['#animals-list', '#alerts-list', '#history-list', '#vet-animals-list', '#simulation-result'].forEach((id) => $(id).replaceChildren());
  $('#history-charts').hidden = true;
  $('#history-list-title').hidden = true;
  $('#risk-chart').replaceChildren();
  $('#temperature-chart').replaceChildren();
  ['#animals-list', '#alerts-list', '#history-list', '#vet-animals-list'].forEach((id) => { $(id).hidden = true; });
  [['#animals-state', 'Cargando registros…'], ['#alerts-state', 'Cargando alertas…'], ['#history-state', 'Selecciona un animal para consultar sus mediciones.'], ['#vet-animals-state', 'Cargando animales…']].forEach(([id, message]) => { $(id).hidden = false; $(id).textContent = message; });
  $('#alert-popover-list').innerHTML = '<p>No hay alertas registradas.</p>';
  closeAlertPopover();
  $('#simulation-result').hidden = true;
  $('#animal-select').replaceChildren();
  $('#history-animal-select').replaceChildren(new Option('Selecciona un animal', ''));
  $('#vet-animal-select').replaceChildren(new Option('Selecciona un animal', ''));
  $('#animal-total').textContent = '…';
  $('#alert-total').textContent = '…';
  $('#nav-alert-count').textContent = '0';
  $('#popover-alert-count').textContent = '0 registradas';
  $('#alert-summary').textContent = 'Sin alertas';
  $('#latest-risk').textContent = '…';
  $('#latest-probability').textContent = 'sin alertas registradas';
  $('#history-meta').textContent = 'Selecciona un animal';
  $('#share-animal').textContent = 'Sin seleccionar';
  $('#account-name').textContent = '';
  $('#account-role').textContent = '';
  ['#vet-account-name', '#vet-account-email', '#vet-account-role'].forEach((id) => { $(id).textContent = '…'; });
}

async function enterDashboard(user) {
  invalidateRequests();
  sessionUser = user;
  $('#auth-screen').hidden = true;
  $('.app-shell').hidden = false;
  $('#auth-form').reset();
  $('#auth-error').hidden = true;
  $('#account-name').textContent = user.name;
  $('#account-role').textContent = user.role === 'veterinario' ? 'Veterinario · consulta compartida' : 'Productor / campesino';
  const producer = user.role === 'productor';
  $('#vet-account-name').textContent = user.name;
  $('#vet-account-email').textContent = user.email;
  $('#vet-account-role').textContent = producer ? 'Productor' : 'Veterinario';
  $('#dashboard-vet-description').textContent = producer ? 'Gestiona el acceso al seguimiento.' : 'Consulta los animales compartidos contigo.';
  $('#new-animal-button').hidden = !producer;
  $('.action-panel').hidden = !producer;
  $('#share-panel').hidden = !producer;
  $('#vet-view-panel').hidden = producer;
  $('.content-grid').classList.toggle('veterinarian-view', !producer);
  updateNavigation();
  await loadDashboard();
}

function setRegistrationMode(enabled) {
  registering = enabled;
  $('#registration-fields').hidden = !registering;
  $('#registration-fields input').disabled = !registering;
  $('#registration-fields input').required = registering;
  $('#registration-fields select').disabled = !registering;
  $('#auth-title').textContent = registering ? 'Crear tu cuenta' : 'Iniciar sesión';
  $('#auth-description').textContent = registering ? 'Elige tu perfil y comienza el seguimiento.' : 'Ingresa con tu correo y contraseña.';
  $('#auth-submit').textContent = registering ? 'Crear cuenta' : 'Entrar';
  $('#auth-toggle').textContent = registering ? 'Ya tengo cuenta. Iniciar sesión' : '¿No tienes cuenta? Regístrate';
  $('#auth-form [name=password]').autocomplete = registering ? 'new-password' : 'current-password';
  $('#auth-error').hidden = true;
}
$('#auth-toggle').addEventListener('click', () => setRegistrationMode(!registering));

$('#auth-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  $('#auth-submit').disabled = true;
  $('#auth-toggle').disabled = true;
  $('#auth-error').hidden = true;
  try {
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const user = await request(`/api/v1/auth/${registering ? 'register' : 'login'}`, { method: 'POST', body: JSON.stringify(data) });
    await enterDashboard(user);
  } catch (error) {
    $('#auth-error').textContent = error.message;
    $('#auth-error').hidden = false;
  } finally {
    $('#auth-submit').disabled = false;
    $('#auth-toggle').disabled = false;
  }
});

$('#logout-button').addEventListener('click', async () => {
  $('#logout-button').disabled = true;
  try {
    await request('/api/v1/auth/logout', { method: 'POST' });
    showLogin();
  } catch { showToast('No se pudo cerrar la sesión. Inténtalo de nuevo.'); }
  finally { $('#logout-button').disabled = false; }
});

async function shareAccess(revoke = false) {
  if (!$('#share-form').reportValidity()) return;
  const animalId = $('#vet-animal-select').value;
  if (!animalId) { showToast('Selecciona un animal primero.'); return; }
  try {
    await request(`/api/v1/auth/animals/${encodeURIComponent(animalId)}/veterinarian`, {
      method: revoke ? 'DELETE' : 'POST', body: JSON.stringify({ email: $('#vet-email').value }),
    });
    showToast(revoke ? 'Acceso veterinario retirado.' : 'Acceso compartido con el veterinario.');
  } catch (error) { showToast(error.message); }
}
$('#share-form').addEventListener('submit', (event) => { event.preventDefault(); shareAccess(); });
$('#revoke-access').addEventListener('click', () => shareAccess(true));
$('#auth-submit').disabled = true;
$('#auth-toggle').disabled = true;
request('/api/v1/auth/me').then(enterDashboard).catch(showLogin).finally(() => {
  $('#auth-submit').disabled = false;
  $('#auth-toggle').disabled = false;
});

}
