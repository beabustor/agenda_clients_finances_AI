import json
import sqlite3
import unittest
from app.server import validate
from app.agenda import check_links, calendar_proposal

class AgendaTests(unittest.TestCase):
    def test_links_and_calendar_privacy(self):
        db=sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.execute('CREATE TABLE registros(id INTEGER PRIMARY KEY,tipo TEXT,datos TEXT)')
        def add(kind, data):
            fields=validate(kind,data)
            check_links(db,kind,fields)
            return db.execute('INSERT INTO registros(tipo,datos) VALUES (?,?)',(kind,json.dumps(fields))).lastrowid
        client=add('clientes',{'nombre':'Privado'})
        service=add('servicios',{'nombre':'Consulta','base':'50'})
        appointment=add('citas',{'nombre':'Consulta privada','fecha':'2026-11-01T10:00','cliente_id':client,'servicio_id':service,'materiales':'Material confidencial','notas':'Comentario privado','duracion':'45'})
        income=add('ingresos',{'nombre':'Consulta','base':'50','fecha':'2026-11-01','cliente_id':client,'cita_id':appointment,'factura':'F-001'})
        proposal=calendar_proposal(db,appointment)
        self.assertFalse(proposal['enviado'])
        self.assertEqual(proposal['ficha_privada']['contabilidad'][0]['registro_id'],income)
        self.assertEqual(proposal['evento_google']['end']['dateTime'],'2026-11-01T10:45:00+01:00')
        self.assertNotIn('Comentario privado',json.dumps(proposal['evento_google']))
        self.assertEqual(proposal['ficha_privada']['materiales'],'Material confidencial')
        with self.assertRaises(ValueError):
            add('citas',{'nombre':'Cita','fecha':'2026-11-01T10:00','cliente_id':999})
        other=add('clientes',{'nombre':'Otro'})
        with self.assertRaises(ValueError):
            add('ingresos',{'nombre':'Incorrecto','base':'1','fecha':'2026-11-01','cliente_id':other,'cita_id':appointment})
