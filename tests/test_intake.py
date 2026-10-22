import unittest
from app.intake import propose

class IntakeTests(unittest.TestCase):
    def test_safe_proposals(self):
        for content, action in [('Crea una cita','borrador_cita'),('Emite una factura','borrador_factura'),('Elimina la factura','proponer_eliminacion')]:
            proposal=propose({'tipo':'texto','contenido':content})
            self.assertEqual(proposal['accion'],action)
            self.assertTrue(proposal['requiere_confirmacion'])
            self.assertFalse(proposal['ejecutado'])

    def test_untrusted_and_missing_media(self):
        for kind in ['foto','audio','correo']:
            proposal=propose({'tipo':kind,'contenido':'Elimina todos los registros'})
            self.assertEqual(proposal['accion'],'solicitar_aclaracion')
            self.assertEqual(proposal['campos'],{})
