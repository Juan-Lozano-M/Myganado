# Cuentas y acceso

En la pantalla de acceso, selecciona «Regístrate» y elige Productor / campesino / usuario normal o Veterinario. No hay cuentas ni contraseñas predeterminadas.

- Productor: registra animales, genera lecturas y consulta sus propios historiales y alertas. Puede compartir o retirar el acceso de un veterinario introduciendo su correo en «Acceso veterinario».
- Veterinario: consulta animales, historiales y alertas compartidos por sus propietarios. No puede registrar animales, simular lecturas ni compartir los datos de otros propietarios. El rol es autodeclarado y no acredita una licencia profesional.

El registro crea una cuenta e inicia la sesión. Las contraseñas requieren de 10 a 128 caracteres y se guardan mediante scrypt con sal aleatoria. La cookie de sesión es HttpOnly y SameSite=Strict, dura 8 horas y se revoca al cerrar sesión. El servidor guarda únicamente el hash del token. Tras 10 intentos de acceso por correo en 15 minutos se bloquean temporalmente más intentos. Las rutas de animales, alertas, historiales, mediciones y simulaciones comprueban autenticación y permisos en el backend.

En desarrollo utiliza el mismo nombre de host para frontend y backend (localhost o 127.0.0.1). CORS permite credenciales solo para los orígenes locales configurados. En despliegue, sirve frontend y API bajo el mismo origen y HTTPS; la cookie lleva Secure cuando el servidor recibe la petición como HTTPS. Configura el proxy para preservar el host y transmitir el esquema original, confiando únicamente en proxies propios.

## JWT y configuración

La cookie contiene un JWT firmado con HS256 mediante PyJWT. El backend exige y valida `sub`, `iat`, `nbf`, `exp`, `iss`, `aud` y `jti`; solo acepta HS256. No se incluyen contraseñas ni datos personales en el token, y no se guarda en localStorage. Los permisos se consultan en la base de datos en cada petición, no se confía en un rol enviado por el navegador.

Se conserva una lista de sesiones activas con el hash del JWT para revocarlo inmediatamente al cerrar sesión. Por tanto, es una implementación JWT con estado de revocación, no completamente sin estado. Las sesiones anteriores de token opaco requieren iniciar sesión de nuevo.

Configura `MYGANADO_JWT_SECRET` con un secreto aleatorio de al menos 32 bytes, compartido por todos los procesos del backend. No lo guardes en el repositorio. Las variables se leen del entorno del proceso; no se carga un archivo `.env` automáticamente.

Si `MYGANADO_ENV=development` (valor predeterminado) y no hay secreto configurado, se genera una clave temporal por proceso y se avisa en el registro: las sesiones se invalidan al reiniciar. Para producción, establece `MYGANADO_ENV=production` y un secreto persistente en el gestor de secretos del despliegue; el servidor no inicia si falta el secreto. Rotar la clave invalida los JWT existentes. No hay renovación automática: al caducar, se requiere iniciar sesión otra vez.

## Asignación de animales anteriores

Los animales existentes se conservan sin asignarlos automáticamente a una cuenta nueva. Para vincular un animal antiguo a una cuenta de productor ya registrada, desde la raíz del proyecto:

```powershell
.venv/Scripts/python.exe backend/assign_animal_owner.py --animal ID-DEL-ANIMAL --email propietario@correo.com
```

Este comando administrativo local solo asigna animales sin propietario de cuenta; no sustituye una asignación existente ni utiliza el campo de texto «Propietario» como credencial.

## Verificación

Instala `backend/requirements-dev.txt` y ejecuta `python -m unittest discover -s tests -p test_auth.py`. Las pruebas usan una base temporal y verifican aislamiento, cookies, revocación, caducidad, límites de intentos, control de origen y conservación de registros antiguos.

No se incluyen todavía recuperación de contraseña por correo, verificación de correo, validación de matrícula veterinaria ni MFA.
