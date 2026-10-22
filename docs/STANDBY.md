# Apagado y recuperación

## Lo que ya está recibido

Las entradas confirmadas por la API, los registros, preferencias y avisos se guardan en SQLite. Al reiniciar la aplicación con la misma base vuelven a aparecer; no se descartan por cerrar el navegador o apagar el ordenador. La ruta por defecto es `data/agenda.sqlite3` dentro del proyecto, independiente del directorio de arranque. Si se utiliza AGENDA_DB, mantener siempre la misma ruta absoluta. La interfaz del admin muestra los pendientes.

Las transacciones confirman datos antes de responder éxito. SQLite usa sincronización FULL; una operación interrumpida antes de commit se revierte. Si la respuesta se pierde después de commit, el emisor debe repetir el mismo ID externo: se deduplica la entrada. Confirmar de nuevo una acción ya completada no repite su registro ni sus avisos. Los daños de disco o la eliminación de la carpeta siguen requiriendo copias de seguridad.

Reabrir la aplicación **no ejecuta automáticamente** IA, envíos o conectores aún no implementados, ni aprueba borradores. Recupera la bandeja para continuar. El inicio automático con el sistema operativo todavía no está instalado; actualmente se arranca `python3 -m app.server`.

## Lo que llega con el ordenador apagado

| Canal | Dónde espera | Requisito pendiente |
| --- | --- | --- |
| Gmail | En la cuenta de Gmail, mientras se conserve el mensaje | Conector con cursor persistido y recuperación incremental, sin depender solo de «no leído» |
| ChatGPT | No existe una cola genérica garantizada de llamadas fallidas | Avisar de indisponibilidad y reintentar con el mismo ID; nunca anunciar éxito sin recibo |
| WhatsApp Business | El proveedor puede reintentar webhooks según sus condiciones, sin garantía ilimitada | Para apagados prolongados, receptor HTTPS y cola duradera externos |
| Fotos/audio subidos a la app | Solo si terminó y se confirmó la recepción | Subidas y almacenamiento de adjuntos todavía pendientes |

No es posible garantizar que un equipo apagado reciba mensajes. Para conservar el modelo sin alojamiento, la primera implantación puede usar Gmail como entrada persistente. Garantizar WhatsApp/ChatGPT durante apagados requiere infraestructura externa; podría añadir costes. No hay automatización Google real todavía.
