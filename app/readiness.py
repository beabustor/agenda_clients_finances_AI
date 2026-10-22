"""Plan mínimo y diagnóstico sin revelar credenciales ni llamar a proveedores."""
import json
import os
from pathlib import Path

DEFAULT = {'ejecucion':'local','ia':'api','presupuesto_eur':5,'intervalo_gmail_min':5,'whatsapp':False,'chatgpt':False}

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS implantacion (id INTEGER PRIMARY KEY CHECK(id=1), datos TEXT NOT NULL)')

def settings(db):
    initialize(db)
    row=db.execute('SELECT datos FROM implantacion WHERE id=1').fetchone()
    return json.loads(row[0]) if row else DEFAULT.copy()

def save(db, data):
    if not isinstance(data,dict) or set(data)!=set(DEFAULT):
        raise ValueError('Plan no válido')
    if data['ejecucion'] not in ('local','servidor') or data['ia'] not in ('manual','api','local'):
        raise ValueError('Modalidad no válida')
    if type(data['presupuesto_eur']) is not int or not 1 <= data['presupuesto_eur'] <= 100:
        raise ValueError('Presupuesto entre 1 y 100 euros')
    if type(data['intervalo_gmail_min']) is not int or not 1 <= data['intervalo_gmail_min'] <= 60:
        raise ValueError('Intervalo entre 1 y 60 minutos')
    if type(data['whatsapp']) is not bool or type(data['chatgpt']) is not bool:
        raise ValueError('Canal no válido')
    initialize(db)
    db.execute('INSERT INTO implantacion VALUES(1,?) ON CONFLICT(id) DO UPDATE SET datos=excluded.datos',(json.dumps(data),))
    return data

def report(db):
    plan=settings(db)
    checks=[]
    def add(name, status, detail):checks.append({'requisito':name,'estado':status,'detalle':detail})
    add('Panel manual','disponible','Funciona localmente; no necesita una suscripción de ChatGPT.')
    add('Equipo encendido','por_verificar','El proceso debe mantenerse activo; al apagar el equipo se detiene la automatización.')
    for variable in ['GOOGLE_CLIENT_ID','GOOGLE_CLIENT_SECRET']:
        add(variable,'presente_no_verificado' if os.environ.get(variable) else 'falta','Solo se comprueba presencia, no validez ni permisos.')
    token_path=os.environ.get('GOOGLE_TOKEN_FILE')
    add('Tokens OAuth','archivo_presente_no_verificado' if token_path and Path(token_path).is_file() else 'falta','No se leen ni muestran tokens. Autorización del titular y renovación pendientes.')
    add('Gmail + Drive + Calendar + Sheets','pendiente_implementacion','Faltan conectores, consultas periódicas, permisos y prueba real de escritura/lectura.')
    if plan['ia']=='api':
        add('LLM_API_KEY','presente_no_verificado' if os.environ.get('LLM_API_KEY') else 'falta','Cuenta API independiente de ChatGPT Plus.')
        add('Límite de consumo','pendiente_implementacion',f'Objetivo: {plan["presupuesto_eur"]} €/mes. Preferencia guardada; todavía NO bloquea gasto. No activar consumo sin control implementado.')
    elif plan['ia']=='local':
        add('IA local','pendiente_implementacion','Requiere motor, modelo, evaluación de calidad, memoria y rendimiento del equipo; sin garantía de capacidad.')
    else:
        add('IA','desactivada','Entrada y revisión manual; no se procesan fotos ni audios automáticamente.')
    if plan['ejecucion']=='servidor' or plan['chatgpt'] or plan['whatsapp']:
        add('HTTPS + autenticación','pendiente_implementacion','Necesarios antes de acceso remoto, herramientas o webhooks. No exponer el servidor actual.')
    for flag,label in [('chatgpt','Herramienta ChatGPT'),('whatsapp','WhatsApp Business')]:
        add(label,'pendiente_implementacion' if plan[flag] else 'opcional_desactivado','Requiere integración oficial, permisos y pruebas; no se activa con este selector.')
    add('Copias de seguridad','por_verificar','Programar copia privada y comprobar una restauración antes de datos reales.')
    return {'plan':plan,'automatizacion_lista':False,'comprobaciones':checks,'nota':'Diagnóstico de preparación; no se ha comprobado conectividad ni facturación de proveedores.'}

if __name__=='__main__':
    from app.server import connect
    with connect() as db:
        print(json.dumps(report(db),ensure_ascii=False,indent=2))
