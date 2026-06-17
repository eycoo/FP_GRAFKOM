"""Driver batch pipeline inti (Jobdesk 1) - tahap A sampai E.

Foto masuk -> GLB keluar, otomatis tanpa intervensi manual (= tanda selesai Jobdesk 1).
Pakai dari CLI atau diimpor dari notebook Colab.

Contoh CLI:
    python run_pipeline.py \
        --input ../../dataset/photos \
        --config ../configs/default.yaml \
        --tier high

Output:
    outputs/glb/<stem>_<tier>.glb        # GLB siap viewer (Jobdesk 3)
    outputs/raw_mesh/<stem>_*.png        # peta PBR mentah (Jobdesk 3 & 4)
    outputs/manifest.jsonl               # 1 baris/objek: timing, VRAM, ukuran (Jobdesk 4)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# impor lokal jalan baik sebagai modul maupun skrip
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import PipelineCfg  # noqa: E402
from preprocess import load_rembg_session, prepare_image  # noqa: E402
from inference import SF3DReconstructor  # noqa: E402
from export_glb import export_glb, dump_raw_maps, write_manifest  # noqa: E402

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def safe_stem(name: str) -> str:
    """Bersihkan nama file jadi stem aman (Kaggle: ada spasi, kutip, koma)."""
    stem = re.sub(r"[^A-Za-z0-9.-]+", "_", name).strip("_")
    return stem or "artifact"


def collect_images(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted(p for p in input_path.rglob("*") if p.suffix.lower() in IMAGE_EXTS)


def process_one(img_path: Path, reconstructor, cfg: PipelineCfg, rembg_session, tier: str) -> dict:
    """Jalankan A->E untuk satu foto, kembalikan record manifest."""
    out_root = Path(cfg.export.out_dir)
    glb_dir = out_root / "glb"
    raw_dir = out_root / "raw_mesh"
    stem = safe_stem(img_path.stem)

    # Tahap A
    image = prepare_image(
        img_path,
        rembg_session,
        foreground_ratio=cfg.preprocess.foreground_ratio,
        remove_background=cfg.preprocess.remove_background,
    )
    # Tahap B + C
    result = reconstructor.run(image, cfg.reconstruct)
    # Tahap E (ekspor dasar + dump mentah; kompresi berat di Jobdesk 3)
    glb_path = export_glb(result.mesh, glb_dir / f"{stem}_{tier}.glb")
    raw_maps = dump_raw_maps(result.glob_dict, raw_dir, stem) if cfg.export.write_raw_mesh else []

    record = {
        "stem": stem,
        "input": str(img_path),
        "glb": str(glb_path),
        "tier": tier,
        "seconds": round(result.seconds, 3),
        "peak_vram_gb": round(result.peak_vram_gb, 3),
        "glb_bytes": glb_path.stat().st_size,
        "raw_maps": [str(p) for p in raw_maps],
        "foreground_ratio": cfg.preprocess.foreground_ratio,
        "texture_resolution": cfg.reconstruct.texture_resolution,
        "remesh": cfg.reconstruct.remesh,
        "vertex_count": cfg.reconstruct.vertex_count,
    }
    return record


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pipeline inti SF3D (tahap A-E)")
    ap.add_argument("--input", required=True, help="file foto atau folder berisi foto")
    ap.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "configs/default.yaml"))
    ap.add_argument("--tier", default="high", choices=["high", "mid", "low"])
    ap.add_argument("--out-dir", default=None, help="override export.out_dir")
    # override ablation cepat dari CLI
    ap.add_argument("--foreground-ratio", type=float, default=None)
    ap.add_argument("--texture-resolution", type=int, default=None)
    ap.add_argument("--remesh", default=None, choices=["none", "triangle", "quad"])
    ap.add_argument("--vertex-count", type=int, default=None)
    args = ap.parse_args(argv)

    overrides = {}
    if args.out_dir is not None:
        overrides["export.out_dir"] = args.out_dir
    if args.foreground_ratio is not None:
        overrides["preprocess.foreground_ratio"] = args.foreground_ratio
    if args.texture_resolution is not None:
        overrides["reconstruct.texture_resolution"] = args.texture_resolution
    if args.remesh is not None:
        overrides["reconstruct.remesh"] = args.remesh
    if args.vertex_count is not None:
        overrides["reconstruct.vertex_count"] = args.vertex_count

    cfg = PipelineCfg.load(args.config, **overrides)
    images = collect_images(Path(args.input))
    if not images:
        print(f"Tidak ada foto di {args.input}", file=sys.stderr)
        return 1

    print(f"Muat SF3D ({cfg.model.name}) ...")
    reconstructor = SF3DReconstructor(cfg.model)
    rembg_session = load_rembg_session()
    manifest = Path(cfg.export.out_dir) / "manifest.jsonl"

    print(f"Proses {len(images)} foto -> tier '{args.tier}' (device={reconstructor.device})")
    ok = 0
    for i, img in enumerate(images, 1):
        try:
            rec = process_one(img, reconstructor, cfg, rembg_session, args.tier)
            write_manifest(rec, manifest)
            print(f"[{i}/{len(images)}] {img.name} -> {Path(rec['glb']).name} "
                  f"({rec['seconds']}s, VRAM {rec['peak_vram_gb']}GB, {rec['glb_bytes']//1024}KB)")
            ok += 1
        except Exception as exc:  # noqa: BLE001 - 1 foto gagal != batch gagal (PRD risiko)
            print(f"[{i}/{len(images)}] GAGAL {img.name}: {exc}", file=sys.stderr)

    print(f"Selesai. {ok}/{len(images)} sukses. Manifest: {manifest}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
