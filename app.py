from pathlib import Path
import json, io, html
import pandas as pd
import altair as alt
import streamlit as st
from analysis import validate,enrich,summary
ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='KBM Evidence Explorer',page_icon='📘',layout='wide')
st.markdown('''<style>
.stApp {background:#f7f9fc;color:#18334b} .block-container {max-width:1280px;padding-top:2.2rem}
h1,h2,h3 {letter-spacing:-.025em} [data-testid="stMetric"] {background:white;border:1px solid #dfe7ed;border-radius:12px;padding:16px}
.eyebrow {color:#16716f;font-size:12px;letter-spacing:.16em;font-weight:700;margin-bottom:9px}
.hero {border-bottom:1px solid #dce5eb;padding:8px 0 22px;margin-bottom:20px}.hero h1 {font-size:38px;margin:0;color:#17334a}.hero p {max-width:800px;color:#536878;line-height:1.65}
</style>''',unsafe_allow_html=True)
@st.cache_data
def bundled():
 return validate(pd.read_csv(ROOT/'data/sessions.csv')),json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
try:base,meta=bundled()
except Exception as e:st.error('Dataset bawaan tidak dapat dibaca: '+str(e));st.stop()
with st.sidebar:
 st.markdown('### KBM Evidence Explorer')
 st.caption('Arbi Muhammad Fajar · LK26 R1\n\n072926010 · Magister Ilmu Komputer\n\nUniversitas Pakuan')
 st.divider()
 mode=st.radio('Sumber data',['Demo dari SQL','Unggah CSV sesi'])
 if mode=='Unggah CSV sesi':
  upload=st.file_uploader('Gunakan struktur sessions.csv',type=['csv'])
  st.caption('CSV dibaca sebagai data, tidak dieksekusi. Batas 50 MB dan 200.000 sesi. Jangan unggah identitas pribadi.')
  if upload is None:st.info('Pilih CSV untuk melanjutkan.');st.stop()
  try:
   if upload.size>50_000_000:raise ValueError('Ukuran melampaui 50 MB.')
   base=validate(pd.read_csv(upload));meta={**meta,'dataset_kind':'uploaded_unverified','provenance':'CSV pengguna: asal, izin, dan kelengkapan belum diverifikasi.'}
  except Exception as e:st.error('CSV ditolak: '+str(e));st.stop()
 st.divider()
 dates=pd.to_datetime(base.tanggal)
 selected=st.date_input('Periode catatan',(max(dates.min(),dates.max()-pd.Timedelta(days=89)).date(),dates.max().date()),min_value=dates.min().date(),max_value=dates.max().date())
 levels=st.multiselect('Tingkat',sorted(x for x in base.tingkat.unique() if x))
 classes=st.multiselect('Kode kelas',sorted(x for x in base.kelas_id.unique() if x))
 threshold=st.slider('Ambang rating untuk ditinjau',1.0,5.0,3.0,0.5)
 st.caption('Aturan eksplorasi, bukan skor prediksi atau label kinerja guru.')
 if st.button('Bersihkan cache'):st.cache_data.clear();st.rerun()
