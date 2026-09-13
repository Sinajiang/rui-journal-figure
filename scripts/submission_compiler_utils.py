from __future__ import annotations
from pathlib import Path
import hashlib, json, yaml

def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def resolve(base: Path, value):
    if not value:
        return None
    p=Path(value)
    return p if p.is_absolute() else (base/p).resolve()

def canonical_hex(x):
    if x is None: return None
    s=str(x).strip().upper()
    if s.startswith("#") and len(s)==7:
        return s
    return s
