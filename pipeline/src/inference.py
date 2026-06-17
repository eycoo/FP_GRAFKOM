"""Tahap B & C - rekonstruksi 3D + material PBR (inti Jobdesk 1).

Bungkus SF3D: satu citra terisolasi -> mesh bertekstur + peta PBR (albedo,
roughness, metallic) dengan delighting. Catat VRAM puncak (NFR-1) dan waktu
inferensi (NFR-4) supaya jobdesk 4 (evaluasi) tinggal pakai.

Tanda selesai Jobdesk 1: satu foto -> mesh otomatis tanpa intervensi manual.
"""
from __future__ import annotations

import time
from contextlib import nullcontext
from dataclasses import dataclass

from PIL import Image


@dataclass
class ReconResult:
    mesh: object              # trimesh.Trimesh dari SF3D (geometri + material PBR)
    glob_dict: dict           # keluaran tambahan SF3D (mis. peta iluminasi bila diminta)
    seconds: float            # waktu inferensi tahap B+C
    peak_vram_gb: float       # VRAM puncak (0.0 bila bukan CUDA)


class SF3DReconstructor:
    """Pembungkus model SF3D yang dimuat sekali, dipakai untuk banyak foto (batch)."""

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
        from sf3d.system import SF3D

        model = SF3D.from_pretrained(
            self.cfg.name,
            config_name=self.cfg.config_name,
            weight_name=self.cfg.weight_name,
        )
        model.to(self.device)
        model.eval()
        return model

    def run(self, image: Image.Image, recon_cfg) -> ReconResult:
        """Jalankan tahap B+C untuk satu citra. Idempotent, aman dipanggil berulang."""
        import torch

        if self.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()

        # autocast bfloat16 di CUDA untuk hemat VRAM & cepat (NFR-1, NFR-4)
        autocast = (
            torch.autocast(device_type="cuda", dtype=torch.bfloat16)
            if self.device == "cuda"
            else nullcontext()
        )

        t0 = time.perf_counter()
        with torch.no_grad(), autocast:
            mesh, glob_dict = self.model.run_image(
                image,
                bake_resolution=recon_cfg.texture_resolution,
                remesh=recon_cfg.remesh,
                vertex_count=recon_cfg.vertex_count,
                estimate_illumination=recon_cfg.estimate_illumination,
            )
        if self.device == "cuda":
            torch.cuda.synchronize()
        seconds = time.perf_counter() - t0

        peak_vram = (
            torch.cuda.max_memory_allocated() / 1024**3 if self.device == "cuda" else 0.0
        )
        return ReconResult(mesh=mesh, glob_dict=glob_dict, seconds=seconds, peak_vram_gb=peak_vram)
