"""Pembanding TripoSR (RQ1 — perbandingan model).

PRD §11 memetakan RQ1 ("apakah bekerja di artefak budaya & di mana batasnya") ke
**perbandingan model**. TripoSR = pembanding ringan untuk SF3D:

| | SF3D (utama) | TripoSR (pembanding) |
|---|---|---|
| material | PBR (albedo/roughness/metallic) + delight + UV | hanya warna verteks |
| VRAM | ~6-9 GB | ~6 GB |
| relight viewer | berarti | lemah (tanpa peta PBR) |

Kelas ini SENGAJA meniru antarmuka `SF3DReconstructor`: `.device`, `.model`, dan
`.run(image, recon_cfg) -> ReconResult`. Jadi `run_pipeline.process_one` dipakai apa
adanya — cukup tukar reconstructor. Mesh hasil = trimesh berwarna-verteks (glob_dict
kosong, tak ada peta PBR), tetap bisa diekspor GLB oleh `export_glb`.

Jalankan di notebook terpisah (`03_kaggle_triposr.ipynb`) — dep TripoSR (torchmcubes
dll) bisa bentrok bila dimuat di kernel yang sama dengan SF3D.
"""
from __future__ import annotations

import time

import numpy as np
from PIL import Image

from inference import ReconResult  # pakai ulang dataclass hasil (kontrak sama)


class TripoSRReconstructor:
    """Pembungkus TripoSR; antarmuka identik SF3DReconstructor agar pipeline tak berubah."""

    def __init__(self, model_cfg):
        self.cfg = model_cfg
        self.device = self._resolve_device(model_cfg.device)
        self.model = self._load_model()

    @staticmethod
    def _resolve_device(requested: str) -> str:
        import torch

        if requested == "cuda" and torch.cuda.is_available():
            return "cuda"
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load_model(self):
        from tsr.system import TSR

        model = TSR.from_pretrained(
            self.cfg.name,                 # mis. "stabilityai/TripoSR"
            config_name=self.cfg.config_name,   # "config.yaml"
            weight_name=self.cfg.weight_name,   # "model.ckpt"
        )
        # chunk renderer -> tekan VRAM puncak di T4 (analog query_chunk SF3D)
        chunk = int(getattr(self.cfg, "chunk_size", 8192) or 8192)
        model.renderer.set_chunk_size(chunk)
        model.to(self.device)
        return model

    @staticmethod
    def _fill_background(image: Image.Image, color: float = 0.5) -> Image.Image:
        """RGBA terisolasi -> RGB dgn latar abu (yang diharapkan TripoSR)."""
        arr = np.asarray(image.convert("RGBA")).astype(np.float32) / 255.0
        rgb = arr[:, :, :3] * arr[:, :, 3:4] + (1.0 - arr[:, :, 3:4]) * color
        return Image.fromarray((rgb * 255.0).astype(np.uint8))

    def run(self, image: Image.Image, recon_cfg) -> ReconResult:
        """Tahap B (geometri+warna verteks). recon_cfg sebagian besar tak relevan TripoSR."""
        import torch

        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()

        rgb = self._fill_background(image)
        mc_res = int(getattr(self.cfg, "mc_resolution", 256) or 256)

        t0 = time.perf_counter()
        with torch.no_grad():
            scene_codes = self.model([rgb], device=self.device)
            try:  # nama arg beda antar versi tsr
                meshes = self.model.extract_mesh(
                    scene_codes, has_vertex_color=True, resolution=mc_res
                )
            except TypeError:
                meshes = self.model.extract_mesh(scene_codes, resolution=mc_res)
        if self.device == "cuda":
            torch.cuda.synchronize()
        seconds = time.perf_counter() - t0

        peak = (
            torch.cuda.max_memory_allocated() / 1024**3 if self.device == "cuda" else 0.0
        )
        # glob_dict kosong: TripoSR tak hasilkan peta PBR/iluminasi (itu intinya RQ1)
        return ReconResult(mesh=meshes[0], glob_dict={}, seconds=seconds, peak_vram_gb=peak)
