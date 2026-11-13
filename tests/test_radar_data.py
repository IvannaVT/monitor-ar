import csv, json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class RadarDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = json.loads((ROOT / 'data/radar_data.json').read_text(encoding='utf-8'))
        with open(ROOT / 'data/radar_trazabilidad.csv', encoding='utf-8') as f:
            cls.T = list(csv.DictReader(f))

    def test_json_regenerado_desde_bases(self):
        r = subprocess.run([sys.executable, 'scripts/build_radar_data.py', '--check'], cwd=ROOT)
        self.assertEqual(r.returncode, 0, 'radar_data.json no coincide con lo que generan las bases')

    def test_icg_octubre_una_sola_vez(self):
        filas = [t for t in self.T if t['ruta'] == 'ICG' and t['mes'] == 'Oct-26']
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]['fila'], '1086')
        self.assertEqual(self.D['ICG'][self.D['MESI'].index('Oct-26')], 1.95)

    def test_isasi_agosto_corregido(self):
        i = self.D['MG'].index('Ago-26')
        self.assertEqual(self.D['GESTION']['Isasi']['aprob'][i], 42)
        self.assertEqual(self.D['GESTION']['Isasi']['desaprob'][i], 48)

    def test_valores_oct_nov_trazados(self):
        trazados = {(t['ruta'], t['mes']) for t in self.T if t['estado'] != 'retirado'}
        for grupo, eje, campos in (('IMG', 'MI', ('pos', 'neg')), ('GESTION', 'MG', ('aprob', 'desaprob')), ('CONS', 'MV', ('lla', 'pj'))):
            for nombre, s in self.D[grupo].items():
                for c in campos:
                    for mes in ('Oct-26', 'Nov-26'):
                        v = s.get(c, [None] * 20)[self.D[eje].index(mes)]
                        if v is not None:
                            self.assertIn((f'{grupo}.{nombre}.{c}', mes), trazados, f'{grupo}.{nombre}.{c} {mes} sin fuente')

    def test_noviembre_parcial_presente(self):
        for eje in ('MESI', 'MI', 'MG', 'MV'):
            self.assertEqual(self.D[eje][-1], 'Nov-26')
        self.assertIn('corte al 12/11', self.D['META']['corte']['etiqueta'])

    def test_html_no_trae_valores_embebidos(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn("fetch('./data/radar_data.json'", html)
        self.assertNotIn('const IMG=', html)
        self.assertNotIn('const GESTION=', html)


if __name__ == '__main__':
    unittest.main()


def test_fuente_secundaria_rotulada():
    """Parte XVI: todo valor de fuente secundaria llega con rótulo y separado en UPD."""
    import json
    from pathlib import Path
    d = json.loads((Path(__file__).resolve().parents[1] / 'data' / 'radar_data.json').read_text())
    sec = [it for t in d['UPD'].values() for its in t.values() for it in its if it.get('secundaria')]
    assert sec, 'se esperaba al menos el IPC sep-26 de monitorargy'
    for it in sec:
        assert it['secundaria'].startswith('FUENTE SECUNDARIA · ')
        assert 'consultado 2026-' in it['secundaria'] and 'fuente original:' in it['secundaria']
