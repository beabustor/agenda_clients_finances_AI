import sqlite3
import unittest
from app.onboarding import save_configuration, configuration, enqueue, events

class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.profile = dict(nombre='Ejemplo', actividad='Servicios', repositorio='https://github.com/ejemplo/oficina', privado_confirmado=True, canales=['gmail'])

    def tearDown(self):
        self.db.close()

    def test_private_copy_required(self):
        for change in [{'privado_confirmado':False}, {'repositorio':'https://github.com/beabustor/agenda_clients_finances_AI'}, {'repositorio':'https://github.com/ejemplo/oficina?token=secreto'}, {'token':'secreto'}]:
            with self.assertRaises(ValueError):
                save_configuration(self.db, self.profile | change)
        self.assertIsNone(configuration(self.db))

    def test_persistence_and_update(self):
        save_configuration(self.db,self.profile)
        save_configuration(self.db,self.profile | {'nombre':'Actualizado'})
        self.assertEqual(configuration(self.db)['nombre'],'Actualizado')
        self.assertEqual(self.db.execute('SELECT count(*) FROM configuracion').fetchone()[0],1)

    def test_deduplication_and_channel_selection(self):
        event = dict(canal='gmail', externo='id-1', texto='Factura ficticia')
        with self.assertRaises(ValueError):
            enqueue(self.db,event)
        save_configuration(self.db,self.profile)
        self.assertFalse(enqueue(self.db,event)['duplicado'])
        self.assertTrue(enqueue(self.db,event)['duplicado'])
        self.assertEqual(len(events(self.db)),1)
        self.assertEqual(events(self.db)[0]['estado'],'pendiente_revision')
        with self.assertRaises(ValueError):
            enqueue(self.db,event | {'canal':'whatsapp'})
