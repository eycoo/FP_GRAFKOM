# PRD: Platform Rekonstruksi 3D Artefak Budaya dari Citra Tunggal

**Mata kuliah:** Grafika Komputer (RKA)
**Tipe dokumen:** Product Requirements Document
**Durasi pengerjaan:** 1 minggu
**Tim:** 5 orang
**Status:** Draf untuk dikerjakan

---

## 1. Ringkasan

Proyek ini membangun platform yang mengubah satu foto artefak budaya menjadi objek 3D interaktif yang bisa diputar dan disinari ulang di browser. Platform memakai model rekonstruksi citra tunggal yang sudah ada (Stable Fast 3D), lalu hasilnya diproses menjadi aset web yang ringan dan ditampilkan lewat viewer berbasis Three.js.

Yang dicari dari proyek ini bukan model baru, melainkan jawaban atas seberapa jauh teknologi rekonstruksi 3D yang ada sekarang bisa dipakai untuk artefak budaya Indonesia, lengkap dengan batasannya dan panduan trade-off untuk dipakai di web. Platform adalah alat untuk menjawab pertanyaan itu, sekaligus deliverable demo.

Posisi akademis: ini applied research atau empirical study, bukan method paper. Kontribusinya ada pada evaluasi dan analisis pada domain baru, bukan pada arsitektur baru.

---

## 2. Latar Belakang dan Masalah

Artefak budaya Indonesia seperti wayang, keris, gerabah, dan miniatur candi sebagian besar terdokumentasi dalam bentuk foto dua dimensi. Foto statis tidak bisa diputar, diperiksa dari berbagai sisi, atau disinari ulang, sehingga terbatas untuk edukasi, katalog museum, dan wisata digital.

Pembuatan model 3D secara konvensional punya hambatan nyata:

- Fotogrametri dan pemindaian 3D butuh banyak foto, peralatan khusus, dan waktu pemrosesan lama.
- Pemodelan manual butuh keahlian artis 3D dan waktu kerja panjang per objek.
- Model generatif yang ada belum diuji secara sistematis pada artefak budaya yang bentuknya tidak biasa dan berornamen rumit.

Hambatan ini berat untuk lembaga dengan anggaran terbatas seperti museum daerah dan komunitas pelestari budaya.

---

## 3. Pertanyaan Penelitian dan Tujuan

### Pertanyaan penelitian

1. Seberapa jauh model rekonstruksi 3D citra tunggal yang dilatih pada objek umum bisa digeneralisasi ke artefak budaya Indonesia? Pada kategori apa berhasil, pada kategori apa gagal, dan kenapa?
2. Di mana titik keseimbangan antara kualitas visual, ukuran file, dan kecepatan render agar aset layak dipakai di web?
3. Apakah estimasi material PBR dan delighting menghasilkan relighting yang masuk akal untuk objek budaya?

### Tujuan teknis

- Membangun pipeline dari satu foto artefak menjadi mesh 3D bertekstur yang berjalan pada GPU T4.
- Menyediakan viewer web yang menampilkan objek secara interaktif dengan kontrol kamera dan relighting.
- Menghasilkan evaluasi terukur untuk menjawab tiga pertanyaan penelitian di atas.

### Tujuan pengguna

- Memberi cara cepat dan murah untuk mengubah foto artefak menjadi objek 3D.
- Memberi pengalaman eksplorasi objek yang lebih baik daripada foto statis.

---

## 4. Pengguna Target

| Pengguna | Kebutuhan |
|---|---|
| Pengelola museum dan lembaga budaya | Katalog digital yang murah diproduksi dan bisa diakses publik |
| Pendidik | Media interaktif untuk mengenalkan warisan budaya |
| Pengembang platform budaya digital | Aset 3D ringan yang jalan di browser |

