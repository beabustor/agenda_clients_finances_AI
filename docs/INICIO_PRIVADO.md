# Configuración inicial en una copia privada

## Administrador

1. En el repositorio público, activar Settings → Template repository si se desea usar «Use this template». Crear un repositorio nuevo con visibilidad **Private**. No crear un fork público para datos privados. Como alternativa, copiar el código a un repositorio privado nuevo.
2. Descargar esa copia y ejecutar `python3 -m app.server` desde su raíz, en un equipo de confianza. La aplicación no copia repositorios ni comprueba su visibilidad; confirmar ambas cosas antes de continuar.
3. Completar el formulario «Configura tu oficina privada»: URL de la copia, nombre del negocio, actividad, correo de contacto y canales deseados. Gmail, ID de carpeta Drive y número Business son referencias no secretas. No pegar contraseñas, tokens o claves en estos campos.
4. Los datos se almacenan en el SQLite local ignorado por Git. Ni guardar el formulario ni crear un repositorio privado sube los datos a GitHub. Mantener también fuera del repositorio privado documentos, tokens y backups. No compartir la base entre distintos autónomos.
5. Probar el simulador con un canal seleccionado y datos ficticios. Repetir el mismo identificador en ese canal no crea un segundo evento. Identificadores distintos sí generan entradas distintas. La deduplicación de documentos por huella todavía no existe.

## Contrato de desarrollo actual

- `GET /api/configuracion`: perfil local y lista vacía de conectores activos.
- `POST /api/configuracion`: preferencias sin secretos; solo los campos del formulario son aceptados.
- `POST /api/eventos/simular`: JSON con `canal` (`gmail`, `chatgpt`, `whatsapp`), `externo` (ID estable) y `texto`. Exige configuración previa y canal seleccionado. No es un webhook público.
- `GET /api/eventos`: últimas 100 entradas, con estado `pendiente_revision` y fecha UTC.

Ninguna entrada dispara IA, etiqueta correos, mueve archivos, crea citas ni contabiliza. Todavía no hay worker, reintentos, gestión de incidencias, aprobación de borradores ni adjuntos. La base de eventos permite construir esos pasos sin fingir conexiones activas.

## Credenciales e integraciones futuras

Gmail/Drive necesitarán OAuth del titular con permisos mínimos y tokens cifrados del lado servidor. ChatGPT necesitará una herramienta autenticada; WhatsApp Business, webhooks con firma verificada. No se solicitan secretos desde el front actual porque aún no existe el almacenamiento seguro necesario. El admin y el titular completarán la autorización cuando se implementen esos conectores.

Antes de publicar endpoints: autenticación, autorización, HTTPS, protección de sesiones, validación de webhooks, gestión de secretos, límites y copias verificadas. El servidor actual permanece local y carece de autenticación. Un repositorio privado no convierte este prototipo en un servicio seguro para Internet.
