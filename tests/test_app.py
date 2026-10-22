import os
import tempfile
import unittest
from unittest.mock import patch
from app.server import connect, records, validate, export_csv

class RecordsTests(unittest.TestCase):
    def test_persistence_and_separation(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'AGENDA_DB': directory+'/test.sqlite3'}):
            import json
            item = validate('gastos', {'nombre':'Electricidad','fecha':'2026-10-22','base':'50.25','iva':'21','afectacion':'30'})
            with connect() as db:
                db.execute('INSERT INTO registros(tipo,datos) VALUES (?,?)', ('gastos',json.dumps(item)))
            self.assertEqual(records('gastos')[0]['base'], '50.25')
            self.assertEqual(records('gastos')[0]['revision'], 'pendiente')
            self.assertEqual(records('ingresos'), [])

    def test_invalid_amounts_and_dates(self):
        for value in ['NaN','Infinity','-1','abc']:
            with self.assertRaises(ValueError):
                validate('servicios', {'nombre':'Servicio','base':value})
        with self.assertRaises(ValueError):
            validate('citas', {'nombre':'Visita','fecha':'no-fecha'})
        with self.assertRaises(ValueError):
            validate('servicios', {'nombre':'Servicio','afectacion':'101'})

    def test_export_neutralizes_formulas(self):
        result = export_csv([{'nombre':'=HYPERLINK("malicioso")','base':'12.00'}]).decode('utf-8-sig')
        self.assertIn("'=HYPERLINK",result)
        self.assertIn('12.00',result)

if __name__ == '__main__':
    unittest.main()