Catatan: untuk lingkup proyek satu minggu, pengguna nyata tidak dilibatkan langsung dalam pengembangan. Pengguna dipakai untuk membingkai relevansi, dan persepsi mereka diuji lewat user study kecil di tahap evaluasi.

---

## 5. Ruang Lingkup

### Masuk lingkup (in scope)

- Rekonstruksi 3D dari satu foto memakai Stable Fast 3D.
- Perbandingan dengan TripoSR sebagai baseline.
- Post-process mesh dan ekspor GLB terkompres.
- Viewer web Three.js dengan PBR shading, relighting, dan mode inspeksi grafika.
- Evaluasi kualitas, performa, ablation, dan failure analysis.

### Di luar lingkup (out of scope)

- Melatih atau fine-tune model dari nol.
- Koneksi live real time antara web dan backend GPU. Alur dibuat manual: GLB digenerate di Colab secara batch, lalu dimuat ke viewer lewat tombol unggah file.
- Dukungan multi-objek dalam satu foto.
- Akurasi geometri setara fotogrametri. Posisi proyek adalah lebih cepat dan murah, bukan lebih akurat.

---

## 6. Pemetaan Materi Grafika Komputer

Bagian ini penting karena ini mata kuliah grafika. Logika grafika dipisah berdasarkan lokasi eksekusi.

### Grafika yang berjalan di web (viewer, tiap frame)

| Logika | Untuk apa |
|---|---|
| Rasterization pipeline | Mengubah segitiga 3D menjadi pixel di layar |
| Evaluasi BRDF dan PBR shading | Menghitung warna pixel dari cahaya, arah pandang, roughness, metallic |
| Image based lighting | Objek memantulkan cahaya dari environment |
| Transformasi dan kamera | Rotasi, zoom, pan lewat perkalian matriks model view projection |
| Texture mapping | Menempelkan tekstur ke permukaan lewat koordinat UV |
| Visualisasi normal dan wireframe | Mode inspeksi untuk memeriksa geometri |

### Grafika yang berjalan di luar web (Python, sekali saat menyiapkan file)

| Logika | Untuk apa |
|---|---|
| Marching cubes | Mengekstrak permukaan mesh dari density field model |
| UV unwrapping | Memetakan permukaan 3D ke ruang tekstur 2D (dilakukan SF3D) |
| Decimation dan perhitungan normal ulang | Menyederhanakan mesh agar ringan, menjaga shading tetap mulus |

Materi grafika yang tersentuh sesuai daftar mata kuliah: mesh representation, texture, dan BRDF.

---

## 7. Arsitektur Sistem dan Pipeline

Alur menyeluruh dari foto sampai laporan:

```
[A] Prapengolahan (bawaan SF3D: hapus latar, crop, center, resize)
        v
[B] Rekonstruksi 3D (image -> ViT -> triplane -> Mesh & PBR Decoder -> marching cubes)
        v
[C] Material PBR + delighting + UV unwrap (bawaan SF3D)
        v
[D] Post-process mesh (decimation, hitung ulang normal)
        v
[E] Export GLB (kompresi Draco + KTX2)
        v
[F] Viewer web Three.js (orbit, relight, mode inspeksi)
        v
[G] Evaluasi (metrik, ablation, failure analysis)
```

Tahap A sampai E berjalan di backend GPU (Colab atau Kaggle T4). Tahap F berjalan di browser. Tahap G berjalan di notebook terpisah.

Catatan konsistensi: penghapusan latar belakang adalah bagian bawaan dari SF3D, bukan komponen terpisah yang dirancang tim. Di semua dokumen dan slide, U2Net diposisikan sebagai prapengolahan bawaan SF3D, bukan tahap besar yang dibangun sendiri.

---

## 8. Functional Requirements

### FR-1 Prapengolahan
- Sistem menerima satu foto artefak dalam format umum (JPG, PNG).
- Sistem menghapus latar belakang dan menyiapkan citra terisolasi memakai prapengolahan bawaan SF3D.

