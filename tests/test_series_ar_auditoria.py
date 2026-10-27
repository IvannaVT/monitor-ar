import json, unittest
from pathlib import Path

class SeriesAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(Path('data/series_ar_auditoria.json').read_text(encoding='utf-8'))

    def test_only_three_consecutive_publications_enter(self):
        rows=self.data['tabla_publicacion_habilitada']
        groups={r['grupo_id'] for r in rows}
        self.assertEqual(len(groups),3)
        for group in groups:
            months=sorted({r['mes_publicacion'] for r in rows if r['grupo_id']==group})
            numbers=[int(m[:4])*12+int(m[5:]) for m in months]
            self.assertGreaterEqual(len(numbers),3)
            self.assertTrue(all(b-a==1 for a,b in zip(numbers,numbers[1:])))

    def test_publication_and_reference_are_not_conflated(self):
        rows=[r for r in self.data['tabla_publicacion_habilitada'] if r['mes_publicacion']=='2026-10']
        self.assertEqual(len(rows),3)
        self.assertTrue(all(r['periodo_dato']=='2026-09' for r in rows))

    def test_deltas_are_contiguous_not_last_available(self):
        for source,month,value,delta in [('tabla_candidatas','mes_periodo','valor','delta_periodo'),('tabla_publicacion_habilitada','mes_publicacion','valor','delta')]:
            rows=self.data[source]
            for row in rows:
                y,m=map(int,row[month].split('-')); previous=f'{y if m>1 else y-1:04d}-{m-1 if m>1 else 12:02d}'
                before=[r for r in rows if r['grupo_id']==row['grupo_id'] and r[month]==previous]
                if before:
                    self.assertAlmostEqual(row[delta],row[value]-before[0][value])
                else:self.assertIsNone(row[delta])

    def test_all_rows_have_traceable_evidence(self):
        for source in ('tabla_candidatas','tabla_publicacion_habilitada'):
            for row in self.data[source]:
                self.assertTrue(row['observacion_id'])
                self.assertTrue(row['fuente_id'])
                if source=='tabla_publicacion_habilitada':self.assertIsInstance(row['pagina'],(int,float))
                elif not isinstance(row['pagina'],(int,float)):
                    self.assertFalse(row['evidencia_localizada'])
                    self.assertIn('página pendiente',row['estado'])
                    self.assertFalse(row['publicable_serie'])
                self.assertTrue(row['url'].startswith('https://'))

    def test_audit_is_not_claimed_exhaustive(self):
        self.assertFalse(self.data['resumen']['cotejo_exhaustivo_de_todos_los_informes'])
        self.assertEqual(self.data['resumen']['diferencias_entre_capas'],0)

    def test_pending_candidates_are_not_published_series(self):
        for row in self.data['tabla_candidatas']:
            if row['estado']!='Habilitada por publicación':self.assertFalse(row['publicable_serie'])

if __name__=='__main__':unittest.main()
