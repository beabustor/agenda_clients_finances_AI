"""Servidor local de desarrollo; sin dependencias externas."""
from app.agenda import enrich, check_links, calendar_proposal
from app.notifications import complete, outbox, summary
from app.intake import propose
from app.onboarding import configuration, save_configuration, enqueue, events
import csv
import io
import json
import os
import sqlite3
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

STATIC = Path(__file__).parent / 'static'
KINDS = {'clientes', 'servicios', 'citas', 'ingresos', 'gastos'}

def connect():
    path = Path(os.environ.get('AGENDA_DB', 'data/agenda.sqlite3'))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE IF NOT EXISTS registros (id INTEGER PRIMARY KEY, tipo TEXT NOT NULL, datos TEXT NOT NULL)')
    return db

def validate(kind, data):
    if kind not in KINDS or not isinstance(data, dict):
        raise ValueError('Tipo de registro no válido')
    result = {'nombre': str(data.get('nombre', '')).strip()[:200]}
    if not result['nombre']:
        raise ValueError('Escribe un nombre o concepto')
    result['notas'] = str(data.get('notas', ''))[:2000]
    if kind in {'ingresos', 'gastos', 'servicios'}:
        for field, default in [('base', '0'), ('iva', '21'), ('afectacion', '100')]:
            try:
                value = Decimal(str(data.get(field, default)))
                if not value.is_finite() or value < 0 or (field != 'base' and value > 100) or value > 100000000:
                    raise ValueError('Importe o porcentaje fuera de rango')
                result[field] = str(value.quantize(Decimal('0.01')))
            except InvalidOperation as exc:
                raise ValueError('Importe o porcentaje no válido') from exc
        result['revision'] = 'pendiente'
    if kind in {'ingresos', 'gastos'}:
        result['fecha'] = date.fromisoformat(str(data.get('fecha', ''))).isoformat()
        result['factura'] = str(data.get('factura', '')).strip()[:100]
    if kind == 'citas':
        result['fecha'] = datetime.fromisoformat(str(data.get('fecha', ''))).isoformat(timespec='minutes')
    if kind == 'citas':
        duration = data.get('duracion', 60)
        if isinstance(duration, bool) or not str(duration).isdigit() or not 5 <= int(duration) <= 1440:
            raise ValueError('Duración no válida')
        result['duracion'] = int(duration)
    return enrich(data, result)

def records(kind):
    with connect() as db:
        return [dict(id=row[0], **json.loads(row[1])) for row in db.execute('SELECT id, datos FROM registros WHERE tipo=? ORDER BY id DESC', (kind,))]

def export_csv(rows):
    output = io.StringIO(newline='')
    fields = ['id', 'fecha', 'nombre', 'factura', 'base', 'iva', 'afectacion', 'revision', 'notas']
    writer = csv.DictWriter(output, fieldnames=fields, delimiter=';', extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        # Evitar fórmulas al abrir datos de terceros en Excel.
        writer.writerow({key: ("'" + str(value) if str(value).startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else value) for key, value in row.items()})
    return ('\ufeff' + output.getvalue()).encode('utf-8')

class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, mime='application/json; charset=utf-8'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path.startswith('/api/calendar/propuesta/'):
            try:
                ident = int(path.rsplit('/', 1)[1])
                with connect() as db:
                    return self.respond(200, calendar_proposal(db, ident))
            except ValueError:
                return self.respond(404, {'error': 'Cita no encontrada'})
        if path in {'/api/avisos', '/api/admin/resumen', '/exportar/admin-resumen'}:
            with connect() as db:
                return self.respond(200, outbox(db) if path == '/api/avisos' else summary(db))
        if path == '/api/configuracion':
            with connect() as db:
                return self.respond(200, {'perfil': configuration(db), 'modo': 'local', 'conectores_activos': []})
        if path == '/api/eventos':
            with connect() as db:
                return self.respond(200, events(db))
        if path == '/api/registros':
            return self.respond(200, {kind: records(kind) for kind in sorted(KINDS)})
        if path in {'/exportar/ingresos', '/exportar/gastos'}:
            return self.respond(200, export_csv(records(path.rsplit('/', 1)[1])), 'text/csv; charset=utf-8')
        files = {'/': ('admin.html', 'text/html'), '/admin': ('admin.html', 'text/html'), '/admin.html': ('admin.html', 'text/html'), '/gestion': ('index.html', 'text/html'), '/admin.js': ('admin.js', 'text/javascript'), '/admin.css': ('admin.css', 'text/css'), '/app.js': ('app.js', 'text/javascript'), '/setup.js': ('setup.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
        for icon in ('envelope', 'folder', 'chat-dots', 'whatsapp', 'person-circle', 'shield-lock', 'lightning-charge', 'check-circle'):
            files['/icons/' + icon + '.svg'] = ('icons/' + icon + '.svg', 'image/svg+xml')
        if path in files:
            name, mime = files[path]
            return self.respond(200, (STATIC / name).read_bytes(), mime + '; charset=utf-8')
        self.respond(404, {'error': 'No encontrado'})

    def do_POST(self):
        # El navegador debe enviar JSON desde el mismo origen. No se permite CORS.
        if self.headers.get('Content-Type') != 'application/json' or self.headers.get('Sec-Fetch-Site') == 'cross-site':
            return self.respond(403, {'error': 'Solicitud no permitida'})
        if self.path in {'/api/configuracion', '/api/eventos/simular', '/api/entrada/proponer', '/api/acciones/confirmar'}:
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 16384:
                    raise ValueError('Tamaño no válido')
                data = json.loads(self.rfile.read(size))
                with connect() as db:
                    db.execute('BEGIN IMMEDIATE')
                    result = complete(db, data, validate) if self.path == '/api/acciones/confirmar' else propose(data) if self.path == '/api/entrada/proponer' else (save_configuration(db, data) if self.path == '/api/configuracion' else enqueue(db, data))
                return self.respond(200, result)
            except (ValueError, TypeError):
                return self.respond(400, {'error': 'Revisa los campos, la copia privada y los canales seleccionados. No envíes secretos.'})
        kind = self.path.removeprefix('/api/')
        if self.path != '/api/' + kind or kind not in KINDS:
            return self.respond(404, {'error': 'No encontrado'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 16384:
                raise ValueError('Tamaño de solicitud no válido')
            data = validate(kind, json.loads(self.rfile.read(size)))
            with connect() as db:
                check_links(db, kind, data)
                cursor = db.execute('INSERT INTO registros (tipo, datos) VALUES (?, ?)', (kind, json.dumps(data, ensure_ascii=False)))
                ident = cursor.lastrowid
            self.respond(201, dict(id=ident, **data))
        except (ValueError, TypeError):
            self.respond(400, {'error': 'Revisa el concepto, las fechas y los importes'})

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', int(os.environ.get('PORT', '8000'))), Handler)
    print('Panel local iniciado en el puerto ' + str(server.server_port), flush=True)
    server.serve_forever()