### FR-2 Rekonstruksi
- Sistem menghasilkan mesh 3D beserta peta material PBR dari satu foto.
- Parameter resolusi ekstraksi mesh dapat diatur untuk kebutuhan ablation.

### FR-3 Material
- Sistem menghasilkan peta albedo, roughness, dan metallic dengan delighting, memakai keluaran SF3D.

### FR-4 Post-process dan ekspor
- Sistem menyederhanakan mesh ke beberapa tingkat jumlah segitiga (tinggi, sedang, ringan).
- Sistem mengekspor GLB terkompres Draco dan KTX2.

### FR-5 Viewer
- Viewer memuat file GLB lewat tombol unggah.
- Viewer mendukung rotasi, zoom, dan pan objek.
- Viewer mendukung pergantian environment lighting untuk relighting.
- Viewer menyediakan mode inspeksi: PBR, normal, dan wireframe.
- Viewer menampilkan statistik real time: FPS, jumlah segitiga, draw call.

### FR-6 Evaluasi
- Sistem menyediakan skrip pengukuran kualitas, performa, dan ablation.
- Sistem menghasilkan tabel hasil dan pemetaan kegagalan.

---

## 9. Non Functional Requirements

| Kode | Requirement | Target |
|---|---|---|
| NFR-1 | Berjalan pada GPU T4 16GB tanpa kehabisan memori | VRAM puncak di bawah 16GB |
| NFR-2 | Viewer berjalan lancar di browser umum | FPS nyaman pada perangkat uji |
| NFR-3 | Aset ringan untuk web | Ukuran GLB final kecil setelah kompresi |
| NFR-4 | Waktu rekonstruksi cepat | Hitungan detik per objek untuk inference |
| NFR-5 | Viewer dapat dibuka tanpa instalasi | Cukup browser, library dari CDN |

---

## 10. Spesifikasi Teknis

### Model
- Utama: Stable Fast 3D (feedforward, citra tunggal ke mesh, output PBR dan delighting, sekitar 7GB VRAM).
- Pembanding: TripoSR (sekitar 6GB VRAM, tanpa PBR dan delighting bawaan).
- Dihindari: TRELLIS versi standar, karena kebutuhan memori melebihi 16GB dan berisiko kehabisan memori di T4.

### Tools dan library
- Backend: Python, PyTorch, Stable Fast 3D, trimesh atau pymeshlab untuk post-process.
- Ekspor dan kompresi: gltf-transform (Draco dan KTX2).
- Viewer: Three.js, GLTFLoader, DRACOLoader, KTX2Loader, RGBELoader, PMREMGenerator, OrbitControls.
- Evaluasi: skimage (PSNR, SSIM), lpips, pyrender atau trimesh untuk render ulang, library jarak 3D untuk Chamfer.

### Dataset

| Data | Untuk apa | Jumlah | Sumber |
|---|---|---|---|
| Foto artefak budaya | Bahan utama sistem dan demo | 30 sampai 60 | Foto sendiri, Wikimedia Commons, koleksi museum digital |
| Subset objek ber-ground-truth 3D | Mengukur akurasi geometri secara objektif | 20 sampai 30 | Google Scanned Objects, OmniObject3D |

Tidak ada pelabelan manual. Beban kerja data ada pada pengumpulan dan kurasi, bukan anotasi. Status lisensi tiap foto dicatat dalam spreadsheet.

---

## 11. Metrik Keberhasilan dan Rencana Evaluasi

### Kualitas hasil
- Tanpa ground truth 3D: render ulang mesh dari sudut yang sama dengan foto input, bandingkan dengan foto asli memakai PSNR, SSIM, LPIPS.
- Dengan ground truth (subset GSO atau OmniObject3D): Chamfer distance setelah alignment ICP.
- User study: penilaian realisme dan kesetiaan skala 1 sampai 5, sekitar 10 sampai 15 responden.

