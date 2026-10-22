"""Relaciones locales de agenda y preparación de eventos; sin envío a Google."""
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def enrich(data, result):
    for field in ('cliente_id','servicio_id','cita_id'):
        value=data.get(field)
        if value not in (None,''):
            if isinstance(value,bool) or not str(value).isdigit() or int(value)<1:
                raise ValueError('Referencia no válida')
            result[field]=int(value)
    if 'materiales' in data:
        if not isinstance(data['materiales'],str) or len(data['materiales'])>2000:
            raise ValueError('Materiales no válidos')
        result['materiales']=data['materiales'].strip()
    return result


def check_links(db, kind, fields):
    for name, target in [('cliente_id','clientes'),('servicio_id','servicios'),('cita_id','citas')]:
        if name in fields:
            row=db.execute('SELECT datos FROM registros WHERE id=? AND tipo=?',(fields[name],target)).fetchone()
            if not row:
                raise ValueError('Referencia inexistente: '+name)
            if name=='cita_id' and fields.get('cliente_id') and json.loads(row[0]).get('cliente_id') not in (None,fields['cliente_id']):
                raise ValueError('La cita pertenece a otro cliente')


def calendar_proposal(db, appointment_id):
    row=db.execute("SELECT datos FROM registros WHERE id=? AND tipo='citas'",(appointment_id,)).fetchone()
    if not row:
        raise ValueError('Cita no encontrada')
    item=json.loads(row[0])
    start=datetime.fromisoformat(item['fecha'])
    if start.tzinfo is None:
        start=start.replace(tzinfo=ZoneInfo('Europe/Madrid'))
    end=start+timedelta(minutes=item.get('duracion',60))
    linked=[]
    for record_id,kind,encoded in db.execute("SELECT id,tipo,datos FROM registros WHERE tipo IN ('ingresos','gastos')"):
        record=json.loads(encoded)
        if record.get('cita_id')==appointment_id:
            linked.append({'registro_id':record_id,'tipo':kind,'factura':record.get('factura','')})
    # Sin notas, materiales ni datos fiscales en un calendario potencialmente compartido.
    payload={'summary':f'Cita #{appointment_id}', 'visibility':'private', 'start':{'dateTime':start.isoformat(),'timeZone':'Europe/Madrid'},'end':{'dateTime':end.isoformat(),'timeZone':'Europe/Madrid'},'description':f'Detalles y documentación en la ficha privada de la oficina. Referencia: cita {appointment_id}.','extendedProperties':{'private':{'cita_id':str(appointment_id)}},'reminders':{'useDefault':False}}
    return {'estado':'pendiente_conector','enviado':False,'evento_google':payload,'ficha_privada':{'cita_id':appointment_id,'cliente_id':item.get('cliente_id'),'servicio_id':item.get('servicio_id'),'materiales':item.get('materiales',''),'comentarios':item.get('notas',''),'contabilidad':linked}}