st.markdown('<div class="hero"><div class="eyebrow">METODE PENELITIAN / ANALITIK MULTISUMBER</div><h1>Telusuri bukti pelaksanaan KBM</h1><p>Jurnal guru, observasi piket, dan review murid dalam satu ruang analisis. Mulai dari cakupan catatan, lalu periksa bukti setiap sesi.</p></div>',unsafe_allow_html=True)
if meta['dataset_kind']=='dummy':st.warning('DATA UJI / DUMMY — dikonfirmasi pemilik data. Grafik dan pola di sini merupakan demonstrasi, bukan temuan operasional sekolah atau hasil tesis.')
else:st.warning('DATA UNGGAHAN — asal dan izin belum diverifikasi. Ringkasan dihitung hanya dari CSV yang dipilih.')
st.caption('Unit: satu ID jadwal + tanggal yang memiliki minimal satu catatan sumber. Bukan seluruh pertemuan wajib. Review tanpa penanda otomatis belum tentu berasal dari manusia.')
if len(selected)!=2:st.info('Lengkapi tanggal awal dan akhir.');st.stop()
start,end=map(str,selected)
df=base[(base.tanggal>=start)&(base.tanggal<=end)].copy()
if levels:df=df[df.tingkat.isin(levels)]
if classes:df=df[df.kelas_id.isin(classes)]
if df.empty:st.info('Tidak ada sesi untuk kombinasi filter ini. Ubah periode atau pilihan kelas.');st.stop()
df=enrich(df,threshold);m=summary(df)
a,b,c,d=st.columns(4)
a.metric('Sesi tercatat',f'{m["sesi"]:,}')
b.metric('Tiga sumber tersedia',f'{m["tiga_sumber"]/m["sesi"]:.1%}',help=f'{m["tiga_sumber"]:,} dari {m["sesi"]:,} sesi. Review harus memiliki rating valid dan tidak bertanda otomatis.')
c.metric('Catatan untuk ditinjau',f'{m["tinjau"]:,}',help='Aturan eksplorasi: masalah pemetaan, duplikasi, status Kosong/Terlambat, atau rating di bawah ambang.')
d.metric('Rating / 5',f'{m["rating"]:.2f}' if m['rating'] is not None else 'Tidak tersedia',help=f'Rata-rata tertimbang {m["review_valid"]:,} rating valid tanpa penanda auto-review; semua data bawaan tetap dummy.')
st.caption(f'Periode terpilih {start} sampai {end} · {df.guru_id.replace("",pd.NA).nunique()} kode guru · {df.kelas_id.replace("",pd.NA).nunique()} kode kelas')
overview,detail,quality,method,downloads=st.tabs(['Ringkasan','Telusuri sesi','Kualitas data','Metode penelitian','Data & unduhan'])
with overview:
 left,right=st.columns([1.3,1])
 with left:
  st.subheader('Cakupan sumber pada sesi tercatat')
  cov=pd.DataFrame({'Sumber':['Jurnal guru','Patroli piket','Review valid non-auto'],'Sesi':[int(df.jurnal_ada.sum()),int(df.piket_ada.sum()),int(df.review_ada.sum())]})
  chart=alt.Chart(cov).mark_bar(color='#16716f',cornerRadiusEnd=4).encode(x=alt.X('Sesi:Q',title='Jumlah sesi (catatan)'),y=alt.Y('Sumber:N',title=None,sort=None),tooltip=['Sumber','Sesi']).properties(height=230)
  st.altair_chart(chart,use_container_width=True)
  st.caption(f'Penyebut: {len(df):,} sesi dalam filter. Ketiadaan laporan tidak menyatakan KBM tidak berlangsung.')
 with right:
  st.subheader('Komposisi catatan')
  counts=df.kategori.value_counts().rename_axis('Kategori').reset_index(name='Sesi')
  st.dataframe(counts,hide_index=True,use_container_width=True)
  st.info('Tiga sumber tersedia menunjukkan kelengkapan. Isi ketiganya tidak selalu mengukur konstruk yang sama.')
 st.subheader('Cakupan pencatatan per minggu')
 trend=df.assign(Minggu=pd.to_datetime(df.tanggal).dt.to_period('W-SUN').dt.start_time).groupby('Minggu').agg(sesi=('sesi_id','size'),jurnal=('jurnal_ada','sum'),piket=('piket_ada','sum'),review=('review_ada','sum')).reset_index()
 for col in ['jurnal','piket','review']:trend[col]=100*trend[col]/trend.sesi
 long=trend.melt(id_vars=['Minggu','sesi'],value_vars=['jurnal','piket','review'],var_name='Sumber',value_name='Persentase')
 line=alt.Chart(long).mark_line(point=True).encode(x=alt.X('Minggu:T',title='Awal minggu (tanggal)'),y=alt.Y('Persentase:Q',title='Sesi dengan sumber (%)',scale=alt.Scale(domain=[0,100])),color=alt.Color('Sumber:N',title='Sumber',scale=alt.Scale(range=['#16716f','#315b9d','#bc7a25'])),tooltip=['Minggu:T','Sumber','Persentase','sesi']).properties(height=280)
 st.altair_chart(line,use_container_width=True)
 st.caption('Sumber: agregasi catatan pada filter aktif. Persentase bukan tingkat keterlaksanaan seluruh jadwal.')
 left,right=st.columns(2)
 with left:
  st.subheader('Distribusi rating valid')
  ratings=pd.DataFrame({'Rating':list(range(1,6)),'Respons':[int(df[f'rating_{i}_n'].sum()) for i in range(1,6)]})
  st.altair_chart(alt.Chart(ratings).mark_bar(color='#315b9d').encode(x=alt.X('Rating:O',title='Rating (skala 1–5)'),y=alt.Y('Respons:Q',title='Jumlah respons'),tooltip=['Rating','Respons']).properties(height=220),use_container_width=True)
 with right:
  st.subheader('Catatan piket')
  statuses=df[df.piket_ada].piket_status.value_counts().rename_axis('Status').reset_index(name='Sesi')
  st.dataframe(statuses,hide_index=True,use_container_width=True)
  st.caption('Gabungan status dipertahankan bila satu sesi memiliki lebih dari satu catatan piket. Rating tidak diterjemahkan menjadi status hadir/tidak hadir.')
