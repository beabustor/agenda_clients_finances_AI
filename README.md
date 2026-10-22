# Mi oficina · Autónomos de España

**Demo admin:** inicia `python3 -m app.server` y abre el puerto local 8000. Ficha → conexiones → prueba. El panel de registros está en `/gestion`.

![Correo](app/static/icons/envelope.svg) **Gmail** · ![Archivos](app/static/icons/folder.svg) **Drive** · ![Chat](app/static/icons/chat-dots.svg) **ChatGPT** · ![WhatsApp](app/static/icons/whatsapp.svg) **WhatsApp**

[Fragmentos del admin](docs/ADMIN_CODIGO.md) · [Prompts de acciones](prompts/sistema.md)


Base pública, en español, para desarrollar una oficina de clientes, servicios, citas y control contable. Primera versión local y manual, sin dependencias externas ni llamadas a proveedores.

## Iniciar

Requiere Python 3.12 o posterior. Desde la raíz del repositorio:

```bash
python3 -m app.server
```

Abre en tu navegador el puerto local 8000. El servidor escucha exclusivamente en el equipo local. `PORT` permite elegir otro puerto; `AGENDA_DB` permite elegir otra ruta para SQLite. No se carga `.env` automáticamente.

```bash
python3 -m unittest discover -s tests -v
```

## Qué funciona

- Alta y listado de clientes, servicios, citas, ingresos y gastos.
- Persistencia SQLite en `data/agenda.sqlite3`, excluida de Git.
- Resumen acumulado de bases de ingresos/gastos, sin filtrar por ejercicio.
- Base, tipo de IVA y porcentaje de afectación editables; revisión fiscal pendiente.
- CSV UTF-8 con separador punto y coma para abrir o importar en Excel.
- Interfaz adaptable a móvil, sin recursos ni rastreadores externos.

## Límites actuales

Es un prototipo de control interno: no emite facturas legales, no presenta impuestos, no calcula liquidaciones ni determina deducciones. CSV no es un libro Excel con fórmulas. Las citas no tienen recordatorios ni sincronización. Clientes y servicios aún no se vinculan a las citas o facturas. No incluye edición, eliminación, adjuntos, autenticación, múltiples usuarios o conectores reales. No publicar este servidor en Internet ni introducir datos reales en entornos compartidos.

## Plantilla pública y clientes privados

El administrador puede marcar este repositorio como plantilla en GitHub y generar un repositorio **privado** para cada autónomo. Las copias no reciben actualizaciones automáticamente; documentar y revisar las actualizaciones antes de aplicarlas. No hace falta un repositorio por cliente final del autónomo: esos clientes son registros de su aplicación.

Incluso en repositorios privados, mantener fuera de Git las bases de datos, documentos, copias de seguridad y credenciales. `.gitignore` ayuda a prevenir inclusiones accidentales; no elimina datos ya publicados. Mantener el almacenamiento de cada autónomo separado, con permisos de acceso y copias cifradas. El repositorio público solo debe contener ejemplos ficticios.

## Costes y conexiones

La versión manual funciona localmente sin suscripciones. No es posible garantizar un coste total de 20 €: ChatGPT Plus tiene precio e impuestos según contratación y **no incluye créditos de la API de OpenAI**. Una integración mediante API se factura por separado. Conectar desde ChatGPT mediante herramientas requiere comprobar las capacidades del plan, un servidor accesible, autenticación y las condiciones vigentes. WhatsApp Business Platform, alojamiento y almacenamiento también pueden generar costes.

No necesitas entregar credenciales para probar esta versión. La configuración real de proveedores se hará con el administrador y autorización del titular; nunca pegues claves en el chat o en Git.

Consulta [el plan y la configuración](docs/PLAN.md) y [privacidad y seguridad](docs/PRIVACIDAD.md).

## Configuración inicial y base de automatizaciones

El panel incluye un formulario para declarar la copia privada, el perfil del negocio y los canales deseados, además de una bandeja de eventos simulados con prevención de duplicados. Las preferencias se conservan en SQLite. No se solicitan claves ni se activan conexiones reales. Sigue [la guía de inicio privado](docs/INICIO_PRIVADO.md) antes de introducir datos.
