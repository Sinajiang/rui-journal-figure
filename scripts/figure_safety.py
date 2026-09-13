from __future__ import annotations
import numpy as np

def safe_label_y(values, pad_fraction=0.04, ymin=None, ymax=None):
    """Return y-positions above values with a scale-aware pad."""
    a = np.asarray(values, dtype=float)
    finite = a[np.isfinite(a)]
    if finite.size == 0:
        return a
    lo = finite.min() if ymin is None else ymin
    hi = finite.max() if ymax is None else ymax
    span = max(hi - lo, 1e-9)
    return a + span * pad_fraction

def assert_monotonic(x, strict=True):
    x = np.asarray(x, dtype=float)
    d = np.diff(x)
    ok = np.all(d > 0) if strict else np.all(d >= 0)
    if not ok:
        raise ValueError("Expected monotonic coordinates.")
    return True
