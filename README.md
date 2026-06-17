# Rekonstruksi 3D Artefak Budaya dari Citra Tunggal

Platform yang mengubah satu foto artefak budaya Indonesia (wayang, keris, gerabah,
miniatur candi) menjadi objek 3D interaktif — bisa diputar & disinari ulang di browser.
Pakai **Stable Fast 3D** untuk rekonstruksi + viewer **Three.js**.

Tugas akhir Grafika Komputer (RKA). Applied research / empirical study.
Spesifikasi lengkap: [`PRD_Rekonstruksi_3D_Artefak.md`](PRD_Rekonstruksi_3D_Artefak.md).

## Alur (tahap A–G)

```
foto → [A prapengolahan] → [B rekonstruksi] → [C material PBR] → [D post-process]
     → [E export GLB] → [F viewer web] → [G evaluasi]
```

A–E: backend GPU T4 (Colab/Kaggle). F: browser. G: notebook. Penghubung: file di `outputs/`.

## Struktur & pembagian tugas

| Folder | Jobdesk | PJ | Status |
|--------|---------|-----|--------|
| [`pipeline/`](pipeline/) | 1 Pipeline inti (A,B,C,E) | Anggota 1 | kode siap, butuh run di T4 |
| [`dataset/`](dataset/) | 2 Dataset (suplai A,G) | Anggota 2 | scaffold |
| [`viewer/`](viewer/) | 3 Aset web & viewer (D,E,F) | Anggota 3 | starter |
| [`evaluation/`](evaluation/) | 4 Evaluasi (G) | Anggota 4 | scaffold |
| [`docs/`](docs/) | 5 Dokumentasi | Anggota 5 | scaffold |
| `outputs/` | aset bersama (GLB, manifest) | semua | titik serah-terima |

## Quickstart (pipeline inti)

Di Colab/Kaggle **T4 GPU** — buka `pipeline/notebooks/01_pipeline_sf3d.ipynb`, jalankan berurutan.
Detail: [`pipeline/README.md`](pipeline/README.md).

## Aturan kunci

- Model: SF3D (utama), TripoSR (pembanding). **Hindari TRELLIS** (OOM di T4).
- Jangan latih/fine-tune. Tanpa koneksi live web↔GPU (alur GLB manual).
- Target: lebih cepat & murah dari fotogrametri, bukan lebih akurat.

Panduan kerja untuk Claude Code: [`CLAUDE.md`](CLAUDE.md).
Koordinasi tim & standup: [`docs/COORDINATION.md`](docs/COORDINATION.md).
