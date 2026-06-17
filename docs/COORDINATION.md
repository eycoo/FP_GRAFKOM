# Koordinasi Tim (dikelola Ketua: Farras)

Tanggung jawab koordinasi Jobdesk 1: repo bersama, standup harian, keputusan teknis
berbasis hasil tes, serah terima antar jobdesk.

## Jalur kritis

```
Jobdesk 2 (foto) ─┐
                  ├─> Jobdesk 1 (pipeline → GLB) ─┬─> Jobdesk 3 (viewer)
                  │                               └─> Jobdesk 4 (evaluasi) ─> Jobdesk 5 (laporan)
```

**Jobdesk 1 = pintu masuk.** Prioritas mutlak: hasilkan **satu mesh secepat mungkin**
agar Jobdesk 3 & 4 bisa mulai. Sebelum GLB pertama ada, Jobdesk 3 pakai GLB contoh,
Jobdesk 4 finalisasi protokol metrik.

## Titik serah-terima (kontrak antar tim)

| Dari → Ke | Artefak | Lokasi | Format |
|-----------|---------|--------|--------|
| 2 → 1 | foto terkurasi | `dataset/photos/<kategori>/` | JPG/PNG, nama `<kategori>_<id>` |
| 1 → 3 | GLB + mesh mentah | `outputs/glb/`, `outputs/raw_mesh/` | `<stem>_<tier>.glb` |
| 1 → 4 | metrik proses | `outputs/manifest.jsonl` | JSONL/objek |
| 2 → 4 | set ber-GT | `dataset/ground_truth/` | mesh GT + render |
| 3 → 4 | GLB final per tier | `outputs/glb/` | GLB terkompres |
| semua → 5 | figur, tabel, angka | `docs/figures/`, `docs/report/` | — |

Kontrak: nama file & folder di atas **tetap**. Ubah lewat kesepakatan standup, update doc ini.

## Standup harian (template)

Salin tiap hari. Format: kemarin / hari ini / blocker.

```
### Hari N — <tanggal>
- Farras (J1): kemarin … | hari ini … | blocker …
- A2 (J2):     …
- A3 (J3):     …
- A4 (J4):     …
- A5 (J5):     …
Keputusan hari ini: …
```

## Log keputusan teknis (berbasis hasil tes)

| # | Keputusan | Alasan / bukti | Tanggal |
|---|-----------|----------------|---------|
| 1 | Model utama SF3D, pembanding TripoSR | PRD; SF3D punya PBR+delighting bawaan | hari 0 |
| 2 | Hindari TRELLIS standar | >16GB VRAM, OOM di T4 | hari 0 |
| 3 | Alur GLB manual (no live web↔GPU) | koneksi live rumit, risiko tak selesai | hari 0 |
| _ | _(isi saat ablation jalan: foreground_ratio, texture_res, decimation)_ | | |

## Timeline (PRD §13)

| Hari | Target |
|------|--------|
| 1–2 | Pipeline inferensi jalan di T4; dataset awal; kerangka viewer & laporan |
| 3–4 | Rekonstruksi banyak artefak; viewer berfungsi; evaluasi mulai |
| 5–6 | Ablation, failure analysis, rapikan demo, tulis laporan |
| 7 | Cadangan & finalisasi |

## Checklist Definisi Selesai (PRD §17)

- [ ] Pipeline: foto → GLB otomatis, terbukti pada beberapa artefak
- [ ] Viewer: muat GLB, interaktif (PBR, relight, mode inspeksi)
- [ ] Evaluasi terukur menjawab 3 pertanyaan + failure taxonomy
- [ ] Laporan akhir lengkap & konsisten
