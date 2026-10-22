"""Outbox local y resumen agregado. Nunca simula envíos a proveedores."""
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.agenda import check_links
from app.onboarding import initialize, configuration

KINDS = {'clientes','servicios','citas','ingresos','gastos'}

def init(db):
    initialize(db)
    db.execute('CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY, evento INTEGER NOT NULL UNIQUE, tipo TEXT NOT NULL, registro INTEGER NOT NULL, dia TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS avisos (id INTEGER PRIMARY KEY, accion INTEGER NOT NULL, destino TEXT NOT NULL, canal TEXT NOT NULL, referencia TEXT NOT NULL, mensaje TEXT NOT NULL, estado TEXT NOT NULL, UNIQUE(accion,destino))')

def complete(db, data, validator):
    init(db)
    if not isinstance(data,dict) or set(data) != {'evento','tipo','datos','confirmado'} or data['confirmado'] is not True:
        raise ValueError('Confirma una acción concreta')
    if type(data['evento']) is not int or data['tipo'] not in KINDS:
        raise ValueError('Acción no válida')
    previous = db.execute('SELECT id,registro FROM acciones WHERE evento=?',(data['evento'],)).fetchone()
    if previous:
        return {'accion':previous[0],'registro':previous[1],'duplicado':True}
    event = db.execute('SELECT canal,externo,estado FROM eventos WHERE id=?',(data['evento'],)).fetchone()
    if not event or event[2] != 'pendiente_revision':
        raise ValueError('Entrada no disponible')
    fields = validator(data['tipo'], data['datos'])
    check_links(db, data['tipo'], fields)
    record = db.execute('INSERT INTO registros(tipo,datos) VALUES (?,?)',(data['tipo'],json.dumps(fields,ensure_ascii=False))).lastrowid
    day = datetime.now(timezone.utc).astimezone(ZoneInfo('Europe/Madrid')).date().isoformat()
    action = db.execute('INSERT INTO acciones(evento,tipo,registro,dia) VALUES (?,?,?,?)',(data['evento'],data['tipo'],record,day)).lastrowid
    message = f'Acción {action}: registro de {data["tipo"]} guardado. Revisión fiscal pendiente cuando corresponda.'
    profile = configuration(db) or {}
    # Referencia de hilo provisional: el conector deberá resolver y verificar destinatarios.
    db.execute('INSERT INTO avisos(accion,destino,canal,referencia,mensaje,estado) VALUES (?,?,?,?,?,?)',(action,'hilo_origen',event[0],event[1],message,'pendiente_conector'))
    if profile.get('avisos_usuario', False):
        channel = profile.get('aviso_canal','email')
        reference = profile.get('whatsapp_numero','') if channel == 'whatsapp' else profile.get('email','')
        state = 'pendiente_conector' if reference else 'falta_destino'
        db.execute('INSERT INTO avisos(accion,destino,canal,referencia,mensaje,estado) VALUES (?,?,?,?,?,?)',(action,'copia_usuario',channel,reference,message,state))
    db.execute('UPDATE eventos SET estado=? WHERE id=?',('realizado',data['evento']))
    return {'accion':action,'registro':record,'duplicado':False,'avisos':'pendientes; no enviados'}

def outbox(db):
    init(db)
    return [dict(zip(('id','accion','destino','canal','estado'),row)) for row in db.execute('SELECT id,accion,destino,canal,estado FROM avisos ORDER BY id DESC LIMIT 100')]

def summary(db):
    init(db)
    # Solo fecha, categoría y conteo: sin contenido, clientes, importes ni IDs.
    return {'zona':'Europe/Madrid','detalle':'Agregado; no garantiza anonimato con volúmenes pequeños', 'dias':[{'dia':row[0],'tipo':row[1],'acciones':row[2]} for row in db.execute('SELECT dia,tipo,count(*) FROM acciones GROUP BY dia,tipo ORDER BY dia DESC,tipo')]}
