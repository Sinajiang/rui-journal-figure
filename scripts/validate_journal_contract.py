from __future__ import annotations
import argparse, json, math
from pathlib import Path
import yaml

def close_to_any(value, allowed, tol=1.5):
    if value is None or not allowed:
        return None
    return min(abs(value-a) for a in allowed) <= tol

def validate(metadata, profile, stage):
    journal=profile["journal"]
    cfg=profile["stages"][stage]
    hard=[]
    warnings=[]
    passed=[]

    # PDF/vector metadata
    width=metadata.get("width_mm")
    height=metadata.get("height_mm")
    min_text=metadata.get("min_text_pt")
    max_text=metadata.get("max_text_pt")
    fmt=(metadata.get("format") or "").lower()

    if cfg.get("preferred_width_mm") and width is not None:
        if close_to_any(width,cfg["preferred_width_mm"]):
            passed.append(f"width {width:.1f} mm matches a preferred width")
        else:
            warnings.append(
                f"width {width:.1f} mm does not match preferred widths {cfg['preferred_width_mm']}"
            )

    if cfg.get("max_height_mm") is not None and height is not None:
        if height <= cfg["max_height_mm"]:
            passed.append(f"height {height:.1f} mm <= {cfg['max_height_mm']} mm")
        else:
            hard.append(f"height {height:.1f} mm exceeds {cfg['max_height_mm']} mm")

    fcfg=cfg.get("font_pt") or {}
    if min_text is not None and fcfg.get("min") is not None:
        if min_text >= fcfg["min"]:
            passed.append(f"minimum text {min_text:.2f} pt >= {fcfg['min']} pt")
        else:
            hard.append(f"minimum text {min_text:.2f} pt < {fcfg['min']} pt")

    if max_text is not None and fcfg.get("max") is not None:
        if max_text <= fcfg["max"] + 0.15:
            passed.append(f"maximum text {max_text:.2f} pt <= {fcfg['max']} pt")
        else:
            warnings.append(f"maximum text {max_text:.2f} pt > recommended {fcfg['max']} pt")

    if cfg.get("recommended_min_text_pt") is not None and min_text is not None:
        if min_text >= cfg["recommended_min_text_pt"]:
            passed.append(
                f"minimum text {min_text:.2f} pt meets recommended {cfg['recommended_min_text_pt']} pt"
            )
        else:
            warnings.append(
                f"minimum text {min_text:.2f} pt below recommended {cfg['recommended_min_text_pt']} pt"
            )

    # Raster metadata
    dpi_x=metadata.get("dpi_x")
    mode=metadata.get("mode")
    if cfg.get("raster_dpi_min") is not None and dpi_x is not None:
        if dpi_x >= cfg["raster_dpi_min"]:
            passed.append(f"DPI {dpi_x:.0f} >= {cfg['raster_dpi_min']}")
        else:
            hard.append(f"DPI {dpi_x:.0f} < {cfg['raster_dpi_min']}")

    if cfg.get("color_mode") and mode:
        expected=cfg["color_mode"].upper()
        if mode.upper()==expected:
            passed.append(f"color mode {mode} matches {expected}")
        else:
            warnings.append(f"color mode {mode}; profile expects {expected}")

    preferred=[]
    if isinstance(cfg.get("preferred_format"),list):
        preferred=cfg["preferred_format"]
    if preferred and fmt and fmt not in preferred:
        warnings.append(f"format {fmt} not in preferred formats {preferred}")

    return {
        "journal":journal,
        "stage":stage,
        "hard_failures":hard,
        "warnings":warnings,
        "passes":passed,
        "pass":len(hard)==0,
        "profile_retrieved":profile.get("retrieved"),
        "official_sources":profile.get("official_sources",[]),
        "notes":cfg.get("notes",[]),
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("metadata_json")
    ap.add_argument("profile_yaml")
    ap.add_argument("--stage",required=True)
    ap.add_argument("--out")
    args=ap.parse_args()

    metadata=json.loads(Path(args.metadata_json).read_text(encoding="utf-8"))
    profile=yaml.safe_load(Path(args.profile_yaml).read_text(encoding="utf-8"))
    if args.stage not in profile["stages"]:
        raise SystemExit(f"Unknown stage {args.stage}. Available: {list(profile['stages'])}")
    res=validate(metadata,profile,args.stage)
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
