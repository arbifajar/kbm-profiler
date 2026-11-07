from pathlib import Path
import re,json,gzip,collections,sys
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/".private"
PRIVATE.mkdir(exist_ok=True)
if len(sys.argv)!=2: raise SystemExit("Usage: python tools/extract_sql.py path/to/siakadmu.sql")
wanted={'jadwal_pelajarans','jurnal_gurus','kontrol_kbms','ulasan_kbms','absensi_gurus','absensi_mapels','guru_details','rombels','tahun_ajarans','mapels'}
# Tokenize mysqldump values without executing SQL. Escapes handled inside strings only.
tok=re.compile(r"'(?:[^'\\]|\\.|'')*'|NULL|-?\d+(?:\.\d+)?|[(),;]",re.S)
def value(t):
 if t=='NULL': return None
 if not t.startswith("'"):return float(t) if '.' in t else int(t)
 t=t[1:-1].replace("''", "'")
 return re.sub(r'\\(.)',lambda m:{'n':'\n','r':'\r','t':'\t','0':'\x00','Z':'\x1a'}.get(m[1],m[1]),t,flags=re.S)
def parse(s,cols):
 row=None;pos=0
 for m in tok.finditer(s):
  if s[pos:m.start()].strip():raise ValueError('Unsupported SQL value')
  t=m[0];pos=m.end()
  if t=='(':row=[]
  elif t==')':
   if len(row)!=len(cols):raise ValueError('Column mismatch')
   yield dict(zip(cols,row));row=None
  elif t not in [',',';']:row.append(value(t))
 if s[pos:].strip():raise ValueError('Unparsed SQL tail')
data={t:[] for t in wanted};buf=[];table=None;cols=None
with open(sys.argv[1],encoding='utf-8') as f:
 for line in f:
  if line.startswith('INSERT INTO '):
   m=re.match(r'INSERT INTO `([^`]+)` \((.*?)\) VALUES\s*(.*)',line,re.S)
   if not m:raise ValueError('Unknown insert format')
   table=m[1] if m[1] in wanted else None
   if table: cols=re.findall(r'`([^`]+)`',m[2]);buf=[m[3]]
  elif table:buf.append(line)
  if table and line.rstrip().endswith(';'):
   data[table].extend(parse(''.join(buf),cols));table=None;buf=[]
with gzip.open(PRIVATE/'source_selected.json.gz','wt',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False)
for t,rows in sorted(data.items()):
 dates=[r['tanggal'] for r in rows if r.get('tanggal')]
 print(t,len(rows),'period',min(dates) if dates else '-',max(dates) if dates else '-')
 if rows and t in ['kontrol_kbms','absensi_gurus']: print(collections.Counter(r.get('status_kehadiran',r.get('status')) for r in rows))
u=data['ulasan_kbms'];print('auto_review_count',sum('auto-review' in (r.get('komentar') or '').lower() for r in u))
print('rating_counts',dict(collections.Counter(r['rating'] for r in u)))
