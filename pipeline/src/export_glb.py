"""Tahap E (sisi pipeline) - ekspor mesh SF3D ke GLB + simpan mesh mentah.

Catatan pembagian kerja: kompresi berat (Draco + KTX2) & multi-tier decimation
adalah milik Jobdesk 3 (viewer), dijalankan via gltf-transform. Di sini Jobdesk 1
cuma menulis GLB dasar + dump peta PBR mentah sebagai titik serah-terima di
`outputs/`. Lihat viewer/README.md untuk langkah kompresi.
"""
from __future__ import annotations

import json
from pathlib import Path


def export_glb(mesh, out_path: str | Path) -> Path:
    """Tulis mesh SF3D (trimesh) ke file GLB. Material PBR ikut ter-embed."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(str(out_path), file_type="glb")
    return out_path


def dump_raw_maps(glob_dict: dict, raw_dir: str | Path, stem: str) -> list[Path]:
    """Simpan peta PBR / iluminasi mentah dari SF3D untuk Jobdesk 3 & 4.

    SF3D menaruh hasil tambahan (mis. peta iluminasi bila estimate_illumination)
    di glob_dict. Apa pun yang berupa PIL.Image disimpan sebagai PNG.
    """
    from PIL import Image

    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for key, val in (glob_dict or {}).items():
        if isinstance(val, Image.Image):
            p = raw_dir / f"{stem}_{key}.png"
            val.save(p)
            written.append(p)
    return written


def write_manifest(record: dict, manifest_path: str | Path) -> Path:
    """Tambah satu baris ke manifest JSONL hasil pipeline (sumber utk evaluasi)."""
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return manifest_path
