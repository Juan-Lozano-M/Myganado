import { $ } from './dom.js';
let getSessionUser = () => null;

const viewHashes = new Set(['#inicio', '#animales', '#historial', '#alertas', '#veterinario']);
function setMobileMenu(open) {
  $('.sidebar').classList.toggle('is-menu-open', open);
  $('#menu-toggle').setAttribute('aria-expanded', String(open));
  $('#menu-toggle').setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  if (!open) closeAlertPopover();
}
export function closeAlertPopover() {
  $('#alert-popover').hidden = true;
  $('#alert-toggle').setAttribute('aria-expanded', 'false');
}
export function updateNavigation() {
  const active = viewHashes.has(window.location.hash) ? window.location.hash : '#inicio';
  document.querySelectorAll('[data-view]').forEach((view) => { view.hidden = `#${view.id}` !== active; });
  document.querySelectorAll('.nav-link').forEach((link) => {
    const selected = link.id === 'alert-toggle' ? active === '#alertas' : link.getAttribute('href') === active;
    link.classList.toggle('active', selected);
    if (selected && link.tagName === 'A') link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  closeAlertPopover();
  setMobileMenu(false);
  if (getSessionUser()) window.scrollTo({ top: 0, behavior: 'auto' });
}
export function bindNavigation(sessionUserGetter) {
  getSessionUser = sessionUserGetter;
  window.addEventListener('hashchange', updateNavigation);
  $('#menu-toggle').addEventListener('click', () => {
    setMobileMenu(!$('.sidebar').classList.contains('is-menu-open'));
  });
  $('.sidebar').addEventListener('click', (event) => {
    if (event.target.closest('a[href^="#"]')) setMobileMenu(false);
  });
  $('#alert-toggle').addEventListener('click', () => {
    const popover = $('#alert-popover');
    popover.hidden = !popover.hidden;
    $('#alert-toggle').setAttribute('aria-expanded', String(!popover.hidden));
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.alerts-nav')) closeAlertPopover();
    if (!event.target.closest('.sidebar')) setMobileMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (!$('#alert-popover').hidden) {
      closeAlertPopover();
      $('#alert-toggle').focus();
    } else if ($('.sidebar').classList.contains('is-menu-open')) {
      setMobileMenu(false);
      $('#menu-toggle').focus();
    }
  });
  window.matchMedia('(min-width: 901px)').addEventListener('change', (event) => {
    if (event.matches) setMobileMenu(false);
  });
  updateNavigation();
}
