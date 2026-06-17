"""Tahap A - prapengolahan citra (bawaan SF3D).

PENTING (PRD 7): penghapusan latar = bagian BAWAAN SF3D, bukan komponen yang
dibangun tim. Modul ini hanya membungkus util SF3D (rembg/U2Net) supaya pemanggilan
dari pipeline rapi. Jangan posisikan ini sebagai tahap besar buatan sendiri.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image


def load_rembg_session(model_name: str = "u2net"):
    """Buat sesi rembg (U2Net) sekali, pakai ulang untuk batch."""
    import rembg

    return rembg.new_session(model_name)


def prepare_image(
    image_path: str | Path,
    rembg_session,
    foreground_ratio: float = 0.85,
    remove_background: bool = True,
) -> Image.Image:
    """Foto mentah -> citra RGBA terisolasi, ter-crop, ter-resize untuk SF3D.

    Pakai util resmi SF3D agar identik dengan jalur internal model. Bila SF3D
    belum ter-import (mis. lint lokal tanpa GPU) -> RuntimeError dengan petunjuk.
    """
    try:
        import sf3d.utils as sf3d_utils
    except ImportError as exc:  # noqa: TRY003
        raise RuntimeError(
            "sf3d belum terpasang. Jalankan di runtime GPU dan pasang SF3D dulu "
            "(lihat pipeline/README.md)."
        ) from exc

    image = Image.open(image_path).convert("RGBA")
    if remove_background:
        image = sf3d_utils.remove_background(image, rembg_session)
    image = sf3d_utils.resize_foreground(image, foreground_ratio)
    return image
