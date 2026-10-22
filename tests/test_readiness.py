import os
import sqlite3
import unittest
from unittest.mock import patch
from app.readiness import DEFAULT, save, report

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)

    def test_preferences_persist_without_activating(self):
        save(self.db,DEFAULT | {'ia':'api','presupuesto_eur':5})
        result=report(self.db)
        self.assertEqual(result['plan']['ia'],'api')
        self.assertFalse(result['automatizacion_lista'])
        self.assertTrue(any(c['requisito']=='Límite de consumo' and c['estado']=='pendiente_implementacion' for c in result['comprobaciones']))

    def test_presence_does_not_expose_or_validate_secret(self):
        with patch.dict(os.environ,{'GOOGLE_CLIENT_SECRET':'secreto-no-publicar'}):
            result=report(self.db)
        self.assertNotIn('secreto-no-publicar',str(result))
        self.assertTrue(any(c['requisito']=='GOOGLE_CLIENT_SECRET' and c['estado']=='presente_no_verificado' for c in result['comprobaciones']))

    def test_invalid_settings(self):
        for change in [{'presupuesto_eur':0},{'ia':'inventada'},{'intervalo_gmail_min':False},{'whatsapp':'si'},{'secret':'x'}]:
            with self.assertRaises(ValueError):save(self.db,DEFAULT | change)
