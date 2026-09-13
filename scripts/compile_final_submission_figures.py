from __future__ import annotations
import argparse, json, shutil, datetime
from pathlib import Path
from submission_compiler_utils import load_yaml, resolve, sha256_file
from validate_figure_set_manifest import validate as validate_manifest
from audit_cross_figure_style import audit as audit_style
from audit_figure_set_rasters import audit as audit_rasters
from build_figure_set_contact_sheet import build as build_contact

def copy_if(src, dst):
    if src and src.exists():
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        return True
    return False

def compile(manifest_path: Path, out_dir: Path):
    m=load_yaml(manifest_path); base=manifest_path.parent
    out_dir.mkdir(parents=True,exist_ok=True)

    qa_dir=out_dir/"QA"; qa_dir.mkdir(exist_ok=True)
    final_dir=out_dir/"FINAL_SUBMISSION_FIGURES"; final_dir.mkdir(exist_ok=True)
    edit_dir=out_dir/"EDITABLE"; edit_dir.mkdir(exist_ok=True)
    prev_dir=out_dir/"PREVIEWS"; prev_dir.mkdir(exist_ok=True)
    src_out=out_dir/"SOURCE_DATA"; src_out.mkdir(exist_ok=True)
    leg_out=out_dir/"LEGENDS"; leg_out.mkdir(exist_ok=True)
    prov_out=out_dir/"PROVENANCE"; prov_out.mkdir(exist_ok=True)

    vm=validate_manifest(manifest_path)
    st=audit_style(manifest_path)
    rs=audit_rasters(manifest_path)

    (qa_dir/"manifest_validation.json").write_text(json.dumps(vm,indent=2,ensure_ascii=False),encoding="utf-8")
    (qa_dir/"cross_figure_style.json").write_text(json.dumps(st,indent=2,ensure_ascii=False),encoding="utf-8")
    (qa_dir/"raster_audit.json").write_text(json.dumps(rs,indent=2,ensure_ascii=False),encoding="utf-8")

    blocking=[]
    blocking += vm["blocking"]
    blocking += st["blocking"]
    blocking += rs["blocking"]

    copied=[]
    for f in m.get("figures",[]) or []:
        n=f["number"]
        mapping=[
            ("pdf", final_dir/f"Figure_{n}.pdf"),
            ("tiff", final_dir/f"Figure_{n}.tiff"),
            ("svg", edit_dir/f"Figure_{n}.svg"),
            ("preview", prev_dir/f"Figure_{n}_preview.png"),
            ("legend", leg_out/f"Figure_{n}_legend.txt"),
            ("provenance", prov_out/f"Figure_{n}_provenance.json"),
        ]
        for key,dst in mapping:
            src=resolve(base,f.get(key))
            if copy_if(src,dst):
                copied.append(str(dst.relative_to(out_dir)))

        sd=resolve(base,f.get("source_data_dir"))
        if sd and sd.exists():
            target=src_out/f"Figure_{n}"
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(sd,target)
            for x in target.rglob("*"):
                if x.is_file():
                    copied.append(str(x.relative_to(out_dir)))

    # Contact sheet.
    contact=qa_dir/"figure_set_contact_sheet.png"
    try:
        build_contact(manifest_path,contact)
        copied.append(str(contact.relative_to(out_dir)))
    except Exception as e:
        blocking.append({"type":"contact_sheet_failed","error":str(e)})

    # Hash manifest.
    hashes=[]
    for p in sorted(out_dir.rglob("*")):
        if p.is_file() and p.name!="MANIFEST_SHA256.json":
            hashes.append({
                "file":str(p.relative_to(out_dir)),
                "bytes":p.stat().st_size,
                "sha256":sha256_file(p)
            })
    (out_dir/"MANIFEST_SHA256.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")

    state="FIGURE_PACKAGE_COMPILED / PRE-SUBMISSION" if not blocking else "FIGURE_PACKAGE_BLOCKED"
    summary={
        "state":state,
        "compiled_at":datetime.datetime.now().isoformat(),
        "target_journal":(m.get("project") or {}).get("target_journal"),
        "manuscript_authority":(m.get("project") or {}).get("manuscript_authority"),
        "figure_count":len(m.get("figures",[]) or []),
        "blocking":blocking,
        "manual_contact_sheet_review_required":True,
        "submission_ready":False,
        "copied_files":copied
    }
    (out_dir/"COMPILATION_SUMMARY.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    return summary

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--out")
    args=ap.parse_args()
    res=compile(Path(args.manifest),Path(args.output_dir))
    txt=json.dumps(res,indent=2,ensure_ascii=False)
    print(txt)
    if args.out:
        Path(args.out).write_text(txt,encoding="utf-8")
