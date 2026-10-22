# Agenda, Calendar y contabilidad

## Implementado localmente

En `/gestion`, una cita admite cliente y servicio por ID, duración, materiales usados y comentarios (notas). Ingresos y gastos admiten `cita_id`; un ingreso puede incluir una referencia de factura. Se comprueba que las referencias existan y que el cliente indicado en un movimiento no contradiga al cliente de su cita. Una cita no genera ingresos por sí sola.

`GET /api/calendar/propuesta/ID` reúne la ficha y los movimientos asociados, y prepara un evento privado con inicio, fin, zona Europe/Madrid e ID interno estable. **No lo envía a Google.** El evento excluye notas, materiales, nombres y datos fiscales. No configura recordatorios. La ficha local sí contiene estos datos privados.

## Destino previsto: Google Calendar

El administrador indica `calendar_id`; el titular autoriza el acceso. Al completar el conector, las citas confirmadas se almacenarán en ese calendario y se conservarán `calendar_id`, `event_id`, enlace y versión del evento en la base local. El evento enlazará una ficha autenticada con cliente, servicios, materiales, comentarios y documentación contable. El enlace no debe incluir tokens. El campo `calendar_id` es actualmente una preferencia, no una conexión activa.

La factura original estará en Drive y se relacionará por documento y cita. No se copiará información fiscal o comentarios personales a la descripción por defecto. Adjuntar un archivo Drive al evento exigirá verificar sus permisos por separado; compartir un evento no debe compartir automáticamente la factura.

## Contrato pendiente de sincronización

- Antes de crear: validar permisos, fecha, horario de verano y disponibilidad; resolver horas ambiguas y pedir confirmación.
- Crear con clave idempotente y persistir el event_id; un reintento no crea otra cita.
- Cambios desde la agenda o Calendar: comparar versión/etag, detectar conflictos y resolver cancelaciones sin eliminar registros contables.
- Sincronización incremental y renovación de suscripciones; manejo de credenciales revocadas.
- Avisar al hilo únicamente después del éxito de Calendar. La confirmación local no equivale a sincronización.

No existe todavía sincronización bidireccional, adjuntos, envío de invitaciones, recordatorios ni emisión legal de facturas. La propuesta JSON permite desarrollar y probar ese contrato sin simular una conexión.
