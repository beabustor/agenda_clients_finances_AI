"""Enrutador determinista de demostración. No ejecuta acciones ni invoca un LLM."""
import unicodedata

def propose(data):
    if not isinstance(data, dict) or set(data) != {'tipo', 'contenido'}:
        raise ValueError('Entrada no válida')
    kind, content = data['tipo'], data['contenido']
    if kind not in ('texto', 'foto', 'audio', 'correo') or not isinstance(content, str) or len(content) > 8000:
        raise ValueError('Tipo o contenido no válido')
    action = 'solicitar_aclaracion'
    missing = []
    reason = 'Describe la acción que deseas realizar.'
    text = ''.join(c for c in unicodedata.normalize('NFD',content.lower()) if unicodedata.category(c) != 'Mn')
    if kind == 'foto':
        missing = ['archivo y extracción OCR verificada']
        reason = 'El procesamiento de imágenes no está conectado.'
    elif kind == 'audio':
        missing = ['archivo y transcripción verificada']
        reason = 'La transcripción de audio no está conectada.'
    elif kind == 'correo':
        missing = ['extracción segura y revisión del titular']
        reason = 'El contenido del remitente no autoriza acciones.'
    elif any(word in text for word in ('elimina','borra')):
        action, missing = 'proponer_eliminacion', ['ID del registro', 'confirmación del titular']
    elif any(word in text for word in ('edita','modifica','cambia')):
        action, missing = 'proponer_edicion', ['ID del registro', 'valores anteriores y nuevos', 'confirmación del titular']
    elif any(word in text for word in ('cita','reserva')):
        action, missing = 'borrador_cita', ['cliente', 'servicio', 'fecha y hora', 'duración', 'comprobación de conflictos']
    elif 'factura' in text and any(word in text for word in ('emite','crea','genera')):
        action, missing = 'borrador_factura', ['emisor', 'destinatario', 'serie', 'líneas e impuestos', 'validación normativa']
    elif any(word in text for word in ('gasto','recibo','factura')):
        action, missing = 'borrador_gasto', ['documento original', 'campos extraídos y revisados']
    elif any(word in text for word in ('ingreso','cobro')):
        action, missing = 'borrador_ingreso', ['documento original', 'campos extraídos y revisados']
    if action != 'solicitar_aclaracion':
        reason = 'Propuesta por palabras clave; revisa la intención. No se ha ejecutado ninguna acción.'
    return dict(accion=action, campos={}, faltantes=missing, requiere_confirmacion=True, motivo=reason, evidencias=[], motor='reglas_demo', ejecutado=False)