with detail:
 st.subheader('Periksa alasan, lalu telusuri sumber')
 category=st.selectbox('Kategori sesi',['Semua']+sorted(df.kategori.unique().tolist()))
 subset=df if category=='Semua' else df[df.kategori==category]
 cols=['sesi_id','tanggal','kelas_id','mapel_id','guru_id','jam_ke','jurnal_n','piket_status','review_valid_n','rating_mean','kategori','alasan']
 st.caption(f'Menampilkan maksimal 1.000 dari {len(subset):,} sesi; unduhan menyertakan seluruh hasil filter.')
 st.dataframe(subset[cols].head(1000),hide_index=True,use_container_width=True,height=340)
 options=subset.sort_values(['tanggal','sesi_id'],ascending=[False,True]).head(500)
 if len(subset)>500:st.caption('Pemilih detail menampilkan 500 sesi terbaru; persempit filter untuk sesi lain. Tabel dan unduhan tetap memuat seluruh hasil filter.')
 sid=st.selectbox('Pilih ID sesi',options.sesi_id.tolist())
 row=df[df.sesi_id==sid].iloc[0]
 st.markdown(f'**{row.tanggal} · {row.kelas_id} · {row.mapel_id}**')
 st.info(row.alasan)
 x,y,z=st.columns(3)
 x.metric('Catatan jurnal',int(row.jurnal_n));y.metric('Catatan piket',int(row.piket_n));z.metric('Review valid non-auto',int(row.review_valid_n))
 st.dataframe(pd.DataFrame({'Indikator':['ID jadwal','Kode guru','Jam mulai','Jam selesai','Status piket','Status absensi guru','Review bertanda otomatis','Duplikat review siswa-sesi','Jeda jurnal paling awal (jam)','Catatan absensi mapel','Status hari jadwal'],'Nilai':[row.jadwal_id,row.guru_id,str(row.jam_mulai),str(row.jam_selesai),row.piket_status or 'Tidak tersedia',row.guru_absensi_status or 'Tidak tersedia',str(row.review_auto_n),str(row.review_duplikat_n),str(row.jeda_jurnal_jam) if pd.notna(row.jeda_jurnal_jam) else 'Tidak tersedia',str(row.absensi_mapel_n),'Sesuai' if row.hari_sesuai else 'Periksa pemetaan']}),hide_index=True,use_container_width=True)
 st.caption('Jeda memakai created_at, bukan bukti pasti waktu pengisian manusia. Nilai negatif dipertahankan untuk pemeriksaan. Pencocokan review menggunakan ID jadwal yang tersimpan tanpa menyebarkannya ke jam lain.')
