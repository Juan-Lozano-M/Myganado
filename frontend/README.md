# Frontend

Aplicación estática en HTML, CSS y JavaScript nativo. No requiere compilación.

## Estructura

- `index.html`: documento base, navegación y puntos de montaje.
- `views/`: una plantilla HTML por pantalla y otra para el formulario de animales.
- `src/boot.js`: carga las plantillas antes de iniciar la aplicación.
- `src/main.js`: sesión, eventos y carga del panel.
- `src/api.js`: peticiones a la API y control de sesión.
- `src/animals.js`, `alerts.js`, `history.js`, `charts.js`, `navigation.js`: funciones de cada área.
- `src/dom.js`: utilidades de presentación.
- `tokens.css`, `base.css`, `styles.css`: estilos y componentes visuales.

Para desarrollo local, sirve este directorio mediante HTTP, por ejemplo `python -m http.server 5173 --directory frontend` desde la raíz del proyecto, con la API en el puerto 8000. Las plantillas se cargan con `fetch`, por lo que abrir `index.html` mediante `file://` no funciona. El contenedor de `frontend/Dockerfile` copia las plantillas, los módulos y las hojas de estilo.
