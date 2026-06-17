# Jobdesk 2 — Dataset

Kumpulkan & kurasi foto artefak budaya + siapkan set evaluasi ber-ground-truth.

## Target

- **30–60 foto** artefak budaya: foto sendiri, Wikimedia Commons, museum digital.
- **20–30 objek** ber-ground-truth 3D dari Google Scanned Objects / OmniObject3D
  (untuk Chamfer distance di Jobdesk 4).
- Variasi kategori bentuk: wayang (tipis), keris, gerabah, miniatur candi, dll.

## Struktur

```
dataset/
├── photos/<kategori>/<id>.jpg      # foto terkurasi, penamaan konsisten
├── ground_truth/<id>/              # mesh GT + foto render-nya
└── licenses.csv                    # WAJIB: sumber + lisensi tiap foto
```

## Aturan

- **Tidak ada aset tanpa lisensi jelas.** Catat di `licenses.csv`.
- Standardisasi: penamaan `<kategori>_<id>`, resolusi & format seragam.
- Tidak ada pelabelan manual — beban kerja di pengumpulan & kurasi.

## Serah terima

- Foto terkurasi → Jobdesk 1 (`pipeline/` baca dari `dataset/photos/`).
- Set evaluasi ber-GT → Jobdesk 4.

**Tanda selesai:** folder rapi per kategori + `licenses.csv` lengkap.
