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


def _isolation_utils():
    """Util remove_background/resize_foreground: utamakan SF3D, fallback ke TripoSR.

    Kedua model mewarisi API util yang sama (rembg + crop foreground). Memilih util
    bawaan model agar prapengolahan identik dgn jalur internalnya. Dipakai pembanding
    TripoSR (notebook terpisah) tanpa perlu memasang SF3D.
    """
    try:
        import sf3d.utils as u
        return u
    except ImportError:
        pass
    try:
        import tsr.utils as u  # TripoSR
        return u
    except ImportError:
        pass
    return None


def prepare_image(
    image_path: str | Path,
    rembg_session,
    foreground_ratio: float = 0.85,
    remove_background: bool = True,
) -> Image.Image:
    """Foto mentah -> citra RGBA terisolasi, ter-crop, ter-resize.

    Pakai util resmi model (SF3D atau TripoSR) agar identik dengan jalur internalnya.
    Bila keduanya tak terpasang (mis. lint lokal tanpa GPU) -> RuntimeError.
    """
    utils = _isolation_utils()
    if utils is None:  # noqa: TRY003
        raise RuntimeError(
            "sf3d/tsr belum terpasang. Jalankan di runtime GPU & pasang model dulu "
            "(lihat pipeline/README.md)."
        )

    image = Image.open(image_path).convert("RGBA")
    if remove_background:
        image = utils.remove_background(image, rembg_session)
    image = utils.resize_foreground(image, foreground_ratio)
    return image
