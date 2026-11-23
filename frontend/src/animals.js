import { $, escapeHtml, showToast } from './dom.js';
import { request } from './api.js';
import { loadHistory } from './history.js';
let refreshDashboard = () => {};
export function configureAnimals(refresh) { refreshDashboard = refresh; }

export function renderAnimals(animals, role) {
  $('#animal-total').textContent = animals.length;
  const state = $('#animals-state');
  const list = $('#animals-list');
  const vetState = $('#vet-animals-state');
  const vetList = $('#vet-animals-list');
  const select = $('#animal-select');
  const selected = select.value;
  const options = animals.map((animal) => `<option value="${escapeHtml(animal.animal_id)}" data-species="${escapeHtml(animal.species || 'bovine_adult')}">${escapeHtml(animal.animal_id)} · ${escapeHtml(animal.breed)} · ${escapeHtml(animal.species_label || '')}</option>`).join('');
  [select, $('#history-animal-select'), $('#vet-animal-select')].forEach((field) => {
    const previous = field.value || selected;
    field.innerHTML = options || '<option value="">Sin animales disponibles</option>';
    if (animals.some((animal) => animal.animal_id === previous)) field.value = previous;
    else if (animals.length) field.value = animals[0].animal_id;
  });
  if (!animals.length) {
    state.hidden = false;
    state.textContent = 'No hay animales registrados todavía.';
    list.hidden = true;
    vetState.hidden = false;
    vetState.textContent = role === 'veterinario' ? 'Todavía no tienes animales compartidos.' : 'No hay animales registrados todavía.';
    vetList.hidden = true;
    $('#share-animal').textContent = 'Sin seleccionar';
    renderSimulationAvailability();
    return;
  }
  $('#share-animal').textContent = $('#vet-animal-select').value;
  state.hidden = true;
  list.hidden = false;
  list.innerHTML = animals.map((animal) => `
    <div class="animal-row">
      <div><button class="animal-name animal-link" type="button" data-animal-id="${escapeHtml(animal.animal_id)}">${escapeHtml(animal.animal_id)}</button><div class="animal-detail">${escapeHtml(animal.species_label || 'Bovina adulta (vaca)')} · ${escapeHtml(animal.breed)} · ${animal.age_months} meses · ${animal.weight_kg} kg · ${escapeHtml(animal.owner)}</div></div>
      <span class="risk-pill low">en seguimiento</span>
    </div>`).join('');
  list.querySelectorAll('[data-animal-id]').forEach((button) => button.addEventListener('click', () => {
    select.value = button.dataset.animalId;
    $('#history-animal-select').value = button.dataset.animalId;
    loadHistory(button.dataset.animalId);
    window.location.hash = '#historial';
  }));
  vetState.hidden = true;
  vetList.hidden = false;
  vetList.innerHTML = animals.map((animal) => `<div class="animal-row"><div><strong class="animal-name">${escapeHtml(animal.animal_id)}</strong><div class="animal-detail">${escapeHtml(animal.species_label || 'Bovina adulta (vaca)')} · ${escapeHtml(animal.breed)} · ${escapeHtml(animal.owner)}</div></div><button class="text-button" type="button" data-vet-animal="${escapeHtml(animal.animal_id)}">Ver historial</button></div>`).join('');
  vetList.querySelectorAll('[data-vet-animal]').forEach((button) => button.addEventListener('click', () => {
    $('#history-animal-select').value = button.dataset.vetAnimal;
    loadHistory(button.dataset.vetAnimal);
    window.location.hash = '#historial';
  }));
  renderSimulationAvailability();
}
export async function simulate() {
  const button = $('#simulate-button');
  const result = $('#simulation-result');
  button.disabled = true;
  button.textContent = 'Ejecutando...';
  try {
    const scenario = $('#scenario-select').value;
    const animal_id = $('#animal-select').value;
    if (!animal_id) throw new Error('Registra y selecciona un animal antes de simular.');
    const data = await request('/api/v1/simulations', { method: 'POST', body: JSON.stringify({ scenario, seed: 42, animal_id }) });
    result.hidden = false;
    result.innerHTML = `<strong>${data.prediction.risk_level}</strong><small>Confianza del modelo ${Math.round(data.prediction.probability * 100)}% · ${scenario.replaceAll('_', ' ')}</small>`;
    await refreshDashboard();
    showToast('Lectura simulada procesada.');
  } catch (error) { showToast(error.message); } finally { button.disabled = false; button.textContent = 'Ejecutar simulación'; }
}

