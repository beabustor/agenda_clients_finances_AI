# Avisos y actividad diaria

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/avisos-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="images/avisos-light.svg">
  <img alt="Guardar una vez. Avisar sin duplicar." src="images/avisos-light.svg" width="1120" loading="lazy">
</picture>

## Funcionamiento local implementado

1. El administrador configura correo, canal de copia del usuario y preferencia de avisos.
2. Una entrada queda pendiente; todavía no genera «acción realizada».
3. `POST /api/acciones/confirmar` recibe evento, tipo, datos y confirmación explícita. Valida y guarda un registro real, marca el evento realizado y crea los avisos en la misma transacción. Solo admite una acción por evento en esta versión; repetir la confirmación devuelve el resultado existente.
4. El admin puede probarlo creando un servicio ficticio de 0 € desde una entrada de la bandeja. No crea facturas ni determina impuestos.
5. `GET /api/avisos` muestra estado de avisos. Se encolan respuesta al hilo y copia opcional por email/WhatsApp al destino configurado. No se marcan como enviados. La referencia de origen aún debe ser resuelta y verificada por el conector.
6. El resumen agrupa acciones por fecha Europe/Madrid y categoría, sin contenido ni identificadores. `python3 -m app.daily_report` guarda un JSON por día en `data/admin/actividad-diaria/` (o junto a AGENDA_DB). Es repetible y se puede programar diariamente; todavía no hay un planificador instalado. El front permite descargar el resumen completo.

## Entrega externa pendiente

Gmail necesitará `threadId`, cabeceras Message-ID/In-Reply-To/References y permiso de envío. Solo responder a remitentes y destinos verificados, evitando respuestas automáticas en bucle. WhatsApp necesitará identidad del remitente verificada, número Business, reglas de ventana/plantilla y, cuando se admita, contexto del mensaje original. ChatGPT recibe el resultado en la misma llamada autenticada de la herramienta; no hay correo ChatGPT ni envío proactivo genérico a una conversación.

La carpeta de administración es local; mover los resúmenes a una carpeta Drive o etiqueta Gmail y enviarlos al correo admin requiere los conectores. El correo admin guardado es una preferencia, no prueba de entrega. El transporte deberá implementar reintentos limitados, idempotencia, firma de webhooks y recibos de entrega sin reejecutar la acción. No se envía nada fuera en esta versión.

## Privacidad

Los resúmenes son **agregados**, no garantizan anonimato: con pocos usuarios o acciones puede inferirse actividad. No contienen nombres, correos, números, textos, importes ni IDs. La cola de entrega sí conserva referencias privadas necesarias para responder; mantenerla restringida y fuera de Git. Definir retención y consentimiento antes de conectar cuentas reales. El servidor sigue siendo local sin autenticación; no exponerlo a Internet.
