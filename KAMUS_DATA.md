### Kamus data ringkas

**Dataset sesi (`sessions.csv`)**

- `sesi_id`: kode unik pasangan jadwal dan tanggal, bukan ID asli.
- `tanggal`: tanggal catatan sumber, format YYYY-MM-DD.
- `jadwal_id`, `guru_id`, `kelas_id`, `mapel_id`: kode penghubung yang konsisten; nilai kosong berarti referensi tidak tersedia.
- `tingkat`, `hari_jadwal`, `jam_ke`, `jam_mulai`, `jam_selesai`: konteks pola jadwal mingguan.
- `jadwal_ditemukan`, `hari_sesuai`: pemeriksaan referensi dan hari, True/False.
- `jurnal_n`, `piket_n`, `review_n`: jumlah catatan sumber pada sesi.
- `materi_terisi_n`: jumlah jurnal dengan teks materi tidak kosong; teks asli tidak dibagikan.
- `piket_status`: daftar kategori unik dari catatan piket, dipisahkan ` | `; bukan hasil voting.
- `review_nonauto_n`: catatan review tanpa penanda Auto-Review; tidak membuktikan penulis manusia.
- `review_auto_n`: review yang komentarnya mengandung Auto-Review, tanpa membedakan huruf besar/kecil.
- `review_valid_n`: review non-auto dengan rating 1–5.
- `rating_sum`, `rating_mean`, `rating_1_n` sampai `rating_5_n`: jumlah nilai, rata-rata berbasis catatan, dan distribusi rating valid. Rata-rata kosong jika tidak ada rating valid.
- `review_duplikat_n`: jumlah catatan tambahan setelah satu catatan pertama per siswa dalam satu sesi, tanpa menghapusnya dari sumber.
- `guru_absensi_status`, `guru_absensi_n`: kategori unik dan jumlah catatan absensi guru-hari yang cocok; kosong bukan berarti alpa.
- `jeda_jurnal_jam`: jeda terkecil created_at jurnal terhadap akhir jadwal, dalam jam; negatif dipertahankan. Timestamp ini belum divalidasi sebagai waktu input manusia.
- `absensi_mapel_n`: jumlah catatan absensi mapel yang mengacu pada seluruh jurnal dalam sesi.
- `murid_hadir_n`, `murid_alfa_n`: jumlah catatan berstatus Hadir/Alfa pada absensi mapel, bukan jumlah siswa unik lintas sesi.
- `jurnal_ada`, `piket_ada`, `review_ada`, `sumber_n`, `tiga_sumber`, `kategori`, `alasan`: kolom hasil olahan saat aplikasi berjalan; ambang rating dapat mengubah kategori dan alasan.

**Berkas sumber dalam paket mentah**

- `jadwal.csv`: satu baris per jadwal mingguan; konteks guru/kelas/mapel dalam kode, tingkat, tahun ajaran, semester, dan jam.
- `jurnal.csv`: satu baris per jurnal; `record_id`, `jadwal_id`, tanggal, timestamp asli, kode guru, learning_stage, dan flag materi_terisi.
- `piket.csv`: satu baris per observasi; kode catatan/jadwal/petugas/pengganti, status_kehadiran, waktu_inspeksi, tanggal, dan timestamp.
- `review.csv`: satu baris per review; kode catatan/jadwal/siswa, tanggal, timestamp, rating, dan flag auto_review_terdeteksi.
- `absensi_guru.csv`: satu baris per absensi guru-hari; kode catatan/guru, tanggal, status, jam tap dan pulang. Berkas hanya header bila tabel sumber kosong.
- `absensi_mapel.csv`: satu baris per absensi siswa-jurnal; kode catatan/jurnal/siswa dan status. Relasi tanggal didapat dari jurnal.

**Nilai hilang dan transformasi**

Nilai SQL NULL diekspor kosong. Kolom identitas menggunakan pseudonim HMAC dengan kunci lokal yang tidak dibagikan. Angka dan kategori dipertahankan, kecuali teks diganti flag untuk minimisasi data. `created_at` dan `updated_at` adalah timestamp dump; zona waktu belum diverifikasi. Tidak ada penyesuaian zona waktu, imputasi nol, pembersihan duplikat diam-diam, atau label target sintetis tambahan.

**Asal data**

Dump `siakadmu.sql` dan kode Laravel `siakadmu.zip`, diberikan pengguna; pengguna mengonfirmasi data uji/dummy pada 7 November 2026. Semua tabel bukan hasil pengumpulan observasi lapangan yang diverifikasi. Rincian hitungan dan periode tersedia pada manifest.json.
