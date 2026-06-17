"""Muat & gabung konfigurasi pipeline (Jobdesk 1).

Sumber nilai, urutan prioritas (tinggi menimpa rendah):
  1. argumen eksplisit (CLI / parameter notebook)
  2. file YAML (configs/default.yaml)
  3. default hardcode di sini
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

try:
    from omegaconf import OmegaConf
except ImportError:  # omegaconf belum terpasang (mis. lint lokal)
    OmegaConf = None

try:
    import yaml  # fallback bila omegaconf tak ada (PyYAML lebih umum tersedia)
except ImportError:
    yaml = None


def _read_yaml(path: str | Path) -> dict:
    if OmegaConf is not None:
        from omegaconf import OmegaConf as _OC
        return dict(_OC.to_container(_OC.load(path), resolve=True) or {})
    if yaml is not None:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


@dataclass
class PreprocessCfg:
    foreground_ratio: float = 0.85
    remove_background: bool = True


@dataclass
class ReconstructCfg:
    texture_resolution: int = 1024
    remesh: str = "none"            # none | triangle | quad
    vertex_count: int = -1
    estimate_illumination: bool = False


@dataclass
class ExportCfg:
    out_dir: str = "../outputs"
    write_raw_mesh: bool = True
    glb_basename: str = "artifact"


@dataclass
class ModelCfg:
    name: str = "stabilityai/stable-fast-3d"
    config_name: str = "config.yaml"
    weight_name: str = "model.safetensors"
    device: str = "cuda"


@dataclass
class PipelineCfg:
    model: ModelCfg = field(default_factory=ModelCfg)
    preprocess: PreprocessCfg = field(default_factory=PreprocessCfg)
    reconstruct: ReconstructCfg = field(default_factory=ReconstructCfg)
    export: ExportCfg = field(default_factory=ExportCfg)

    @classmethod
    def load(cls, yaml_path: str | Path | None = None, **overrides: Any) -> "PipelineCfg":
        cfg = cls()
        if yaml_path is not None and Path(yaml_path).exists():
            data = _read_yaml(yaml_path)
            if data:
                cfg = cls(
                    model=ModelCfg(**(data.get("model") or {})),
                    preprocess=PreprocessCfg(**(data.get("preprocess") or {})),
                    reconstruct=ReconstructCfg(**(data.get("reconstruct") or {})),
                    export=ExportCfg(**(data.get("export") or {})),
                )
        # override datar bertitik, mis. reconstruct.texture_resolution=512
        for key, val in overrides.items():
            section, _, leaf = key.partition(".")
            if leaf and hasattr(cfg, section):
                setattr(getattr(cfg, section), leaf, val)
            elif hasattr(cfg, key):
                setattr(cfg, key, val)
        return cfg

    def as_dict(self) -> dict:
        return asdict(self)
