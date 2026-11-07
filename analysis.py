"""Reproducible descriptive rules. No learned outcome label or causal claims."""
import pandas as pd

REQUIRED = {'sesi_id','tanggal','jadwal_id','guru_id','kelas_id','mapel_id','tingkat','hari_jadwal','jam_ke','jam_mulai','jam_selesai','jadwal_ditemukan','hari_sesuai','jurnal_n','piket_n','piket_status','review_n','review_nonauto_n','review_auto_n','review_valid_n','rating_sum','rating_mean','review_duplikat_n','guru_absensi_status','guru_absensi_n','jeda_jurnal_jam','absensi_mapel_n','murid_hadir_n','murid_alfa_n'} | {f'rating_{i}_n' for i in range(1,6)}
COUNTS = ['jurnal_n','piket_n','review_n','review_nonauto_n','review_auto_n','review_valid_n','review_duplikat_n','guru_absensi_n','absensi_mapel_n','murid_hadir_n','murid_alfa_n']+[f'rating_{i}_n' for i in range(1,6)]

def validate(df):
 missing=REQUIRED-set(df.columns)
 if missing:raise ValueError('Kolom wajib tidak tersedia: '+', '.join(sorted(missing)))
 if df.empty:raise ValueError('Dataset kosong.')
 if len(df)>200000:raise ValueError('Maksimal 200.000 sesi per unggahan.')
 df=df.copy()
 if df.sesi_id.isna().any() or df.sesi_id.duplicated().any():raise ValueError('ID sesi harus terisi dan unik.')
 dates=pd.to_datetime(df.tanggal,format='%Y-%m-%d',errors='coerce')
 if dates.isna().any():raise ValueError('Tanggal harus valid dalam format YYYY-MM-DD.')
 df['tanggal']=dates.dt.strftime('%Y-%m-%d')
 for c in COUNTS:
  df[c]=pd.to_numeric(df[c],errors='coerce')
  if df[c].isna().any() or (df[c]<0).any() or (df[c]%1!=0).any():raise ValueError(f'{c} harus bilangan bulat nonnegatif.')
  df[c]=df[c].astype(int)
 for c in ['rating_mean','rating_sum','jeda_jurnal_jam']:
  original=df[c];df[c]=pd.to_numeric(original,errors='coerce')
  if (original.notna() & df[c].isna()).any():raise ValueError(f'Nilai {c} tidak numerik.')
 for c in ['jadwal_ditemukan','hari_sesuai']:
  converted=df[c].astype(str).str.lower().map({'true':True,'false':False,'1':True,'0':False})
  if converted.isna().any():raise ValueError(f'{c} harus True/False.')
  df[c]=converted
 if ((df.review_nonauto_n+df.review_auto_n)!=df.review_n).any():raise ValueError('Jumlah review tidak konsisten.')
 if (df.review_valid_n>df.review_nonauto_n).any():raise ValueError('Jumlah rating valid melebihi review nonotomatis.')
 if (df[[f'rating_{i}_n' for i in range(1,6)]].sum(axis=1)!=df.review_valid_n).any():raise ValueError('Distribusi rating tidak konsisten.')
 expected_sum=sum(i*df[f'rating_{i}_n'] for i in range(1,6))
 if df.rating_sum.isna().any() or (abs(expected_sum-df.rating_sum)>0.001).any():raise ValueError('Jumlah nilai rating tidak konsisten.')
 valid=df.review_valid_n>0
 if df.loc[valid,'rating_mean'].isna().any() or (abs(df.loc[valid,'rating_mean']-df.loc[valid,'rating_sum']/df.loc[valid,'review_valid_n'])>0.001).any():raise ValueError('Rata-rata rating tidak konsisten.')
 if df.loc[~valid,'rating_mean'].notna().any():raise ValueError('Tanpa rating valid, rata-rata harus kosong.')
 for c in ['guru_id','kelas_id','mapel_id','tingkat','piket_status','guru_absensi_status','hari_jadwal']:
  df[c]=df[c].fillna('').astype(str)
 return df

def enrich(df,threshold=3.0):
 df=df.copy()
 df['jurnal_ada']=df.jurnal_n>0;df['piket_ada']=df.piket_n>0;df['review_ada']=df.review_valid_n>0
 df['sumber_n']=df[['jurnal_ada','piket_ada','review_ada']].sum(axis=1)
 df['tiga_sumber']=df.sumber_n==3
 def classify(r):
  issues=[]
  if not r.jadwal_ditemukan or not r.hari_sesuai or r.jurnal_n>1 or r.piket_n>1 or r.review_duplikat_n>0:
   issues.append('Periksa pemetaan, hari atau duplikasi')
  if 'Kosong' in r.piket_status:
   issues.append('Piket mencatat Kosong'+('; jurnal juga tersedia' if r.jurnal_n else ''))
  if 'Terlambat' in r.piket_status:issues.append('Piket mencatat keterlambatan')
  if r.review_valid_n and r.rating_mean<threshold:issues.append('Rata-rata rating di bawah ambang eksplorasi')
  if issues: return 'Tinjau catatan','; '.join(issues)
  if r.sumber_n<3:return 'Bukti belum lengkap','Sumber belum tersedia atau belum memiliki rating valid; bukan bukti KBM gagal'
  return 'Tiga sumber tersedia','Kelengkapan tercatat; belum merupakan verifikasi kebenaran pelaksanaan'
 classified=df.apply(classify,axis=1,result_type='expand');df['kategori']=classified[0];df['alasan']=classified[1]
 return df

def summary(df):
 n=len(df);v=int(df.review_valid_n.sum())
 return {'sesi':n,'tiga_sumber':int(df.tiga_sumber.sum()),'tinjau':int((df.kategori=='Tinjau catatan').sum()),'rating':float(df.rating_sum.sum()/v) if v else None,'review_valid':v}
