import unittest
from pathlib import Path
import pandas as pd
from analysis import validate,enrich,summary
ROOT=Path(__file__).resolve().parent
class AnalysisTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.df=validate(pd.read_csv(ROOT/'data/sessions.csv'))
 def test_missing_attendance_not_absent(self):
  x=self.df.iloc[[0]].copy()
  x['guru_absensi_n']=0;x['guru_absensi_status']='';x['jurnal_n']=1;x['piket_n']=1;x['piket_status']='Tepat Waktu';x['review_valid_n']=1;x['rating_mean']=5;x['hari_sesuai']=True;x['jadwal_ditemukan']=True;x['review_duplikat_n']=0
  self.assertEqual(enrich(x).iloc[0].kategori,'Tiga sumber tersedia')
 def test_auto_reviews_do_not_complete_sources(self):
  x=self.df.iloc[[0]].copy();x['review_valid_n']=0;x['review_auto_n']=20;x['rating_mean']=float('nan')
  self.assertFalse(enrich(x).iloc[0].tiga_sumber)
 def test_weighted_rating(self):
  x=self.df.iloc[:2].copy();x['review_valid_n']=[1,9];x['rating_sum']=[1,45]
  self.assertAlmostEqual(summary(enrich(x))['rating'],4.6)
 def test_reject_duplicate_ids_and_inconsistent_counts(self):
  with self.assertRaises(ValueError):validate(pd.concat([self.df.iloc[:1],self.df.iloc[:1]]))
  x=self.df.iloc[:1].copy();x['review_n']=x.review_n+1
  with self.assertRaises(ValueError):validate(x)
 def test_no_rating_is_not_zero(self):
  x=self.df.iloc[:1].copy();x['review_valid_n']=0;x['rating_sum']=0
  self.assertIsNone(summary(enrich(x))['rating'])
 def test_fully_empty_sources_not_fabricated(self):
  self.assertTrue(((self.df.jurnal_n+self.df.piket_n+self.df.review_n)>0).all())
 def test_dataset_unique_keys(self):
  self.assertFalse(self.df[['jadwal_id','tanggal']].duplicated().any())
class AppTests(unittest.TestCase):
 def test_app_and_filters(self):
  from streamlit.testing.v1 import AppTest
  app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
  self.assertEqual(len(app.exception),0)
  self.assertEqual(len(app.tabs),5)
  self.assertEqual(len(app.metric),7)
  app.slider[0].set_value(4.0).run()
  self.assertEqual(len(app.exception),0)
  app.multiselect[0].set_value([app.multiselect[0].options[0]]).run()
  self.assertEqual(len(app.exception),0)
  app.selectbox[0].set_value('Bukti belum lengkap').run()
  self.assertEqual(len(app.exception),0)
  app.radio[0].set_value('Unggah CSV sesi').run()
  self.assertEqual(len(app.exception),0)
  self.assertEqual(len(app.file_uploader),1)
if __name__=='__main__':unittest.main()
