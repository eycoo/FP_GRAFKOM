# CLAUDE.md

Guidance for Claude Code when working in this repo.

## Apa ini

Platform **Rekonstruksi 3D Artefak Budaya dari Citra Tunggal**. Tugas akhir mata
kuliah Grafika Komputer (RKA). Mengubah satu foto artefak budaya Indonesia (wayang,
keris, gerabah, miniatur candi) menjadi objek 3D interaktif yang bisa diputar dan
disinari ulang di browser.

Posisi akademis: **applied research / empirical study**, bukan method paper.
Kontribusi ada pada evaluasi & analisis pada domain baru, bukan arsitektur baru.
Sumber kebenaran lengkap: `PRD_Rekonstruksi_3D_Artefak.md`. Baca PRD sebelum
keputusan desain besar.

## Pipeline (tahap A–G)

```
[A] Prapengolahan (bawaan SF3D: hapus latar U2Net, crop, center, resize)
[B] Rekonstruksi 3D (image -> ViT -> triplane -> Mesh & PBR Decoder -> marching cubes)
[C] Material PBR + delighting + UV unwrap (bawaan SF3D)
[D] Post-process mesh (decimation, hitung ulang normal)
[E] Export GLB (kompresi Draco + KTX2)
[F] Viewer web Three.js (orbit, relight, mode inspeksi)
[G] Evaluasi (metrik, ablation, failure analysis)
```

A–E di backend GPU (Colab/Kaggle T4). F di browser. G di notebook terpisah.

## Struktur repo (per jobdesk)

| Folder        | Jobdesk            | Penanggung jawab | Tahap     |
|---------------|--------------------|------------------|-----------|
| `pipeline/`   | 1 Ketua: pipeline inti | Farras       | Setup,A,B,C |
| `dataset/`    | 2 Dataset          | Anggota 2        | suplai A,G |
| `viewer/`     | 3 Aset web & viewer | Anggota 3       | D,E,F     |
| `evaluation/` | 4 Evaluasi         | Anggota 4        | G         |
| `docs/`       | 5 Dokumentasi      | Anggota 5        | menyatukan |
| `outputs/`    | aset bersama (GLB) | —                | jembatan  |

Jobdesk terhubung lewat **file**, bukan kode bercampur. `outputs/` adalah titik
serah-terima utama: pipeline tulis GLB ke sini, viewer & evaluasi baca dari sini.

## Aturan kunci (dari PRD, JANGAN dilanggar)

- **Model utama: Stable Fast 3D (SF3D)**. Pembanding: TripoSR. **Hindari TRELLIS
  standar** — butuh >16GB VRAM, OOM di T4.
- **Jangan latih / fine-tune model.** Hanya inferensi feedforward.
- **Tidak ada koneksi live web↔GPU.** Alur GLB manual: generate batch di Colab,
  muat ke viewer lewat tombol unggah file.
- **U2Net = prapengolahan BAWAAN SF3D**, bukan komponen yang dibangun tim. Jangan
  posisikan sebagai tahap besar buatan sendiri di dokumen/slide.
- Satu foto = satu objek. Tanpa multi-objek.
- Target: lebih cepat & murah dari fotogrametri, **bukan** lebih akurat.

## Constraint teknis

- GPU: **T4 16GB**. VRAM puncak harus < 16GB (NFR-1). SF3D ~7GB, TripoSR ~6GB.
- GLB final harus kecil (Draco + KTX2). Viewer pakai library dari CDN, no install.
- Inference target: hitungan detik per objek.

## Konvensi

- Python pipeline: jalan di Colab/Kaggle, bukan di mesin lokal Windows. Kode harus
  portable, path relatif, no hardcode path lokal.
- Penamaan output GLB: `<kategori>_<id>_<tier>.glb` di mana tier ∈ {high,mid,low}.
- Catat lisensi tiap foto di `dataset/licenses.csv`. Tidak ada aset tanpa lisensi jelas.
- Notebook checkpoint & commit rutin — sesi Colab bisa putus (lihat Risiko PRD §14).

## Definisi selesai (per PRD §17)

1. Pipeline: foto → GLB otomatis, terbukti pada beberapa artefak.
2. Viewer: muat GLB, tampil interaktif (PBR, relight, mode inspeksi).
3. Evaluasi terukur menjawab 3 pertanyaan penelitian + failure taxonomy.
4. Laporan akhir lengkap & konsisten.
