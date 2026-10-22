import json
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from app.server import connect, validate
from app.onboarding import save_configuration, enqueue
from app.notifications import complete, outbox, summary
from app.daily_report import export_reports

class NotificationsTests(unittest.TestCase):
    def test_action_atomic_idempotent_and_minimized(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'AGENDA_DB':folder+'/test.sqlite3'}):
            with connect() as db:
                save_configuration(db,dict(nombre='Nombre privado',actividad='Servicios',repositorio='https://github.com/demo/privado',privado_confirmado=True,canales=['gmail'],email='privado@example.com',avisos_usuario=True,aviso_canal='email'))
                event=enqueue(db,dict(canal='gmail',externo='hilo-secreto',texto='Contenido privado'))
                payload=dict(evento=event['id'],tipo='servicios',datos={'nombre':'Concepto privado','base':'12'},confirmado=True)
                with self.assertRaises(ValueError):
                    complete(db,payload | {'confirmado':False},validate)
                self.assertEqual(outbox(db),[])
                result=complete(db,payload,validate)
                self.assertFalse(result['duplicado'])
                self.assertTrue(complete(db,payload,validate)['duplicado'])
                self.assertEqual(len(outbox(db)),2)
                self.assertTrue(all(row['estado']=='pendiente_conector' for row in outbox(db)))
                self.assertEqual(db.execute('SELECT count(*) FROM registros').fetchone()[0],1)
                report=json.dumps(summary(db))
                for secret in ['privado@example.com','hilo-secreto','Contenido privado','Concepto privado']:
                    self.assertNotIn(secret,report)
                root=Path(folder)/'admin'/'actividad-diaria'
                self.assertEqual(export_reports(db,root),1)
                self.assertEqual(export_reports(db,root),1)
                self.assertEqual(len(list(root.glob('*.json'))),1)
                self.assertEqual(json.loads(next(root.glob('*.json')).read_text())['acciones'][0]['cantidad'],1)
