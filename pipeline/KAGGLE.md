# Run di Kaggle — dataset `scrapping grafkom`

Panduan jalankan pipeline inti SF3D di Kaggle GPU T4 dengan dataset hasil scraping.

## Bentuk dataset (dari scraping)

```
/kaggle/input/<slug>/
├── dataset_artefak_indonesia/   <- foto artefak: <id>_<nama>.jpg  (INPUT pipeline)
└── met_dataset/                 <- met museum + metadata.json
```

`<slug>` = slug Kaggle dari nama "scrapping grafkom" (mis. `scrapping-grafkom`).
Notebook sel 1 mendeteksi path otomatis via `glob` — tak perlu hardcode.

## Langkah

1. Buka <https://www.kaggle.com/code> → **New Notebook**.
2. Panel kanan:
   - **Settings → Accelerator → GPU T4 x1**
   - **Settings → Internet → ON** (wajib: pip, git clone, Hugging Face)
   - **Add Data** → cari **`scrapping grafkom`** → Attach
   - **Add-ons → Secrets** → tambah `HF_TOKEN` = token Hugging Face
     (akun harus sudah klik *Agree* di halaman model SF3D yang gated)
3. **File → Import Notebook** → unggah `pipeline/notebooks/02_kaggle_sf3d.ipynb`
   (atau salin sel-selnya).
4. Run All. Urutan sel: cek GPU/deteksi path → pasang SF3D → login HF →
   muat model → inferensi batch → zip hasil.

## Output

```
/kaggle/working/outputs/glb/<stem>_<tier>.glb   <- GLB siap viewer (Jobdesk 3)
/kaggle/working/outputs/raw_mesh/*.png          <- peta PBR mentah (Jobdesk 3 & 4)
/kaggle/working/outputs/manifest.jsonl          <- timing/VRAM/ukuran (Jobdesk 4)
/kaggle/working/glb_outputs.zip                 <- unduh dari tab Output
```

## Tips

- Mulai `LIMIT=5` (sel 5) untuk uji cepat; naikkan setelah yakin jalan.
- Sesi GPU bisa putus (PRD §14) → **Save Version** untuk simpan output reproducible.
- Output bisa dijadikan **dataset turunan** Kaggle → input langsung Jobdesk 3 & 4.
- Jika `INPUT` kosong di sel 1 → dataset belum ter-attach atau slug beda; cek
  daftar `Dataset ter-attach` yang dicetak.

## Alternatif: Colab

Pakai `pipeline/notebooks/01_pipeline_sf3d.ipynb` — sama, tapi input dari
`dataset/photos/` repo & login HF via `login()` interaktif.