### Performa sistem
- Waktu rekonstruksi per objek, VRAM puncak, ukuran GLB, waktu muat di browser, FPS.

### Ablation
- Pengaruh foreground ratio terhadap kelengkapan mesh.
- Pengaruh resolusi ekstraksi mesh terhadap kualitas dan ukuran file.
- Pengaruh tingkat decimation terhadap FPS dan kualitas visual.
- Delighting hidup versus mati terhadap realisme relighting.

### Failure taxonomy
- Pengelompokan kegagalan: objek tipis, bagian tidak terlihat, ornamen berulang, permukaan mengkilap atau transparan, dengan contoh tiap kategori.

### Pemetaan metrik ke pertanyaan penelitian

| Pertanyaan | Dijawab oleh |
|---|---|
| Apakah bekerja di artefak budaya dan di mana batasnya | Perbandingan model, metrik kualitas, failure taxonomy |
| Di mana keseimbangan kualitas, ukuran, kecepatan | Ablation resolusi dan decimation, metrik performa |
| Apakah relighting meyakinkan | Ablation delighting, user study |

---

## 12. Pembagian Tugas

Lima jobdesk berjalan paralel karena terhubung lewat file, bukan kode yang bercampur.

| Jobdesk | Penanggung jawab | Tahap | Tanggung jawab utama |
|---|---|---|---|
| 1 Ketua: Pipeline inti | Farras | Setup, A, B, C | Inferensi model, prapengolahan, koordinasi tim |
| 2 Dataset | [Anggota 2] | nyuplai A, G | Kumpulkan dan kurasi foto, siapkan set evaluasi |
| 3 Aset web dan viewer | [Anggota 3] | D, E, F | Post-process, ekspor GLB, viewer Three.js |
| 4 Evaluasi | [Anggota 4] | G | Metrik, ablation, user study, failure analysis |
| 5 Dokumentasi | [Anggota 5] | menyatukan | Laporan, figur, dokumentasi |

### Jobdesk 1: Ketua (Pipeline inti dan prapengolahan)
- Setup environment Colab atau Kaggle, pasang SF3D, accept license gated di Hugging Face.
- Bangun fungsi inferensi: satu foto menjadi mesh bertekstur otomatis.
- Verifikasi material PBR dan hasil delighting.
- Koordinasi: repo bersama, standup harian, keputusan teknis dari hasil tes.
- Serah terima: mesh mentah dan peta PBR ke jobdesk 3 dan 4.
- Tanda selesai: satu foto bisa diubah jadi mesh otomatis tanpa intervensi manual.

### Jobdesk 2: Dataset
- Tentukan kategori artefak dengan variasi bentuk.
- Kumpulkan 30 sampai 60 foto dari foto sendiri, Wikimedia, museum digital.
- Catat sumber dan lisensi di spreadsheet.
- Kurasi kualitas dan standardisasi penamaan, resolusi, format.
- Siapkan subset 20 sampai 30 objek ber-ground-truth dari GSO atau OmniObject3D.
- Serah terima: foto terkurasi ke jobdesk 1, set evaluasi ke jobdesk 4.
- Tanda selesai: folder foto rapi per kategori dan spreadsheet lengkap.

### Jobdesk 3: Aset web dan viewer
- Post-process mesh: decimation, hitung ulang normal, buat beberapa tingkat penyederhanaan.
- Ekspor GLB terkompres Draco dan KTX2.
- Bangun viewer Three.js: loader GLB, IBL, OrbitControls, mode PBR, normal, wireframe, statistik.
- Sediakan tombol unggah GLB agar output pipeline tinggal dimuat.
- Serah terima: viewer dan tangkapan layar ke jobdesk 5, set GLB ke jobdesk 4.
- Tanda selesai: GLB bisa dimuat, objek bisa diputar dan disinari ulang dengan lancar.