export async function createAnimal(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const error = $('#form-error');
  const button = form.querySelector('button[type="submit"]');
  if (button.disabled || $('#species-select').disabled ||
      ($('#species-select').value === 'bovine_adult' && $('#breed-select').disabled)) return;
  button.disabled = true;
  button.textContent = 'Guardando…';
  error.hidden = true;
  const data = Object.fromEntries(new FormData(form));
  if (data.species !== 'bovine_adult') data.breed = null;
  data.age_months = Number(data.age_months);
  data.weight_kg = Number(data.weight_kg);
  try {
    await request('/api/v1/animals', { method: 'POST', body: JSON.stringify(data) });
    $('#animal-dialog').close();
    form.reset();
    error.hidden = true;
    await refreshDashboard();
    showToast('Animal registrado correctamente.');
  } catch (requestError) { error.textContent = requestError.message; error.hidden = false; }
  finally { button.disabled = false; button.textContent = 'Guardar animal'; }
}

export async function openAnimalDialog() {
  const select = $('#breed-select');
  const button = $('#animal-form button[type="submit"]');
  const previousBreed = select.value;
  $('#form-error').hidden = true;
  select.disabled = true;
  button.disabled = true;
  select.replaceChildren(new Option('Cargando razas…', ''));
  $('#animal-dialog').showModal();
  try {
    const [breeds, species] = await Promise.all([
      request('/api/v1/catalogs/breeds'), request('/api/v1/catalogs/species'),
    ]);
    select.replaceChildren(new Option('Selecciona una raza', ''));
    breeds.forEach((breed) => select.add(new Option(breed, breed)));
    if (breeds.includes(previousBreed)) select.value = previousBreed;
    const speciesSelect = $('#species-select');
    speciesSelect.replaceChildren(new Option('Selecciona el tipo de animal', ''));
    species.forEach((item) => speciesSelect.add(new Option(`${item.label} · ${item.count.toLocaleString('es-CO')} registros fuente`, item.id)));
    speciesSelect.disabled = false;
    speciesSelect.value = 'bovine_adult';
    updateBreedField();
    select.disabled = $('#species-select').value !== 'bovine_adult';
    button.disabled = false;
  } catch {
    select.replaceChildren(new Option('Razas no disponibles', ''));
    $('#form-error').textContent = 'No se pudo cargar el catálogo. Cierra el formulario y vuelve a abrirlo para reintentar.';
    $('#form-error').hidden = false;
  }
}

export function updateBreedField() {
  const adultBovine = $('#species-select').value === 'bovine_adult';
  $('#breed-field').hidden = !adultBovine;
  $('#breed-select').required = adultBovine;
  $('#breed-select').disabled = !adultBovine;
  $('#species-source-note').textContent = adultBovine
    ? 'Razas del dataset de mastitis bovina: 6.600 lecturas de referencia.'
    : 'Categoría del dataset de animales jóvenes. La fuente no aporta razas para esta categoría ni predicciones clínicas para ella.';
}

export function renderSimulationAvailability() {
  const adultBovine = $('#animal-select').selectedOptions[0]?.dataset.species === 'bovine_adult';
  $('#simulate-button').disabled = !adultBovine;
  $('#scenario-select').disabled = !adultBovine;
  $('#simulation-species-note').hidden = adultBovine;
}
