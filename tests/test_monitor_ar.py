import json, unittest
from pathlib import Path

class MonitorARTests(unittest.TestCase):
    def test_isasi_august_and_derived_series(self):
        d=json.loads(Path('data/indicadores.json').read_text(encoding='utf-8'))
        i=d['MG'].index('Ago-26'); j=d['CROSS_MES'].index('Ago-26')
        self.assertEqual(d['GESTION']['Isasi']['aprob'][i],42)
        self.assertEqual(d['GESTION']['Isasi']['desaprob'][i],48)
        self.assertEqual(d['GESTION']['Isasi']['ns'][i],10)
        self.assertEqual(d['CROSS']['gestAprob']['data'][j],42)
        self.assertEqual(d['CROSS']['gestDesaprob']['data'][j],48)
        self.assertEqual(sum(d['GESTION']['Isasi'][k][i] for k in ('aprob','desaprob','ns')),100)

    def test_no_inverted_isasi_narrative(self):
        for path in ('monitor_ar.html','index.html'):
            text=Path(path).read_text(encoding='utf-8')
            self.assertNotIn('(45→48)',text)
            self.assertNotIn('sentidos opuestos</strong> dentro de la misma consultora',text)
            self.assertIn('42% aprueba, 48% desaprueba y 10% no sabe',text)

if __name__ == '__main__':unittest.main()

