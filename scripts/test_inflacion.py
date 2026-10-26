import importlib.util, io, unittest
from datetime import datetime
from pathlib import Path
import openpyxl

spec = importlib.util.spec_from_file_location('extractor', Path(__file__).with_name('extract_inflacion.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class InflationTests(unittest.TestCase):
    def csv(self, extra=''):
        return ('Codigo;Descripcion;Periodo;Indice_IPC;v_m_IPC;v_i_a_IPC;Region\n'
                '0;NIVEL GENERAL;202601;110;2,9;30;Nacional\n'
                '0;NIVEL GENERAL;202602;113;2,7;31;Nacional\n'
                '0;NIVEL GENERAL;202602;999;99;99;GBA\n'+extra).encode('latin-1')

    def xlsx(self, marker='///'):
        w = openpyxl.Workbook(); s = w.active; s.title = 'Evol_gral_bs_svcios'
        s.append(['IPCBA (base 2021 = 100)']);s.append([])
        s.append(['Mes','Indice',None,None,'Variacion'])
        s.append([None,'Nivel General','Bienes','Servicios','Nivel General'])
        s.append([datetime(2026,1,1),100,None,None,marker])
        s.append([datetime(2026,2,1),102,None,None,2])
        b=io.BytesIO();w.save(b);return b.getvalue()

    def test_selects_national_and_published_decimal(self):
        r=mod.parse_indec(self.csv());self.assertEqual(len(r),2)
        self.assertEqual(r[1]['variacion_mensual'],2.7)
        self.assertIsNone(r[0]['fecha_publicacion'])

    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicada'):
            mod.parse_indec(self.csv('0;NIVEL GENERAL;202602;113;2,7;31;Nacional\n'))

    def test_changed_schema_rejected(self):
        with self.assertRaises(ValueError): mod.parse_indec(b'fecha,valor\n2026-01,99\n')

    def test_missing_month_rejected(self):
        with self.assertRaisesRegex(ValueError,'Hueco'):
            mod.parse_indec(self.csv('0;NIVEL GENERAL;202604;120;3;32;Nacional\n'))

    def test_missing_marker_is_not_zero(self):
        r=mod.parse_idecba(self.xlsx());self.assertIsNone(r[0]['variacion_mensual'])
        self.assertIsNone(r[1]['variacion_interanual'])

    def test_invalid_numeric_rejected(self):
        with self.assertRaises(ValueError): mod.parse_idecba(self.xlsx('ilegible'))

    def test_detects_revision_and_blocks_monitor_publication(self):
        blobs={'INDEC':self.csv(),'IDECBA':self.xlsx()};urls={'INDEC':mod.INDEC,'IDECBA':mod.IDECBA}
        previous=mod.build(blobs,urls);previous['observaciones'][0]['indice']=99
        current=mod.build(blobs,urls,previous=previous)
        self.assertEqual(len(current['revisiones_detectadas']),1)
        self.assertTrue(all(not r['publicable_monitor'] for r in current['observaciones']))

    def test_rejects_loss_of_previous_data(self):
        blobs={'INDEC':self.csv(),'IDECBA':self.xlsx()};urls={'INDEC':mod.INDEC,'IDECBA':mod.IDECBA}
        old=mod.build(blobs,urls);old['observaciones'].append({'id':'INDEC_IPC_2025-12'})
        with self.assertRaisesRegex(ValueError,'pierde'):mod.build(blobs,urls,previous=old)

    def test_discovery_rejects_unofficial_link(self):
        with self.assertRaisesRegex(ValueError,'Origen'):
            mod.discover_idecba('<a href="https://evil.example/Evol_gral_bs_svcios.xlsx">X</a>')

if __name__ == '__main__':unittest.main()

