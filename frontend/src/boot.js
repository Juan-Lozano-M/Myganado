const fragments = [
  ['auth-mount', 'auth'],
  ['views-mount', 'dashboard'],
  ['views-mount', 'animals'],
  ['views-mount', 'history'],
  ['views-mount', 'alerts'],
  ['views-mount', 'veterinary'],
  ['dialog-mount', 'animal-dialog'],
];

async function boot() {
  const markup = await Promise.all(fragments.map(async ([, name]) => {
    const response = await fetch(`views/${name}.html`);
    if (!response.ok) throw new Error(`No se pudo cargar ${name}.`);
    return response.text();
  }));
  fragments.forEach(([target], index) => document.getElementById(target).insertAdjacentHTML('beforeend', markup[index]));
  const { init } = await import('./main.js');
  init();
}

boot().catch((error) => {
  const mount = document.getElementById('auth-mount');
  const message = document.createElement('p');
  message.setAttribute('role', 'alert');
  message.textContent = `No se pudo iniciar la aplicación. ${error.message}`;
  const retry = document.createElement('button');
  retry.type = 'button';
  retry.textContent = 'Reintentar';
  retry.addEventListener('click', () => window.location.reload());
  mount.replaceChildren(message, retry);
});
