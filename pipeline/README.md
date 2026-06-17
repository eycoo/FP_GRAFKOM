# Jobdesk 1 — Pipeline Inti (Ketua: Farras)

Tahap **A–E**: satu foto artefak → GLB bertekstur, otomatis tanpa intervensi manual.
Ini jalur paling kritis (PRD §13): output jadi pintu masuk Jobdesk 3 & 4.

## Isi

```
pipeline/
├── configs/default.yaml     # konfigurasi + knob ablation
├── src/
│   ├── config.py            # muat & gabung config (YAML + override)
│   ├── preprocess.py        # tahap A (bungkus rembg/U2Net bawaan SF3D)
│   ├── inference.py         # tahap B+C (SF3D: mesh + PBR + delighting), catat VRAM/timing
│   ├── export_glb.py        # tahap E sisi pipeline (GLB dasar + dump mentah + manifest)
│   └── run_pipeline.py      # driver batch A→E (CLI + dipakai notebook)
├── notebooks/01_pipeline_sf3d.ipynb   # Colab/Kaggle T4
└── requirements.txt
```

## Jalankan (di Colab/Kaggle T4, BUKAN Windows lokal)

1. Pilih runtime **T4 GPU**.
2. Accept license SF3D gated di Hugging Face, siapkan token.
3. Pasang SF3D:
   ```bash
   git clone https://github.com/Stability-AI/stable-fast-3d.git
   pip install -r stable-fast-3d/requirements.txt
   pip install ./stable-fast-3d/texture_baker ./stable-fast-3d/uv_unwrapper
   pip install -r pipeline/requirements.txt
   ```
4. Batch:
   ```bash
   cd pipeline/src
   python run_pipeline.py --input ../../dataset/photos --tier high
   ```

Cara termudah: buka notebook, jalankan sel berurutan.

## Knob ablation (PRD §11) — lewat CLI atau config

| Knob | Flag | Menjawab |
|------|------|----------|
| Foreground ratio | `--foreground-ratio 0.85` | kelengkapan mesh |
| Resolusi tekstur | `--texture-resolution 1024` | kualitas vs ukuran file |
| Remesh / vertex | `--remesh triangle --vertex-count 20000` | jumlah segitiga |

## Output → serah-terima

| File | Ke |
|------|-----|
| `outputs/glb/<stem>_<tier>.glb` | Jobdesk 3 (viewer + kompresi) |
| `outputs/raw_mesh/<stem>_*.png` | Jobdesk 3 & 4 |
| `outputs/manifest.jsonl` | Jobdesk 4 (timing, VRAM, ukuran) |

## Tanggung jawab ketua (PRD §12, Jobdesk 1)

- [x] Setup environment + pasang SF3D + accept license (notebook sel 1–2)
- [x] Fungsi inferensi otomatis: foto → mesh (`run_pipeline.py`)
- [x] Verifikasi material PBR & delighting (notebook sel 6)
- [ ] Koordinasi: repo bersama, standup harian, keputusan teknis dari hasil tes
- [ ] Serah terima mesh mentah + PBR ke Jobdesk 3 & 4

> Catatan: kode siap, butuh dijalankan di GPU T4 dengan token HF untuk hasil nyata.
