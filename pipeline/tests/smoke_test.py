"""Smoke test pipeline inti tanpa GPU/SF3D nyata.

Tujuan: buktikan jalur A->E (config -> collect -> preprocess -> inference -> export
-> manifest) tersambung & tahan nama file berantakan (gaya Kaggle), TANPA memuat
model SF3D 7GB. SF3D & rembg distub dengan modul palsu yang mengembalikan kubus
trimesh, jadi GLB yang ditulis benar-benar valid.

Jalankan lokal:  python pipeline/tests/smoke_test.py
Kode nyata SF3D tetap dites di Colab/Kaggle (lihat notebook).
"""
from __future__ import annotations

import sys
import tempfile
import types
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))


# ---- stub modul sf3d (preprocess.py & inference.py mengimpornya) -------------
def install_sf3d_stub() -> dict:
    calls = {"remove_background": 0, "resize_foreground": 0, "run_image": 0}

    utils = types.ModuleType("sf3d.utils")

    def remove_background(image, session):
        calls["remove_background"] += 1
        return image.convert("RGBA")

    def resize_foreground(image, ratio):
        calls["resize_foreground"] += 1
        return image

    utils.remove_background = remove_background
    utils.resize_foreground = resize_foreground

    system = types.ModuleType("sf3d.system")

    class _FakeSF3D:
        @classmethod
        def from_pretrained(cls, *a, **k):
            return cls()

        def to(self, device):
            return self

        def eval(self):
            return self

        def run_image(self, image, **kw):
            calls["run_image"] += 1
            mesh = trimesh.creation.box(extents=(1, 1, 1))
            # peta PBR mentah palsu agar dump_raw_maps punya yang ditulis
            glob = {"illumination": Image.fromarray(
                np.zeros((8, 8, 3), dtype=np.uint8))}
            return mesh, glob

    system.SF3D = _FakeSF3D

    pkg = types.ModuleType("sf3d")
    sys.modules["sf3d"] = pkg
    sys.modules["sf3d.utils"] = utils
    sys.modules["sf3d.system"] = system
    return calls


def make_fake_images(d: Path) -> list[Path]:
    # tiru nama Kaggle: spasi, kutip, koma, subfolder kategori
    names = [
        "dataset_artefak_indonesia/192770_Saint_Bridget.jpg",
        "met_dataset/451725_The Concourse, study.jpg",  # spasi+koma (Windows blok kutip)
        "dataset_artefak_indonesia/39046_Seated_Male.png",
    ]
    out = []
    for n in names:
        p = d / n
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (32, 32), (120, 90, 60)).save(p)
        out.append(p)
    return out


def main() -> int:
    calls = install_sf3d_stub()

    import config
    import run_pipeline
    from inference import SF3DReconstructor

    fails = []

    def check(name, cond):
        print(("PASS " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    # 1. config: YAML + override
    yaml_path = SRC.parent / "configs" / "default.yaml"
    cfg = config.PipelineCfg.load(yaml_path, **{"reconstruct.texture_resolution": 512})
    check("config muat YAML (model SF3D)", cfg.model.name == "stabilityai/stable-fast-3d")
    check("config override texture_resolution", cfg.reconstruct.texture_resolution == 512)

    # 2. safe_stem bersihkan nama berantakan
    check("safe_stem buang kutip/koma/spasi",
          run_pipeline.safe_stem('451725_"The_Concourse, study') == "451725_The_Concourse_study")

    # 2b. categorize: judul -> kategori (RQ1)
    import categorize
    check("categorize: ax -> senjata", categorize.classify_title("Hafted Ax") == "senjata")
    check("categorize: buddha -> arca", categorize.classify_title("Head of a Buddha") == "arca")
    check("categorize: lintel -> arsitektur (sebelum deity)",
          categorize.classify_title("Lintel with the Head of a Male Deity") == "arsitektur")
    check("categorize: stem -> object_id", categorize.stem_to_object_id("artefak_39046_low") == "39046")
    title_map = {"39046": "Seated Male Figure", "192770": "Hand Bell"}
    check("category_for_stem pakai title_map",
          categorize.category_for_stem("artefak_39046", title_map) == "arca")
    check("category_for_stem fallback lainnya tanpa id",
          categorize.category_for_stem("artefak_999999", title_map) == "lainnya")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        imgs = make_fake_images(tmp / "input")
        out_dir = tmp / "outputs"

        # 3. collect_images rekursif, semua ext
        found = run_pipeline.collect_images(tmp / "input")
        check("collect_images temukan 3 foto rekursif", len(found) == len(imgs))

        # 4. preprocess: stub remove_background abaikan session, jadi None aman
        rembg_session = None

        # 5. jalur penuh A->E via process_one
        cfg.export.out_dir = str(out_dir)
        reconstructor = SF3DReconstructor(cfg.model)  # pakai _FakeSF3D
        check("device resolve (cpu lokal)", reconstructor.device in {"cpu", "cuda", "mps"})

        recs = []
        for img in found:
            rec = run_pipeline.process_one(img, reconstructor, cfg, rembg_session, "high", title_map)
            recs.append(rec)

        check("3 record dihasilkan", len(recs) == 3)
        check("record punya kolom category (RQ1)", all("category" in r for r in recs))
        # 39046 (Seated Male Figure)->arca & 192770 (Hand Bell)->ritual ada di title_map
        check("category terisi dari title_map (bukan semua lainnya)",
              any(r["category"] != "lainnya" for r in recs))
        glbs = list((out_dir / "glb").glob("*.glb"))
        check("3 GLB tertulis", len(glbs) == 3)
        check("nama GLB aman (no spasi/kutip)",
              all(" " not in g.name and '"' not in g.name for g in glbs))

        # 6. GLB benar-benar valid (bisa dimuat ulang trimesh)
        reloaded = trimesh.load(glbs[0])
        check("GLB valid & bisa dimuat ulang", reloaded is not None)

        # 7. manifest JSONL + dump peta mentah
        import json
        manifest = out_dir / "manifest.jsonl"
        from export_glb import write_manifest
        for r in recs:
            write_manifest(r, manifest)
        lines = manifest.read_text(encoding="utf-8").strip().splitlines()
        check("manifest 3 baris JSON valid",
              len(lines) == 3 and all(json.loads(x).get("glb") for x in lines))
        raw_maps = list((out_dir / "raw_mesh").glob("*.png"))
        check("peta PBR mentah ter-dump", len(raw_maps) >= 1)

        # 8. CLI arg parser tak crash
        ns = run_pipeline.argparse.ArgumentParser()  # parser dibangun di main(); cek fungsi ada
        check("run_pipeline.main callable", callable(run_pipeline.main))

    # 9. stub benar dipanggil (bukti jalur eksekusi lewat SF3D)
    check("SF3D.run_image dipanggil 3x", calls["run_image"] == 3)

    print(f"\n=== {'SEMUA LULUS' if not fails else f'{len(fails)} GAGAL: {fails}'} ===")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