### Jobdesk 4: Evaluasi
- Tetapkan metrik dan protokol di awal.
- Jalankan metrik kualitas, Chamfer pada subset ber-ground-truth, dan metrik performa.
- Jalankan ablation dan user study.
- Susun failure taxonomy berkategori dengan contoh.
- Serah terima: tabel hasil, grafik, pemetaan kegagalan ke jobdesk 5.
- Tanda selesai: tabel angka lengkap dan daftar kegagalan berkategori.

### Jobdesk 5: Dokumentasi dan laporan
- Kumpulkan bahan dari semua anggota secara berkala.
- Susun laporan mengikuti format sebelas bagian proposal.
- Buat figur: diagram pipeline, screenshot viewer, grafik hasil.
- Integrasikan hasil evaluasi ke narasi, hubungkan ke pertanyaan penelitian.
- Serah terima: draf untuk direview seluruh tim.
- Tanda selesai: laporan lengkap, konsisten, semua angka dan figur masuk.

---

## 13. Timeline 1 Minggu

| Hari | Target |
|---|---|
| Hari 1 sampai 2 | Pipeline inferensi berjalan di T4, dataset awal terkumpul, kerangka viewer dan laporan disiapkan |
| Hari 3 sampai 4 | Rekonstruksi sejumlah artefak, viewer berfungsi, evaluasi dimulai |
| Hari 5 sampai 6 | Ablation, failure analysis, perapian demo, penulisan laporan |
| Hari 7 | Cadangan waktu dan finalisasi |

Jalur paling kritis ada di jobdesk 1, karena outputnya jadi pintu masuk untuk jobdesk 3 dan 4. Prioritas: hasilkan satu mesh secepat mungkin agar anggota lain bisa lanjut.

---

## 14. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Sesi Colab atau Kaggle putus saat proses panjang | Kerja hilang | Checkpoint dan commit rutin ke repo |
| SF3D gagal di objek tipis seperti wayang | Hasil jelek | Jadikan bahan failure analysis, bukan kegagalan proyek |
| Decimation merusak UV dan tekstur belang | Aset rusak | Kontrol jumlah segitiga dari resolusi ekstraksi dulu, decimation ringan |
| Tidak ada ground truth untuk artefak | Akurasi sulit diukur | Pakai render ulang dan subset GSO ber-ground-truth |
| Koneksi live web ke GPU rumit | Tidak selesai tepat waktu | Pakai alur GLB manual, bukan koneksi live |
| Library viewer gagal dimuat | Demo gagal | Viewer menampilkan pesan kebutuhan koneksi internet, siapkan cadangan offline jika perlu |

---

## 15. Dependensi dan Asumsi

- Akses GPU T4 di Colab atau Kaggle tersedia selama pengerjaan.
- Akses dan persetujuan license SF3D di Hugging Face berhasil.
- Tim punya repo bersama untuk kode dan aset.
- Viewer dijalankan di browser dengan koneksi internet untuk menarik library dari CDN.

---

## 16. Deliverables

1. Notebook pipeline tahap A sampai E yang menghasilkan GLB.
2. Kumpulan GLB hasil rekonstruksi beberapa artefak, beberapa tingkat penyederhanaan.
3. Viewer web Three.js dengan mode inspeksi grafika.
4. Tabel evaluasi, grafik trade-off, dan failure taxonomy.
5. Laporan akhir bergaya paper sesuai format proposal sebelas bagian.

---

## 17. Definisi Selesai

Proyek dianggap selesai bila:

- Pipeline mengubah satu foto menjadi GLB secara otomatis dan terbukti pada beberapa artefak.
- Viewer memuat GLB dan menampilkan objek interaktif dengan PBR, relighting, dan mode inspeksi.
- Ada hasil evaluasi terukur yang menjawab tiga pertanyaan penelitian, termasuk failure taxonomy.
- Laporan akhir lengkap, konsisten antar bagian, dengan semua angka dan figur masuk.
