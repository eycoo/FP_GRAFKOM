# Jobdesk 3 — Aset Web & Viewer (tahap D, E, F)

Post-process mesh + ekspor GLB terkompres + viewer Three.js interaktif.

## Status

`index.html` = **starter dari ketua**, sudah jalan:
- Unggah GLB, orbit/zoom/pan (OrbitControls)
- IBL relighting (PMREMGenerator + RoomEnvironment)
- Mode inspeksi: PBR / Normal / Wireframe
- Statistik real time: FPS, tris, draw calls

## TODO Jobdesk 3

**Tahap D — post-process mesh** (input: `outputs/raw_mesh/` & GLB dari Jobdesk 1)
- Decimation multi-tier (high/mid/low), hitung ulang normal — `pymeshlab`/`trimesh`.

**Tahap E — kompresi**
- Draco + KTX2 via `gltf-transform`:
  ```bash
  npx @gltf-transform/cli optimize in.glb out.glb --compress draco --texture-compress ktx2
  ```

**Tahap F — viewer**
- Tambah `DRACOLoader` + `KTX2Loader` agar GLB terkompres termuat.
- Pilihan environment HDR (`RGBELoader`) untuk relighting bervariasi.
- Switch antar tier, polish UI, pesan error bila CDN gagal (PRD risiko §14).

## Jalankan lokal

Butuh server (modul ES + CDN):
```bash
cd viewer && python -m http.server 8000   # buka http://localhost:8000
```

## Serah terima

- Viewer + screenshot → Jobdesk 5.
- Set GLB final → Jobdesk 4.

**Tanda selesai:** GLB termuat, objek diputar & disinari ulang dengan lancar.
