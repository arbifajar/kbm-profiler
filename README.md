# KBM Evidence Explorer

Prototipe tugas Metode Penelitian dan studi pendahuluan tesis.

**Arbi Muhammad Fajar · LK26 R1 · 072926010**  
Fakultas Pascasarjana, Magister Ilmu Komputer, Universitas Pakuan.

## Status data

Seluruh data bawaan merupakan **data uji/dummy**, sebagaimana dikonfirmasi pemilik dump. Tidak boleh disajikan sebagai hasil observasi operasional sekolah, hasil survei murid nyata, atau hasil evaluasi guru. Nama dan pengenal langsung tetap dihapus karena master data dalam aplikasi uji dapat berasal dari data nyata.

Aplikasi adalah profil deskriptif dengan aturan peninjauan yang transparan. Tidak ada model machine learning terlatih, label tindak lanjut independen, atau klaim akurasi prediksi.

## Menjalankan aplikasi

Gunakan Python 3.10 atau lebih baru (disarankan 3.12).

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Buka alamat lokal yang ditampilkan, biasanya http://localhost:8501. Data demo tersedia langsung. CSV unggahan harus mengikuti struktur `data/sessions.csv`; format dan konsistensi jumlah akan divalidasi. Unggahan tidak ditulis ke disk oleh kode aplikasi. Cache hanya digunakan untuk data demo bawaan.

## Isi aplikasi

1. Ringkasan: jumlah sesi, kelengkapan tiga sumber, rating tertimbang, tren mingguan, dan status piket.
2. Telusuri sesi: filter kategori, rincian satu sesi, jumlah sumber, alasan penandaan, serta referensi jadwal berkode.
3. Kualitas data: referensi hilang, hari tidak cocok, duplikasi, rating otomatis, dan jeda jurnal negatif.
4. Metode penelitian: unit analisis, aturan, batasan, dan jalur pengembangan tesis.
5. Data dan unduhan: CSV hasil filter, dataset sesi lengkap, metadata, dan tautan paket sumber jika tersedia.

## Cara perhitungan

- Satu sesi = pasangan ID jadwal dan tanggal yang memiliki minimal satu jurnal, patroli, atau review.
- Tidak membangkitkan sesi dari seluruh kalender karena hari libur, pembatalan, dan masa berlaku jadwal belum tervalidasi. Kelengkapan selalu dibagi jumlah sesi tercatat, bukan seluruh sesi yang seharusnya terjadi.
- Catatan tiap sumber diringkas sebelum penggabungan. Tidak ada join many-to-many yang menggandakan jumlah review atau jurnal.
- `rating_mean` memakai rating 1 sampai 5 tanpa penanda `Auto-Review` pada komentar. Semua respons dalam dump tetap dummy. Review duplikat dilaporkan dan tidak dibuang diam-diam; rata-rata berbasis catatan, bukan responden unik.
- Rata-rata keseluruhan = jumlah nilai rating / jumlah rating valid, bukan rata-rata tidak tertimbang dari rata-rata sesi.
- Kategori `Tinjau catatan` dipicu referensi/hari yang tidak cocok, duplikasi, piket Kosong/Terlambat, atau rating di bawah ambang eksplorasi. `Bukti belum lengkap` berarti sumber belum tersedia. `Tiga sumber tersedia` tidak berarti kebenaran isi terverifikasi.
- Tidak adanya absensi guru ditampilkan sebagai tidak tersedia dan tidak menjadi bukti ketidakhadiran.

## Temuan dari kode Laravel

- Laravel 12 dengan PHP ^8.4 tercantum pada composer.json; aplikasi Python berdiri sendiri dan tidak menjalankan Laravel.
- `AutoReviewKbm` dapat memberi rating 5 otomatis untuk siswa hadir yang belum review. Penanda komentar digunakan sebagai flag; tidak adanya flag tidak membuktikan respons manusia.
- `UlasanKbmSeeder.calculateRating` menggunakan kondisi piket, rasio alfa, jam pelajaran, dan profil acak. Hubungan antarvariabel dalam dummy tidak dapat digunakan sebagai bukti empiris atau validasi triangulasi independen.
- Dashboard murid mengelompokkan jadwal per mata pelajaran. Review yang tersimpan pada satu ID tidak diduplikasi ke seluruh jam. Cakupan review per slot adalah cakupan menurut foreign key tersimpan.
- `KbmAttendanceAnalysisService` memperlakukan absensi guru yang tidak tersedia sebagai tidak hadir pada beberapa cabang logika. Prototipe penelitian sengaja membedakan kedua kondisi.
- `sumber_verifikasi` dan foto pada kontrol bukan label hasil tindak lanjut yang independen. Tidak digunakan sebagai target prediksi.

