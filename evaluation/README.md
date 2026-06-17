# Jobdesk 4 — Evaluasi (tahap G)

Metrik kualitas, performa, ablation, user study, failure taxonomy. Menjawab 3
pertanyaan penelitian (PRD §3, §11).

## Input

- `outputs/manifest.jsonl` (Jobdesk 1): timing, VRAM, ukuran GLB per objek.
- `outputs/glb/`, `outputs/raw_mesh/` (Jobdesk 1 & 3).
- `dataset/ground_truth/` (Jobdesk 2): subset ber-GT untuk Chamfer.

## Metrik (PRD §11)

| Metrik | Library | Untuk |
|--------|---------|-------|
| PSNR / SSIM / LPIPS | skimage, lpips | render-ulang vs foto asli (tanpa GT) |
| Chamfer distance | jarak 3D + ICP | akurasi geometri (subset GT) |
| Performa | manifest + viewer | waktu rekon, VRAM, ukuran GLB, FPS, waktu muat |
| User study 1–5 | form | realisme & kesetiaan, 10–15 responden |

## Ablation

- foreground_ratio → kelengkapan mesh
- resolusi ekstraksi → kualitas vs ukuran
- tingkat decimation → FPS vs kualitas
- delighting on/off → realisme relighting

## Failure taxonomy

Kelompokkan: objek tipis, bagian tak terlihat, ornamen berulang, permukaan
mengkilap/transparan — dengan contoh tiap kategori.

## Serah terima

Tabel hasil, grafik trade-off, pemetaan kegagalan → Jobdesk 5.

**Tanda selesai:** tabel angka lengkap + daftar kegagalan berkategori.

> Taruh skrip di `src/`, notebook di `notebooks/`. Tetapkan protokol metrik di awal.
