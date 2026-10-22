# Primera implantación: ordenador local + API de IA

Decisión: equipo de la usuaria encendido, sin alojamiento de pago, y extracción con API. No se necesita ChatGPT Plus para que el servidor llame a una API de IA. El canal de conversación ChatGPT es una integración distinta y opcional.

## Mínimos del titular y administrador

| Necesidad | Qué preparar | Coste o condición |
| --- | --- | --- |
| Equipo | Python 3.12+, disco privado, Internet y proceso encendido | Sin alquiler de servidor; usa recursos del equipo |
| Google | Cuenta del titular, proyecto Cloud, APIs Gmail/Drive/Calendar/Sheets y cliente OAuth de escritorio | Comprobar cuotas, almacenamiento y condiciones vigentes; no implica Workspace de pago obligatorio |
| Permisos | Autorizar correo, calendario y archivos necesarios | El administrador no necesita la contraseña del usuario |
| IA | Elegir API OpenAI o Anthropic, clave de proyecto y modelo | Consumo separado de Plus; precio según modelo y volumen |
| Límite | Propuesta inicial: 5 €/mes, editable y pendiente de aceptación | No es una estimación ni límite efectivo todavía |
| Seguridad | Sesión del sistema protegida, tokens cifrados y copias privadas restaurables | Requisito previo a datos reales |

## Funcionamiento mínimo que se implementará

Gmail se consultará cada 5 minutos mientras esté encendido el equipo, evitando un webhook público y Pub/Sub en esta primera versión. Al volver a encender, recuperará el trabajo pendiente mediante un cursor persistido. Los documentos entrarán en una cola local con deduplicación; la API propondrá campos; el titular confirmará antes de escribir en Drive/Sheets/Calendar. Un error de aviso no repetirá la escritura contable.

No hace falta alojar una web pública para este flujo de Google. ChatGPT como entrada y WhatsApp requieren endpoints accesibles/autenticados y quedan fuera del mínimo. No exponer el servidor actual mediante un túnel sin implementar seguridad. Audio y fotos requieren adaptadores específicos y pruebas: seleccionar «API» no los activa.

## Proveedor y orquestación

OpenAI y Anthropic son alternativas, no dos suscripciones obligatorias. n8n es opcional. [Comparación y arquitectura](IA_Y_N8N.md).

## Control de consumo necesario antes de usar IA

El presupuesto del panel es hoy una preferencia, **no un bloqueo**. Antes de habilitar llamadas, implementar:

1. Libro de consumo mensual persistente y límite por instancia.
2. Reserva atómica del coste máximo antes de cada llamada, incluyendo reintentos y peticiones simultáneas.
3. Límites de tamaño, páginas, tokens y llamadas por documento. Fijar modelo y tarifas verificadas; si no pueden estimarse, bloquear la llamada.
4. Reconciliar consumo real y convertir moneda con criterio documentado. Al alcanzar el límite, pasar a captura manual sin perder documentos.
5. Configurar alertas y límites del proveedor cuando existan. Una alerta del proveedor por sí sola no garantiza un tope de facturación. Considerar también impuestos y otros clientes que usen la misma cuenta.

## Preparación disponible

- Panel «El mínimo para empezar»: modalidad, presupuesto objetivo, intervalo y canales opcionales.
- `python3 -m app.readiness`: diagnóstico de requisitos y presencia de variables, sin mostrar valores ni autenticar proveedores.
- `config/conexiones.example.env`: nombres de configuración. No introducir claves en ese archivo público; usar entorno o gestor privado. No se carga automáticamente.

Los conectores, almacenamiento cifrado, worker y límite efectivo siguen pendientes. El diagnóstico nunca anuncia automatización lista solo porque haya claves.

## Prueba de aceptación antes de la implantación

- Autorizar y revocar Google; comprobar renovación de sesión y acceso solo a la cuenta prevista.
- Importar una factura ficticia y repetirla sin duplicar registros ni llamadas de IA.
- Confirmar borrador; verificar archivo, hoja y evento Calendar realmente creados y relacionados.
- Cortar Internet, reiniciar y recuperar sin perder ni duplicar trabajo.
- Forzar agotamiento del presupuesto: cero nuevas llamadas y alternativa manual.
- Comprobar el aviso, resumen mínimo y restauración de backup.

## Fuentes para configurar

- Google OAuth para aplicaciones instaladas: https://developers.google.com/identity/protocols/oauth2/native-app
- APIs de Workspace: https://developers.google.com/workspace
- Precios OpenAI API: https://openai.com/api/pricing/
- Marca Google: https://about.google/brand-resource-center/

No se han validado precios ni permisos de una cuenta real en este entorno. Se comprobarán con el titular al implementar y conectar.