## Data mentah penelitian

Paket `data_mentah_kbm_dummy.zip` berisi CSV pada tingkat catatan sumber: jadwal, jurnal, piket, review, absensi guru, dan absensi mapel. Ini adalah **ekstrak sumber yang diminimalkan dan dipseudonimkan**, bukan salinan SQL lengkap. ID dikodekan konsisten; nilai kategori, tanggal, dan angka relevan dipertahankan. Flag `materi_terisi` dan `auto_review_terdeteksi` adalah transformasi eksplisit. Teks bebas, identitas, foto, token, dan kredensial tidak disertakan. Kamus data menjelaskan perubahan.

Master jadwal dapat memuat nama asli dalam dump; ekspor hanya memakai kode guru, kelas, dan mata pelajaran. Kunci pemetaan tidak masuk paket. Untuk data nyata, tanggal/jam serta kombinasi kelas-mapel masih dapat mengungkap identitas sehingga akses harus ditinjau ulang.

## Google Drive

Paket mentah dapat diunggah sebagai ZIP ke Drive tanpa konversi Google Sheets. Ini mempertahankan CSV besar tanpa batas sel spreadsheet. Berikan akses kepada dosen secara eksplisit sesuai kebijakan penelitian. Jangan unggah SQL asli atau kode Laravel ke repositori publik.

## Publikasi Streamlit Community Cloud

1. Unggah isi folder aplikasi ini ke repositori GitHub milik Anda. Sertakan `app.py`, `analysis.py`, `requirements.txt`, `.streamlit/config.toml`, `data`, serta dokumentasi.
2. Masuk ke Streamlit Community Cloud dengan akun GitHub. Pilih repositori, branch, dan entrypoint `app.py`.
3. Pilih Python 3.12 dan jalankan deploy. Paket demo hanya menggunakan data dummy dengan identitas langsung dihapus.
4. Periksa halaman ringkasan, filter, dan unduhan setelah deploy.

Referensi resmi: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

Dokumentasi pengujian: https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest

Tidak ada klaim aplikasi telah dipublikasikan sampai URL publik berhasil dibuat dan diperiksa. Akses Google Drive mengikuti izin berkas; tautan tidak otomatis berarti publik.

## Pengembangan tesis

Gunakan studi pendahuluan untuk mengaudit struktur dan aturan. Tahap tesis memerlukan data operasional berizin, kalender pertemuan yang valid, batas waktu fitur, label independen bila memakai supervised learning, dan evaluasi terhadap prosedur sekolah. Dokumen pengajuan tesis terdahulu masih bersifat rancangan; ketersediaan data operasional belum terpenuhi.

## Reproduksi dari dump dummy

Jalankan dari folder aplikasi:

```powershell
python tools/extract_sql.py "C:\lokasi\siakadmu.sql"
python tools/build_dataset.py
python -m unittest -v test_app.py
```

Parser hanya membaca INSERT pada tabel yang dipilih; SQL tidak dieksekusi. Folder `.private` memuat data sumber terpilih dan kunci pengodean lokal, sehingga tidak boleh diunggah. `raw-data` memuat ekstrak penelitian yang telah diminimalkan. Kedua folder diabaikan oleh Git. Simpan kunci lokal jika ingin kode konsisten antar-ekspor. Skrip ini khusus struktur dump yang diperiksa dan menandai hasil sebagai dummy; penggunaan data operasional memerlukan audit ulang serta perubahan metadata secara eksplisit. Skrip dapat membutuhkan beberapa menit dan memori yang cukup karena jutaan catatan.
