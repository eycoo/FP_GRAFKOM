"""Kategorisasi artefak dari judul katalog (untuk RQ1 evaluasi).

PRD pertanyaan penelitian #1: "pada kategori apa berhasil, pada kategori apa
gagal, dan kenapa?". Dataset nyata = artefak Met Museum (`dataset/metadata_artefak.csv`)
dengan judul teks-bebas Inggris (mis. "Hafted Ax", "Head of a Buddha"), TANPA kolom
kategori. Modul ini menurunkan kategori kasar dari kata kunci judul supaya manifest &
notebook evaluasi bisa membandingkan kualitas per-kategori.

Kategori bersifat heuristik (bukan label kurator). Hasilnya ditulis ke
`dataset/categories.csv` agar bisa ditinjau & dikoreksi manual bila perlu.

Kunci join: stem manifest `artefak_<ObjectID>` <-> kolom `Object_ID` metadata.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

# Urutan PENTING: aturan pertama yang cocok menang. Yang spesifik/struktural dulu
# (lintel, antefix) sebelum yang umum (deity, head), supaya "Lintel with Head of a
# Deity" -> arsitektur, bukan arca.
KEYWORD_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("arsitektur", (
        "antefix", "lintel", "architectural", "tympanum", "water spout", "spout",
        "finial",
    )),
    ("senjata", (
        "ax head", "hafted", " ax", "axe", "sword", "halberd", "celt", "chandrasa",
        "weapon", "blade", "dagger", "keris", "kris", "spear", "shield", "halberd",
    )),
    ("wadah", (
        "lime container", "lime spatula", "container", "box", "flask", "mold",
        "lid", "betel", "holy-water vessel", "vessel", "spatula", "plaque", "rattle",
    )),
    ("ritual", (
        "bell", "gong", "lamp", "scepter", "ghen", "prayer", "kentongan", "drum",
        "kinnari", "holy-water", "ritual",
    )),
    ("arca", (
        "buddha", "bodhisattva", "deity", "ganesha", "shiva", "vishnu", "durga",
        "avalokiteshvara", "manjushri", "jambhala", "kuvera", "maitreya", "vairochana",
        "vajrapani", "vajrasattva", "prajnaparamita", "surya", "goddess", "god",
        "mahabala", "figure", "torso", "bust", "head", "warrior", "ruler",
        "padmapani", "lokeshvara", "hariti", "parvati", "anthropomorph", "portrait",
        "akshobhya", "ratnasambhava", "demon", "guardian", "deity", " vina",
    )),
]

FALLBACK = "lainnya"  # mis. "Mirror Handle", "Arm Band", "Chastity Plaque"

# Semua kategori yang mungkin (dipakai notebook untuk urutan plot konsisten)
CATEGORIES = ["arca", "senjata", "wadah", "ritual", "arsitektur", FALLBACK]


def classify_title(judul: str) -> str:
    """Judul katalog -> kategori kasar. Cocokkan substring lowercase berurutan."""
    t = (judul or "").lower()
    for kategori, keywords in KEYWORD_RULES:
        if any(kw in t for kw in keywords):
            return kategori
    return FALLBACK


def stem_to_object_id(stem: str) -> str:
    """`artefak_37743` / `artefak_37743_low` -> `37743`. Ambil gugus angka pertama."""
    m = re.search(r"(\d+)", stem or "")
    return m.group(1) if m else ""


def load_title_map(metadata_csv: str | Path) -> dict[str, str]:
    """Baca metadata_artefak.csv -> {Object_ID(str): Judul}. {} bila file tak ada."""
    path = Path(metadata_csv)
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            oid = str(row.get("Object_ID", "")).strip()
            if oid:
                out[oid] = row.get("Judul", "")
    return out


def category_for_stem(stem: str, title_map: dict[str, str]) -> str:
    """Stem manifest -> kategori. FALLBACK bila id tak ada di metadata."""
    oid = stem_to_object_id(stem)
    judul = title_map.get(oid)
    if judul is None:
        return FALLBACK
    return classify_title(judul)


def default_metadata_path() -> Path:
    """dataset/metadata_artefak.csv relatif ke root repo (src ada di pipeline/src)."""
    return Path(__file__).resolve().parents[2] / "dataset" / "metadata_artefak.csv"


def build_categories_csv(metadata_csv: str | Path | None = None,
                         out_csv: str | Path | None = None) -> Path:
    """Tulis dataset/categories.csv: object_id,judul,kategori (untuk tinjauan manual)."""
    metadata_csv = Path(metadata_csv) if metadata_csv else default_metadata_path()
    out_csv = Path(out_csv) if out_csv else metadata_csv.parent / "categories.csv"
    title_map = load_title_map(metadata_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["object_id", "judul", "kategori"])
        for oid, judul in sorted(title_map.items()):
            w.writerow([oid, judul, classify_title(judul)])
    return out_csv


if __name__ == "__main__":  # `python categorize.py` -> regen categories.csv + ringkasan
    from collections import Counter

    tmap = load_title_map(default_metadata_path())
    dist = Counter(classify_title(j) for j in tmap.values())
    out = build_categories_csv()
    print(f"metadata: {len(tmap)} artefak -> {out}")
    for k in CATEGORIES:
        print(f"  {k:12} {dist.get(k, 0)}")
