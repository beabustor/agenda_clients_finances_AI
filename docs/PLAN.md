# Producto y plan de desarrollo

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/entradas-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="images/entradas-light.svg">
  <img alt="Cuatro tipos de entrada. Un recorrido controlado." src="images/entradas-light.svg" width="1120" loading="lazy">
</picture>

## Flujo previsto

1. El administrador prepara una instancia privada por autónomo y configura su actividad, régimen fiscal, moneda EUR, zona Europe/Madrid, series y ejercicios.
2. El titular conecta las cuentas y aprueba los permisos de forma individual. La aplicación debe poder funcionar con todas las integraciones desactivadas.
3. Entrada manual, correo, archivos desde ChatGPT o mensajes de WhatsApp producen un documento pendiente, con origen, fecha, identificador externo y huella para evitar duplicados.
4. La extracción propone proveedor, NIF, número de factura, fecha, base, IVA, retención, total y categoría. Documento original y propuesta quedan enlazados.
5. El usuario confirma o corrige antes de contabilizar, mover correos/archivos o enviar información. Registrar cambios y procedencia. Los documentos y correos se tratan como datos, nunca como instrucciones ejecutables.
6. Exportar libros revisados por ejercicio y trimestre para asesoría. Una cita puede vincular cliente y servicio y, más adelante, generar un borrador de factura.

## Integraciones pendientes de implementar

| Canal | Configuración del administrador | Permisos y comportamiento previsto |
| --- | --- | --- |
| Gmail | Proyecto Google Cloud, API Gmail, cliente OAuth, pantalla de consentimiento y URL de retorno | Primero lectura explícita; `gmail.modify` solo al habilitar etiquetas. Gmail usa etiquetas, no carpetas tradicionales. Nunca borrar ni enviar correos por defecto. |
| Drive | API Drive y OAuth del titular | Preferir `drive.file` para archivos creados o seleccionados por la aplicación. Acceder a carpetas existentes puede requerir permisos adicionales y revisión de Google. |
| Calendar | API Google Calendar opcional | Calendario concreto autorizado para citas; contemplar cancelaciones, conflictos, horario de verano e idempotencia. |
| ChatGPT | Elegir herramienta compatible con el plan y autenticación del usuario | Backend HTTPS autenticado con contrato de herramientas y confirmación de escrituras. No usar la cookie o contraseña de ChatGPT. La suscripción no es una clave de API. |
| OpenAI API | Cuenta y presupuesto independientes, solo si se desea extracción automática por API | Clave únicamente en el servidor; minimizar documentos enviados y limitar gasto. |
| WhatsApp | Cuenta Business, número autorizado, aplicación Meta, token y secreto para validar webhooks | Usar plataforma oficial, consentimiento y reglas de plantillas/ventanas vigentes. Verificar firmas, evitar duplicados y descargar medios con autorización. Revisar tarifas. |

Estos ajustes todavía no tienen pantalla ni endpoints. No basta con introducir claves para activar los conectores. Los tokens OAuth deberán guardarse cifrados fuera del repositorio, con revocación y renovación; cada usuario autoriza su cuenta. Una aplicación pública de Google con permisos sensibles/restringidos puede requerir verificación y requisitos adicionales. Comprobar documentación y precios oficiales al implementar cada proveedor.

## Organización propuesta en Drive y correo

Drive: `Mi oficina / EJERCICIO / Facturas emitidas`, `Facturas recibidas`, `Justificantes`, `Exportaciones` y `Citas`. Usar identificadores internos en nombres y evitar NIF u otros datos personales innecesarios. Guardar el vínculo entre archivo y registro.

Gmail: etiquetas `Mi oficina/Pendiente`, `Mi oficina/Revisado`, `Mi oficina/Incidencia`. Mantener los mensajes originales y ofrecer simulación antes de etiquetar por lotes. Las agendas estructuradas irán en Calendar si se activa; Drive conservará sus documentos.

## Contabilidad española

Antes de automatizar, recoger actividad/epígrafe, régimen IRPF e IVA, territorio fiscal y reglas de facturación con la asesoría. Distinguir base, IVA soportado/repercutido, IVA deducible, retenciones y gasto deducible IRPF: un único porcentaje no representa todas estas reglas. Vivienda, suministros, vehículo, dietas, bienes de inversión y uso mixto requieren tratamiento específico y justificantes; no marcar automáticamente como deducibles. Contemplar operaciones exentas, recargo, rectificativas y operaciones internacionales según actividad.

La base actual no es software de facturación certificado ni implementa Veri*Factu. Antes de emitir facturas, revisar obligaciones y calendarios normativos vigentes con fuentes oficiales AEAT y asesoría; no presumir que un Excel cumple todos los requisitos.

## Próximas entregas

1. Modelo relacional: perfil del autónomo, clientes, servicios, citas vinculadas, facturas y líneas, pagos, documentos y auditoría. Edición, búsqueda y eliminación controlada.
2. Usuarios, roles administrador/titular/asesoría, sesiones seguras, HTTPS, cifrado de credenciales, copias y restauración verificadas. Necesario antes de exponer el sistema o recibir datos personales reales.
3. Gmail y Drive: OAuth, importación de prueba, revisión y etiquetado idempotente. Pruebas con cuentas de desarrollo y datos ficticios.
4. Extracción documental opcional, exportación XLSX y libros acordados con asesoría, sin presentación automática de impuestos.
5. Herramientas para ChatGPT y WhatsApp con consentimiento, firma de webhooks y pruebas de aislamiento entre usuarios.

Cada integración deberá probar errores, permisos revocados, documentos duplicados y separación de datos antes de darse por conectada.