with quality:
 st.subheader('Pemeriksaan pada data terpilih')
 checks={'Sesi tanpa referensi jadwal':int((~df.jadwal_ditemukan).sum()),'Sesi dengan hari tidak sesuai jadwal':int((df.jadwal_ditemukan&~df.hari_sesuai).sum()),'Sesi dengan lebih dari satu jurnal':int((df.jurnal_n>1).sum()),'Sesi dengan lebih dari satu catatan piket':int((df.piket_n>1).sum()),'Tambahan review siswa-sesi yang berulang':int(df.review_duplikat_n.sum()),'Review bertanda otomatis':int(df.review_auto_n.sum()),'Rating non-auto di luar 1–5':int((df.review_nonauto_n-df.review_valid_n).sum()),'Sesi dengan jeda jurnal negatif':int((df.jeda_jurnal_jam<0).sum()),'Sesi tanpa catatan absensi guru':int((df.guru_absensi_n==0).sum())}
 st.dataframe(pd.DataFrame(checks.items(),columns=['Pemeriksaan','Jumlah']),hide_index=True,use_container_width=True)
 st.markdown('''**Batas interpretasi**
- Data bawaan adalah dummy; seeder rating menggunakan informasi piket dan absensi. Korelasi bukan bukti independen.
- Tidak ada kalender hari efektif atau riwayat pembatalan tervalidasi. Sesi tanpa semua sumber tidak dapat dihitung dari dataset ini.
- Dashboard murid Laravel mengelompokkan jadwal per mata pelajaran. Satu review dapat mewakili beberapa jam; pencocokan konservatif tetap memakai ID tersimpan.
- Penanda `Auto-Review` dipisahkan. Tidak adanya penanda tidak membuktikan respons manusia.
- Belum ada label hasil verifikasi independen. Kategori aplikasi adalah aturan eksplorasi, bukan target Y atau kinerja prediksi.''')
with method:
 st.subheader('Rancangan penelitian')
 st.markdown('''**Judul kerja:** Pengembangan dan Evaluasi Model Analitik Multisumber untuk Prioritas Verifikasi Pelaksanaan Kegiatan Belajar Mengajar.

**Tahap sekarang:** studi pendahuluan dan prototipe deskriptif menggunakan dump dummy. Alur: ekstraksi aman SQL → pemilihan kolom → pengodean ID → penggabungan ID jadwal dan tanggal → ringkasan dan penelusuran.

**Indikator:** ketersediaan jurnal, patroli, review valid; distribusi rating; status observasi; duplikasi; dan kesesuaian tanggal dengan pola jadwal. Tingkat kelengkapan dibagi jumlah sesi tercatat dalam filter, bukan jumlah jadwal wajib.

**Aturan peninjauan:** tandai masalah pemetaan/duplikasi, catatan piket Kosong atau Terlambat, atau rata-rata rating di bawah ambang pilihan. Ambang belum divalidasi. Rating memakai semua respons valid tanpa penanda otomatis dan dapat tetap mengandung duplikasi yang dilaporkan pada halaman kualitas.

**Pengembangan tesis:** DSRM, pembanding satu sumber/prosedur saat ini, label hasil tindak lanjut independen, pemisahan periode pengembangan dan pengujian, serta evaluasi ketepatan dan waktu tugas pengguna. Tidak ada model supervised yang dilatih pada tahap ini.

**Privasi:** nama, NIP/NISN, kontak, kredensial, komentar bebas, foto, dan materi teks tidak diekspor. ID diganti kode konsisten. Tanggal dan jam dipertahankan untuk analisis; pseudonimisasi bukan jaminan anonim untuk data operasional.''')
with downloads:
 st.subheader('Data yang dapat diperiksa kembali')
 st.download_button('Unduh sesi sesuai filter · CSV',df.to_csv(index=False).encode('utf-8-sig'),'sesi_kbm_terfilter.csv','text/csv')
 st.download_button('Unduh struktur dan data sesi lengkap · CSV',base.to_csv(index=False).encode('utf-8-sig'),'sessions.csv','text/csv')
 st.download_button('Unduh metadata · JSON',json.dumps(meta,indent=2,ensure_ascii=False).encode(),'manifest.json','application/json')
 st.caption('CSV sesi merupakan data olahan. Paket data mentah penelitian disediakan terpisah: jadwal, jurnal, piket, review, absensi guru, dan absensi mapel dengan ID berkode. Dump SQL asli tidak disertakan.')
 linkfile=ROOT/'data/drive_link.json'
 if linkfile.exists():
  link=json.loads(linkfile.read_text());st.link_button('Buka paket data di Google Drive',link['url'])
 if (ROOT/'KAMUS_DATA.md').exists():st.markdown((ROOT/'KAMUS_DATA.md').read_text(encoding='utf-8'))
 st.divider();st.json(meta,expanded=False)
st.caption('KBM Evidence Explorer · Data dummy · Ringkasan dapat ditelusuri, keputusan tetap melalui verifikasi manusia.')
