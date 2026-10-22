"""Configuración local y bandeja de eventos de prueba. Sin conectores externos."""
import json
import re
from datetime import datetime, timezone

CHANNELS = ('gmail', 'chatgpt', 'whatsapp')
FIELDS = ('nombre', 'actividad', 'email', 'repositorio', 'gmail', 'drive_carpeta', 'whatsapp_numero')

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS configuracion (id INTEGER PRIMARY KEY CHECK(id=1), datos TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS eventos (id INTEGER PRIMARY KEY, canal TEXT NOT NULL, externo TEXT NOT NULL, texto TEXT NOT NULL, estado TEXT NOT NULL, creado TEXT NOT NULL, UNIQUE(canal,externo))')

def configuration(db):
    initialize(db)
    row = db.execute('SELECT datos FROM configuracion WHERE id=1').fetchone()
    return json.loads(row[0]) if row else None

def save_configuration(db, data):
    if not isinstance(data, dict) or set(data) - set(FIELDS) - {'canales', 'privado_confirmado'}:
        raise ValueError('Configuración no válida; no envíes secretos')
    result = {}
    for key in FIELDS:
        value = data.get(key, '')
        if not isinstance(value, str) or len(value) > 250:
            raise ValueError('Campo no válido: ' + key)
        result[key] = value.strip()
    if not result['nombre'] or not result['actividad']:
        raise ValueError('Completa el nombre y la actividad')
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?', result['repositorio']):
        raise ValueError('Indica la URL de la copia privada en GitHub')
    if result['repositorio'].rstrip('/').lower() == 'https://github.com/beabustor/agenda_clients_finances_ai':
        raise ValueError('La plantilla pública no puede ser la copia privada')
    if data.get('privado_confirmado') is not True:
        raise ValueError('Confirma que has creado una copia privada')
    channels = data.get('canales', [])
    if not isinstance(channels, list) or any(c not in CHANNELS for c in channels):
        raise ValueError('Canal no válido')
    result.update(canales=sorted(set(channels)), privado_confirmado=True, zona='Europe/Madrid', moneda='EUR')
    initialize(db)
    db.execute('INSERT INTO configuracion VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET datos=excluded.datos', (json.dumps(result),))
    return result

def enqueue(db, data):
    config = configuration(db)
    if not config:
        raise ValueError('Completa primero la configuración')
    if not isinstance(data, dict) or set(data) != {'canal', 'externo', 'texto'}:
        raise ValueError('Evento no válido')
    if data['canal'] not in config['canales']:
        raise ValueError('Canal no seleccionado')
    for key, limit in [('externo', 200), ('texto', 4000)]:
        if not isinstance(data[key], str) or not data[key].strip() or len(data[key]) > limit:
            raise ValueError('Identificador o texto no válido')
    cursor = db.execute('INSERT OR IGNORE INTO eventos(canal,externo,texto,estado,creado) VALUES (?,?,?,?,?)', (data['canal'], data['externo'], data['texto'], 'pendiente_revision', datetime.now(timezone.utc).isoformat()))
    row = db.execute('SELECT id,estado FROM eventos WHERE canal=? AND externo=?', (data['canal'], data['externo'])).fetchone()
    return {'id': row[0], 'estado': row[1], 'duplicado': cursor.rowcount == 0}

def events(db):
    initialize(db)
    return [dict(zip(('id','canal','externo','texto','estado','creado'), row)) for row in db.execute('SELECT id,canal,externo,texto,estado,creado FROM eventos ORDER BY id DESC LIMIT 100')]
