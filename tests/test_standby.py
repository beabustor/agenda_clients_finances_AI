import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from app.server import connect
from app.onboarding import enqueue
from app.standby import status

class StandbyTests(unittest.TestCase):
    def test_recovery_after_process_exit(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'AGENDA_DB':folder+'/office.sqlite3'}):
            code="""
from app.server import connect
from app.onboarding import save_configuration,enqueue
with connect() as db:
 save_configuration(db,dict(nombre='Demo',actividad='Servicio',repositorio='https://github.com/demo/privado',privado_confirmado=True,canales=['gmail']))
 enqueue(db,dict(canal='gmail',externo='persistente-1',texto='Pendiente tras apagar'))
"""
            subprocess.run([sys.executable,'-c',code],check=True)
            with connect() as db:
                self.assertEqual(status(db)['entradas_pendientes'],1)
                self.assertTrue(enqueue(db,dict(canal='gmail',externo='persistente-1',texto='Reentrega'))['duplicado'])
                self.assertEqual(status(db)['entradas_pendientes'],1)
