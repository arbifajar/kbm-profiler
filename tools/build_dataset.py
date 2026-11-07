import json,gzip,collections,hashlib,hmac,secrets,csv,zipfile,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'raw-data'; RAW.mkdir(exist_ok=True)
(ROOT/'.private').mkdir(exist_ok=True)
(ROOT/'data').mkdir(exist_ok=True)
keypath=ROOT/'.private/pseudonym_key.bin'
if not keypath.exists():keypath.write_bytes(secrets.token_bytes(32))
key=keypath.read_bytes()
from functools import lru_cache
@lru_cache(maxsize=32768)
def code(kind,v):
 return '' if v is None else kind+'-'+hmac.new(key,f'{kind}:{v}'.encode(),hashlib.sha256).hexdigest()[:12].upper()
def write(name,rows):
 rows=iter(rows);first=next(rows,None)
 if first is None:return
 with (RAW/(name+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(first));w.writeheader();w.writerow(first);w.writerows(rows)
 print('Exported',name,flush=True)
with gzip.open(ROOT/'.private/source_selected.json.gz','rt',encoding='utf-8') as f:D=json.load(f)
J={r['id']:r for r in D['jadwal_pelajarans']};G={r['id']:r['user_id'] for r in D['guru_details']}
R={r['id']:r for r in D['rombels']};T={r['id']:r for r in D['tahun_ajarans']}
def base(r,kind):
 return {'record_id':code(kind,r['id']),'jadwal_id':code('JD',r['jadwal_pelajaran_id']),'tanggal':r['tanggal'],'created_at':r.get('created_at'),'updated_at':r.get('updated_at')}
write('jadwal',[{'jadwal_id':code('JD',r['id']),'guru_id':code('GR',r['guru_id']),'kelas_id':code('KL',r['rombel_id']),'mapel_id':code('MP',r['mapel_id']),'tingkat':R.get(r['rombel_id'],{}).get('tingkat',''),'tahun_ajaran':T.get(r['tahun_ajaran_id'],{}).get('tahun',''),'semester':T.get(r['tahun_ajaran_id'],{}).get('semester',''),'hari':r['hari'],'jam_ke':r['jam_ke'],'jam_mulai':r['jam_mulai'],'jam_selesai':r['jam_selesai']} for r in J.values()])
write('jurnal',[{**base(r,'JR'),'guru_id':code('GR',r['guru_id']),'learning_stage':r.get('learning_stage',''),'materi_terisi':bool((r.get('materi_pembelajaran') or '').strip())} for r in D['jurnal_gurus']])
write('piket',[{**base(r,'PK'),'piket_id':code('GR',r['piket_id']),'status_kehadiran':r['status_kehadiran'],'guru_pengganti_id':code('GR',r.get('guru_pengganti_id')),'waktu_inspeksi':r.get('waktu_inspeksi')} for r in D['kontrol_kbms']])
def review(r):
 return {**base(r,'UL'),'siswa_id':code('SW',r['siswa_detail_id']),'rating':r['rating'],'auto_review_terdeteksi':'auto-review' in (r.get('komentar') or '').lower()}
write('review',(review(r) for r in D['ulasan_kbms']))
write('absensi_guru',[{'record_id':code('AG',r['id']),'guru_id':code('GR',G.get(r['guru_detail_id'])),'tanggal':r['tanggal'],'status':r['status'],'jam_tap':r['jam_tap'],'jam_pulang':r['jam_pulang']} for r in D['absensi_gurus']])
write('absensi_mapel',({'record_id':code('AM',r['id']),'jurnal_id':code('JR',r['jurnal_guru_id']),'siswa_id':code('SW',r['siswa_detail_id']),'status':r['status']} for r in D['absensi_mapels']))
# Retain exact source keys; never manufacture calendar dates or repeat reviews across periods.
by={}
for t in ['jurnal_gurus','kontrol_kbms','ulasan_kbms']:
 idx=collections.defaultdict(list)
 for r in D[t]:idx[(r['jadwal_pelajaran_id'],r['tanggal'])].append(r)
 by[t]=idx
keys=set().union(*(set(x) for x in by.values()))
att=collections.defaultdict(list)
for r in D['absensi_gurus']:att[(G.get(r['guru_detail_id']),r['tanggal'])].append(r)
mapelatt=collections.defaultdict(collections.Counter)
for r in D['absensi_mapels']:mapelatt[r['jurnal_guru_id']][r['status']]+=1
import datetime
DAYS=['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
sessions=[]
for jid,date in sorted(keys,key=lambda x:(x[1],x[0])):
 j=J.get(jid,{});journals=by['jurnal_gurus'].get((jid,date),[]);patrol=by['kontrol_kbms'].get((jid,date),[]);reviews=by['ulasan_kbms'].get((jid,date),[])
 nonauto=[r for r in reviews if not review(r)['auto_review_terdeteksi']]
 valid=[r for r in nonauto if isinstance(r['rating'],(float,int)) and 1<=r['rating']<=5]
 ps=sorted(set(r['status_kehadiran'] for r in patrol));ats=sorted(set(r['status'] for r in att.get((j.get('guru_id'),date),[])))
 counts=collections.Counter()
 for r in journals:counts.update(mapelatt[r['id']])
 delay=[]
 for r in journals:
  if r.get('created_at') and j.get('jam_selesai'):
   try:delay.append(round((datetime.datetime.fromisoformat(r['created_at'])-datetime.datetime.fromisoformat(date+' '+j['jam_selesai'])).total_seconds()/3600,2))
   except ValueError:pass
 sessions.append({'sesi_id':code('SS',str(jid)+'|'+date),'tanggal':date,'jadwal_id':code('JD',jid),'guru_id':code('GR',j.get('guru_id')),'kelas_id':code('KL',j.get('rombel_id')),'mapel_id':code('MP',j.get('mapel_id')),'tingkat':R.get(j.get('rombel_id'),{}).get('tingkat',''),'hari_jadwal':j.get('hari',''),'jam_ke':j.get('jam_ke'),'jam_mulai':j.get('jam_mulai',''),'jam_selesai':j.get('jam_selesai',''),'jadwal_ditemukan':bool(j),'hari_sesuai':bool(j) and DAYS[datetime.date.fromisoformat(date).weekday()]==j.get('hari'),'jurnal_n':len(journals),'materi_terisi_n':sum(bool((r.get('materi_pembelajaran') or '').strip()) for r in journals),'piket_n':len(patrol),'piket_status':' | '.join(ps),'review_n':len(reviews),'review_nonauto_n':len(nonauto),'review_auto_n':len(reviews)-len(nonauto),'review_valid_n':len(valid),'rating_sum':sum(r['rating'] for r in valid),'rating_mean':round(sum(r['rating'] for r in valid)/len(valid),4) if valid else None,'rating_1_n':sum(r['rating']==1 for r in valid),'rating_2_n':sum(r['rating']==2 for r in valid),'rating_3_n':sum(r['rating']==3 for r in valid),'rating_4_n':sum(r['rating']==4 for r in valid),'rating_5_n':sum(r['rating']==5 for r in valid),'review_duplikat_n':len(reviews)-len(set(r['siswa_detail_id'] for r in reviews)),'guru_absensi_status':' | '.join(ats),'guru_absensi_n':len(att.get((j.get('guru_id'),date),[])),'jeda_jurnal_jam':min(delay) if delay else None,'absensi_mapel_n':sum(counts.values()),'murid_hadir_n':counts['Hadir'],'murid_alfa_n':counts['Alfa']})
with (ROOT/'data/sessions.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(sessions[0]));w.writeheader();w.writerows(sessions)
manifest={'dataset_kind':'dummy','provenance':'Pengguna mengonfirmasi dump merupakan data uji/dummy.','source_file':'siakadmu.sql','exported_on':datetime.date.today().isoformat(),'unit':'ID jadwal + tanggal dengan minimal satu catatan jurnal/piket/review','period_start':min(r['tanggal'] for r in sessions),'period_end':max(r['tanggal'] for r in sessions),'sessions':len(sessions),'source_counts':{k:len(v) for k,v in D.items()},'auto_reviews':sum(r['review_auto_n'] for r in sessions),'unknown_schedule_sessions':sum(not r['jadwal_ditemukan'] for r in sessions),'day_mismatch_sessions':sum(not r['hari_sesuai'] for r in sessions),'independent_outcome_labels':False,'review_origin_note':'Tanpa penanda otomatis tidak berarti review manusia; seluruh dump berstatus dummy.','calendar_note':'Tidak ada rekonstruksi hari efektif. Penyebut adalah sesi tercatat, bukan seluruh jadwal wajib.','generator_note':'UlasanKbmSeeder.calculateRating menggunakan kondisi piket, rasio alfa dan jam pelajaran; korelasi bersifat rekayasa simulasi.'}
(ROOT/'data/manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
(RAW/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest,indent=2))

if not (RAW/"absensi_guru.csv").exists():
 (RAW/"absensi_guru.csv").write_text("record_id,guru_id,tanggal,status,jam_tap,jam_pulang\n",encoding="utf-8")
