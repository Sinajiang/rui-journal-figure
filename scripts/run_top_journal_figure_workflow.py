from __future__ import annotations
import argparse, json, subprocess, sys, datetime
from pathlib import Path
import yaml

from workflow_utils import (
    resolve, load_yaml, load_json, save_json, new_state, now, sha256_file,
    stage_set, clear_pending_for_stage, add_agent_action, add_human_review,
    invalidate_downstream, STAGE_ORDER
)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def run_py(script, args, cwd=None):
    cmd=[sys.executable,str(HERE/script)] + [str(x) for x in args]
    cp=subprocess.run(cmd,capture_output=True,text=True,cwd=str(cwd) if cwd else None)
    return {
        "returncode":cp.returncode,
        "stdout":cp.stdout,
        "stderr":cp.stderr,
        "cmd":cmd
    }

def read_review(path: Path|None):
    if not path or not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))

class Workflow:
    def __init__(self, config_path: Path):
        self.config_path=config_path.resolve()
        self.base=self.config_path.parent
        self.cfg=load_yaml(self.config_path)
        work_name=(self.cfg.get("workflow") or {}).get("work_dir","TOP_JOURNAL_FIGURE_WORKFLOW")
        self.work=(self.base/work_name).resolve()
        self.work.mkdir(parents=True,exist_ok=True)
        self.state_path=self.work/"WORKFLOW_STATE.json"
        if self.state_path.exists():
            self.state=load_json(self.state_path)
        else:
            self.state=new_state((self.cfg.get("project") or {}).get("id",""))
            self.save()

    def save(self):
        save_json(self.state_path,self.state)

    def input(self,key):
        return resolve(self.base,(self.cfg.get("inputs") or {}).get(key))

    def source_inputs(self):
        vals=(self.cfg.get("inputs") or {}).get("source_data",[]) or []
        return [resolve(self.base,x) for x in vals]

    def status(self):
        return self.state

    def ingest(self):
        stage="INGEST"; clear_pending_for_stage(self.state,stage)
        out=self.work/"01_INGEST"; out.mkdir(exist_ok=True)
        manuscript=self.input("manuscript")
        sources=self.source_inputs()
        blocking=[]

        if not manuscript or not manuscript.exists():
            blocking.append({"type":"manuscript_missing","path":str(manuscript) if manuscript else None})
        for p in sources:
            if not p or not p.exists():
                blocking.append({"type":"source_missing","path":str(p)})

        if blocking:
            stage_set(self.state,stage,"BLOCKED",blocking=blocking)
            self.state["blocking"]=blocking
            self.state["current_state"]="BLOCKED"
            self.save(); return

        ingest_manifest={
            "manuscript":{
                "path":str(manuscript),
                "sha256":sha256_file(manuscript),
                "bytes":manuscript.stat().st_size
            },
            "source_data":[
                {
                    "path":str(p),
                    "sha256":sha256_file(p) if p.is_file() else None,
                    "bytes":p.stat().st_size if p.is_file() else None
                } for p in sources
            ]
        }
        save_json(out/"input_manifest.json",ingest_manifest)

        # manuscript sections
        sec=run_py("extract_manuscript_sections.py",[manuscript,"--out",out/"manuscript_sections.json"])
        # source tables if all are files
        table_files=[p for p in sources if p.is_file()]
        if table_files:
            si=run_py("inspect_source_tables.py",[*table_files,"--out",out/"source_inventory.json"])
        else:
            save_json(out/"source_inventory.json",{"tables":[],"note":"Directories require agent-level enumeration."})

        stage_set(self.state,stage,"COMPLETE",artifacts={
            "input_manifest":str(out/"input_manifest.json"),
            "manuscript_sections":str(out/"manuscript_sections.json"),
            "source_inventory":str(out/"source_inventory.json")
        })
        self.state["artifacts"]["INGEST"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="INGEST_COMPLETE"
        self.state["blocking"]=[]
        self.save()

    def journal_contract(self):
        stage="JOURNAL_CONTRACT"; clear_pending_for_stage(self.state,stage)
        out=self.work/"02_JOURNAL"; out.mkdir(exist_ok=True)
        profile=self.input("journal_profile")
        target=(self.cfg.get("project") or {}).get("target_journal","")
        allow=(self.cfg.get("workflow") or {}).get("allow_bundled_journal_profile",True)

        if profile and profile.exists():
            chosen=profile
            source="user_supplied"
        else:
            chosen=None
            if allow:
                key=target.lower().replace(" ","_").replace(":","").replace(",","")
                bundled={
                    "nature":ROOT/"journal_profiles/nature.yaml",
                    "headache":ROOT/"journal_profiles/headache.yaml",
                    "headache_the_journal_of_head_and_face_pain":ROOT/"journal_profiles/headache.yaml",
                    "brain_communications":ROOT/"journal_profiles/brain_communications.yaml",
                }
                # relaxed contains matching
                for k,v in bundled.items():
                    if k.replace("_"," ") in target.lower() or target.lower() in k.replace("_"," "):
                        chosen=v; break

            if chosen is None or not chosen.exists():
                stage_set(self.state,stage,"AGENT_ACTION_REQUIRED")
                add_agent_action(
                    self.state,stage,
                    "Verify the current official target-journal figure guidelines and create a journal profile.",
                    ["journal_profile.yaml"]
                )
                self.state["current_state"]="JOURNAL_CONTRACT_REQUIRED"
                self.save(); return
            source="bundled_profile"

        data=load_yaml(chosen)
        record={
            "target_journal":target,
            "profile_path":str(chosen),
            "profile_retrieved":data.get("retrieved"),
            "official_sources":data.get("official_sources",[]),
            "source":source,
            "warning":"Bundled profiles must be re-verified when stale or when submission-date requirements may have changed."
        }
        save_json(out/"journal_contract_record.json",record)

        # Bundled profile is usable as a planning baseline, but current web verification remains an agent action
        if source=="bundled_profile":
            add_agent_action(
                self.state,stage,
                "Re-verify the bundled journal profile against the current official author guidelines before final submission packaging.",
                ["verified_journal_profile_or_confirmation"]
            )

        stage_set(self.state,stage,"COMPLETE_WITH_VERIFICATION_PENDING" if source=="bundled_profile" else "COMPLETE",
                  artifacts={"journal_contract_record":str(out/"journal_contract_record.json")})
        self.state["artifacts"]["JOURNAL_CONTRACT"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="JOURNAL_CONTRACT_COMPLETE"
        self.save()

    def benchmark(self):
        stage="BENCHMARK"; clear_pending_for_stage(self.state,stage)
        out=self.work/"03_BENCHMARK"; out.mkdir(exist_ok=True)
        candidates=self.input("benchmark_candidates")

        # Always create a search brief scaffold.
        brief=out/"benchmark_search_brief.yaml"
        if not brief.exists():
            brief.write_text((ROOT/"templates/benchmark_search_brief.yaml").read_text(encoding="utf-8"),encoding="utf-8")
        run_py("generate_benchmark_queries.py",[brief,"--out",out/"generated_queries.json"])

        if not candidates or not candidates.exists():
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED",artifacts={
                "search_brief":str(brief),
                "generated_queries":str(out/"generated_queries.json")
            })
            add_agent_action(
                self.state,stage,
                "Search and verify current target-journal / peer-journal benchmark papers, then provide benchmark_candidates.tsv.",
                ["benchmark_candidates.tsv","benchmark_dossier_or_grammar"]
            )
            self.state["current_state"]="BENCHMARK_SEARCH_REQUIRED"
            self.save(); return

        # Provenance, normalize, rank, select
        prov=run_py("audit_benchmark_provenance.py",[candidates,"--out",out/"provenance_audit.json"])
        norm=run_py("normalize_benchmark_candidates.py",[
            candidates,"--normalized-out",out/"normalized_candidates.tsv",
            "--report-out",out/"dedup_report.json"
        ])
        rank=run_py("rank_benchmark_candidates.py",[out/"normalized_candidates.tsv","--out",out/"ranked.json"])
        min_n=int((self.cfg.get("workflow") or {}).get("benchmark_minimum",5))
        max_n=int((self.cfg.get("workflow") or {}).get("benchmark_maximum",10))
        sel=run_py("select_diverse_benchmark_set.py",[
            out/"ranked.json","--minimum",min_n,"--maximum",max_n,"--out",out/"selected.json"
        ])
        run_py("build_benchmark_dossier.py",[
            out/"selected.json",out/"normalized_candidates.tsv","--out",out/"benchmark_dossier.md"
        ])

        audit=load_json(out/"provenance_audit.json")
        if not audit.get("pass"):
            stage_set(self.state,stage,"BLOCKED",blocking=audit.get("blocking",[]))
            self.state["blocking"]=audit.get("blocking",[])
            self.state["current_state"]="BLOCKED"
            self.save(); return

        stage_set(self.state,stage,"COMPLETE",artifacts={
            "normalized_candidates":str(out/"normalized_candidates.tsv"),
            "ranked":str(out/"ranked.json"),
            "selected":str(out/"selected.json"),
            "dossier":str(out/"benchmark_dossier.md")
        })
        self.state["artifacts"]["BENCHMARK"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="BENCHMARK_CORPUS_COMPLETE"
        self.save()

    def evidence(self):
        stage="EVIDENCE"; clear_pending_for_stage(self.state,stage)
        out=self.work/"04_EVIDENCE"; out.mkdir(exist_ok=True)
        graph=self.input("evidence_graph")
        if not graph or not graph.exists():
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED",artifacts={
                "evidence_graph_template":str(ROOT/"templates/evidence_graph.yaml")
            })
            add_agent_action(
                self.state,stage,
                "Read Methods, Results, legends, source tables, and benchmark dossier; construct claim → figure/panel → source → statistic → legend evidence graph.",
                ["evidence_graph.yaml","panel_candidate_inventory.tsv"]
            )
            self.state["current_state"]="EVIDENCE_MAPPING_REQUIRED"
            self.save(); return

        run_py("audit_evidence_graph.py",[graph,"--out",out/"evidence_graph_audit.json"])
        audit=load_json(out/"evidence_graph_audit.json")
        if not audit.get("pass"):
            stage_set(self.state,stage,"BLOCKED",blocking=audit.get("blocking",[]))
            self.state["blocking"]=audit.get("blocking",[])
            self.state["current_state"]="BLOCKED"
            self.save(); return

        stage_set(self.state,stage,"COMPLETE",artifacts={
            "evidence_graph":str(graph),
            "audit":str(out/"evidence_graph_audit.json")
        })
        self.state["artifacts"]["EVIDENCE"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="EVIDENCE_GRAPH_COMPLETE"
        self.save()


    def domain_grammar(self):
        stage="DOMAIN_GRAMMAR"; clear_pending_for_stage(self.state,stage)
        out=self.work/"04B_DOMAIN_GRAMMAR"; out.mkdir(exist_ok=True)

        selection=self.input("domain_selection")
        if not selection or not selection.exists():
            # infer from ingest artifacts to create an advisory suggestion
            ingest=(self.state.get("artifacts",{}).get("INGEST") or {})
            paths=[]
            for key in ["manuscript_sections","source_inventory"]:
                p=ingest.get(key)
                if p and Path(p).exists():
                    paths.append(Path(p))
            if paths:
                run_py("infer_scientific_domain.py",[
                    *paths,"--out",out/"domain_inference.json"
                ])
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED",artifacts={
                "domain_inference":str(out/"domain_inference.json") if (out/"domain_inference.json").exists() else None,
                "selection_template":str(ROOT/"templates/domain_selection.yaml")
            })
            add_agent_action(
                self.state,stage,
                "Confirm the primary scientific domain and optional secondary domains, then provide domain_selection.yaml.",
                ["domain_selection.yaml"]
            )
            self.state["current_state"]="DOMAIN_GRAMMAR_SELECTION_REQUIRED"
            self.save(); return

        run_py("resolve_domain_grammar.py",[
            selection,"--out",out/"resolved_domain_grammar.json"
        ])
        run_py("recommend_domain_figure_grammar.py",[
            out/"resolved_domain_grammar.json","--out",out/"domain_figure_recommendations.json"
        ])
        stage_set(self.state,stage,"COMPLETE",artifacts={
            "selection":str(selection),
            "grammar":str(out/"resolved_domain_grammar.json"),
            "recommendations":str(out/"domain_figure_recommendations.json")
        })
        self.state["artifacts"]["DOMAIN_GRAMMAR"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="DOMAIN_GRAMMAR_COMPLETE"
        self.save()

    def architecture(self):
        stage="ARCHITECTURE"; clear_pending_for_stage(self.state,stage)
        out=self.work/"05_ARCHITECTURE"; out.mkdir(exist_ok=True)
        opt=self.input("optimizer_input")
        panel=self.input("panel_inventory")
        if not opt or not opt.exists() or not panel or not panel.exists():
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED")
            add_agent_action(
                self.state,stage,
                "Create panel_candidate_inventory.tsv and architecture_optimizer_input.yaml from the evidence graph and benchmark dossier.",
                ["panel_candidate_inventory.tsv","architecture_optimizer_input.yaml"]
            )
            self.state["current_state"]="ARCHITECTURE_INPUT_REQUIRED"
            self.save(); return

        # Optimizer expects panel inventory relative to optimizer input; user should configure exact path.
        run_py("compute_panel_redundancy.py",[panel,"--out",out/"redundancy.json"])
        run_py("optimize_main_figure_architecture.py",[opt,"--out",out/"architecture_candidates.json"])
        run_py("recommend_panel_actions.py",[opt,"--out",out/"panel_actions.json"])
        data=load_json(out/"architecture_candidates.json")
        if data.get("recommended_target_figure_count") is None:
            stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"no_eligible_architecture"}])
            self.state["blocking"]=[{"type":"no_eligible_architecture"}]
            self.state["current_state"]="BLOCKED"
            self.save(); return

        stage_set(self.state,stage,"COMPLETE",artifacts={
            "candidates":str(out/"architecture_candidates.json"),
            "redundancy":str(out/"redundancy.json"),
            "panel_actions":str(out/"panel_actions.json")
        })
        self.state["artifacts"]["ARCHITECTURE"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="ARCHITECTURE_OPTIMIZED"
        self.save()


    def visual_weighting(self):
        stage="VISUAL_WEIGHTING"; clear_pending_for_stage(self.state,stage)
        out=self.work/"05B_VISUAL_WEIGHTING"; out.mkdir(exist_ok=True)
        panel=self.input("panel_inventory")
        arch_art=(self.state.get("artifacts",{}).get("ARCHITECTURE") or {})
        cpath=Path(arch_art.get("candidates",""))
        if not panel or not panel.exists() or not cpath.exists():
            stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"architecture_or_panel_inventory_missing"}])
            self.state["current_state"]="BLOCKED"; self.save(); return
        run_py("score_panel_contribution.py",[panel,"--out",out/"panel_contribution.json"])
        data=load_json(cpath); rec_count=data.get("recommended_target_figure_count")
        if rec_count is None:
            stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"no_recommended_architecture"}])
            self.state["current_state"]="BLOCKED"; self.save(); return
        rec=[x for x in data["candidates"] if x["target_figure_count"]==rec_count][0]
        rec_json=out/"recommended_candidate.json"; save_json(rec_json,rec)
        run_py("allocate_visual_area.py",[rec_json,out/"panel_contribution.json","--out",out/"visual_weight_plan.json"])
        run_py("audit_visual_weight_scientific_alignment.py",[out/"visual_weight_plan.json","--out",out/"visual_weight_audit.json"])
        run_py("recommend_contribution_actions.py",[out/"panel_contribution.json","--out",out/"contribution_actions.json"])
        run_py("build_weighted_architecture_prototype.py",[out/"visual_weight_plan.json","--out-pdf",out/"weighted_prototype.pdf","--out-png",out/"weighted_prototype.png"])
        qa=load_json(out/"visual_weight_audit.json")
        if not qa.get("pass"):
            stage_set(self.state,stage,"BLOCKED",blocking=qa.get("blocking",[])); self.state["current_state"]="BLOCKED"; self.save(); return
        stage_set(self.state,stage,"COMPLETE",artifacts={
            "panel_contribution":str(out/"panel_contribution.json"),
            "visual_weight_plan":str(out/"visual_weight_plan.json"),
            "visual_weight_audit":str(out/"visual_weight_audit.json"),
            "contribution_actions":str(out/"contribution_actions.json"),
            "weighted_prototype":str(out/"weighted_prototype.pdf")
        })
        self.state["artifacts"]["VISUAL_WEIGHTING"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="VISUAL_WEIGHTING_COMPLETE"; self.save()


    def layout_grammar(self):
        stage="LAYOUT_GRAMMAR"; clear_pending_for_stage(self.state,stage)
        out=self.work/"05C_LAYOUT_GRAMMAR"; out.mkdir(exist_ok=True)
        annotations=self.input("benchmark_layout_annotations")
        if not annotations or not annotations.exists():
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED",artifacts={"annotation_template":str(ROOT/"templates/benchmark_layout_annotation.tsv")})
            add_agent_action(self.state,stage,"Annotate selected benchmark figures for geometry/topology/white-space/legend/text density.",["benchmark_layout_annotation.tsv"])
            self.state["current_state"]="LAYOUT_GRAMMAR_ANNOTATION_REQUIRED"; self.save(); return
        run_py("validate_benchmark_layout_annotations.py",[annotations,"--out",out/"annotation_validation.json"])
        qa=load_json(out/"annotation_validation.json")
        if not qa.get("pass"):
            stage_set(self.state,stage,"BLOCKED",blocking=qa.get("blocking",[])); self.state["blocking"]=qa.get("blocking",[]); self.state["current_state"]="BLOCKED"; self.save(); return
        run_py("aggregate_benchmark_layout_grammar.py",[annotations,"--out",out/"layout_grammar.json"])
        run_py("build_layout_grammar_report.py",[out/"layout_grammar.json","--out",out/"layout_grammar_report.md"])
        stage_set(self.state,stage,"COMPLETE",artifacts={"grammar":str(out/"layout_grammar.json"),"report":str(out/"layout_grammar_report.md")})
        self.state["artifacts"]["LAYOUT_GRAMMAR"]=self.state["stages"][stage]["artifacts"]; self.state["current_state"]="LAYOUT_GRAMMAR_COMPLETE"; self.save()

    def visual_hierarchy(self):
        stage="VISUAL_HIERARCHY"; clear_pending_for_stage(self.state,stage)
        out=self.work/"05D_VISUAL_HIERARCHY"; out.mkdir(exist_ok=True)
        vw=(self.state.get("artifacts",{}).get("VISUAL_WEIGHTING") or {}).get("visual_weight_plan")
        lg=(self.state.get("artifacts",{}).get("LAYOUT_GRAMMAR") or {}).get("grammar")
        if not vw or not Path(vw).exists() or not lg or not Path(lg).exists():
            stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"visual_weight_or_layout_grammar_missing"}])
            self.state["current_state"]="BLOCKED"; self.save(); return
        run_py("solve_layouts_from_visual_weight_plan.py",[
            vw,lg,"--out",out/"solved_layouts.json"
        ])
        run_py("derive_visual_hierarchy.py",[
            out/"solved_layouts.json","--out",out/"visual_hierarchy.json"
        ])
        run_py("audit_visual_hierarchy_consistency.py",[
            out/"visual_hierarchy.json","--out",out/"visual_hierarchy_audit.json"
        ])
        run_py("build_visual_hierarchy_report.py",[
            out/"visual_hierarchy.json","--out",out/"visual_hierarchy_report.md"
        ])
        qa=load_json(out/"visual_hierarchy_audit.json")
        if not qa.get("pass"):
            stage_set(self.state,stage,"BLOCKED",blocking=qa.get("blocking",[]))
            self.state["blocking"]=qa.get("blocking",[]); self.state["current_state"]="BLOCKED"; self.save(); return
        stage_set(self.state,stage,"COMPLETE",artifacts={
            "solved_layouts":str(out/"solved_layouts.json"),
            "visual_hierarchy":str(out/"visual_hierarchy.json"),
            "audit":str(out/"visual_hierarchy_audit.json"),
            "report":str(out/"visual_hierarchy_report.md")
        })
        self.state["artifacts"]["VISUAL_HIERARCHY"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="VISUAL_HIERARCHY_COMPLETE"; self.save()

    def annotation_intelligence(self):
        stage="ANNOTATION_INTELLIGENCE"; clear_pending_for_stage(self.state,stage)
        out=self.work/"05E_ANNOTATION_INTELLIGENCE"; out.mkdir(exist_ok=True)
        inv=self.input("annotation_candidate_inventory")
        ev=(self.state.get("artifacts",{}).get("EVIDENCE") or {}).get("evidence_graph")
        vh=(self.state.get("artifacts",{}).get("VISUAL_HIERARCHY") or {}).get("visual_hierarchy")
        lg=(self.state.get("artifacts",{}).get("LAYOUT_GRAMMAR") or {}).get("grammar")
        if (not inv or not inv.exists()) and ev and Path(ev).exists():
            auto=out/"annotation_candidate_inventory.auto.tsv"
            run_py("extract_annotation_candidates_from_evidence_graph.py",[ev,"--out",auto])
            if auto.exists() and auto.stat().st_size>0:
                inv=auto
        if not inv or not inv.exists():
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED",artifacts={
                "inventory_template":str(ROOT/"templates/annotation_candidate_inventory.tsv"),
                "prompt":str(ROOT/"prompts/automatic-annotation-legend-intelligence.md")
            })
            add_agent_action(self.state,stage,
                "Materialize the annotation candidate inventory from Results, Methods, source tables, evidence graph, and benchmark evidence; do not recalculate frozen statistics.",
                ["annotation_candidate_inventory.tsv"])
            self.state["current_state"]="ANNOTATION_INVENTORY_REQUIRED"; self.save(); return
        args=[inv,"--out",out/"annotation_legend_plan.json"]
        if lg and Path(lg).exists(): args += ["--benchmark-grammar",lg]
        if vh and Path(vh).exists(): args += ["--visual-hierarchy",vh]
        run_py("derive_annotation_legend_plan.py",args)
        run_py("audit_annotation_legend_plan.py",[out/"annotation_legend_plan.json","--out",out/"annotation_legend_audit.json"])
        run_py("build_annotation_legend_report.py",[out/"annotation_legend_plan.json","--out",out/"annotation_legend_report.md"])
        qa=load_json(out/"annotation_legend_audit.json")
        if not qa.get("pass"):
            stage_set(self.state,stage,"BLOCKED",blocking=qa.get("blocking",[]))
            self.state["blocking"]=qa.get("blocking",[]); self.state["current_state"]="BLOCKED"; self.save(); return
        stage_set(self.state,stage,"COMPLETE",artifacts={
            "inventory":str(inv),
            "plan":str(out/"annotation_legend_plan.json"),
            "audit":str(out/"annotation_legend_audit.json"),
            "report":str(out/"annotation_legend_report.md")
        })
        self.state["artifacts"]["ANNOTATION_INTELLIGENCE"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="ANNOTATION_INTELLIGENCE_COMPLETE"; self.save()

    def prototype(self):
        stage="PROTOTYPE"; clear_pending_for_stage(self.state,stage)
        out=self.work/"06_PROTOTYPE"; out.mkdir(exist_ok=True)
        arch_art=(self.state.get("artifacts",{}).get("ARCHITECTURE") or {})
        cand_path=Path(arch_art.get("candidates",""))
        panel=self.input("panel_inventory")
        if not cand_path.exists() or not panel or not panel.exists():
            stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"architecture_or_panel_inventory_missing"}])
            self.state["current_state"]="BLOCKED"; self.save(); return

        data=load_json(cand_path)
        rec_count=data["recommended_target_figure_count"]
        rec=[x for x in data["candidates"] if x["target_figure_count"]==rec_count][0]
        rec_json=out/"recommended_candidate.json"
        save_json(rec_json,rec)
        run_py("build_architecture_prototype.py",[
            rec_json,panel,"--out-pdf",out/"prototype.pdf","--out-png",out/"prototype.png"
        ])
        run_py("score_structural_prototype.py",[
            rec_json,panel,"--out",out/"prototype_score.json"
        ])

        review=read_review(out/"manual_prototype_review.yaml")
        require=bool((self.cfg.get("workflow") or {}).get("require_manual_prototype_review",True))
        if require and (not review or str(review.get("status","")).upper()!="PASS"):
            if not (out/"manual_prototype_review.yaml").exists():
                (out/"manual_prototype_review.yaml").write_text(
                    (ROOT/"templates/manual_review_record.yaml").read_text(encoding="utf-8")
                    .replace('stage: ""','stage: "PROTOTYPE"'),
                    encoding="utf-8"
                )
            stage_set(self.state,stage,"HUMAN_REVIEW_REQUIRED",artifacts={
                "prototype_pdf":str(out/"prototype.pdf"),
                "prototype_png":str(out/"prototype.png"),
                "score":str(out/"prototype_score.json"),
                "review_record":str(out/"manual_prototype_review.yaml")
            })
            add_human_review(
                self.state,stage,
                "Review the structural prototype at final physical size and record PASS/FAIL.",
                str(out/"manual_prototype_review.yaml")
            )
            self.state["current_state"]="PROTOTYPE_REVIEW_REQUIRED"
            self.save(); return

        stage_set(self.state,stage,"COMPLETE",artifacts={
            "prototype_pdf":str(out/"prototype.pdf"),
            "prototype_png":str(out/"prototype.png"),
            "score":str(out/"prototype_score.json"),
            "review_record":str(out/"manual_prototype_review.yaml")
        })
        self.state["artifacts"]["PROTOTYPE"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="ARCHITECTURE_PROMOTED"
        self.save()

    def real_data(self):
        stage="REAL_DATA"; clear_pending_for_stage(self.state,stage)
        out=self.work/"07_REAL_DATA"; out.mkdir(exist_ok=True)
        # The AI/expert must materialize actual render specs from promoted architecture.
        specs=sorted(out.glob("Figure_*_render_spec.yaml"))
        if not specs:
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED")
            add_agent_action(
                self.state,stage,
                "Create explicit Figure_N_render_spec.yaml files and sentinel contracts from the promoted architecture and frozen source data, then inject the approved annotation-intelligence plan before rendering.",
                ["Figure_N_render_spec.yaml","sentinel_contracts","annotation_intelligence_applied"]
            )
            self.state["current_state"]="REAL_DATA_RENDER_SPEC_REQUIRED"
            self.save(); return

        ann=(self.state.get("artifacts",{}).get("ANNOTATION_INTELLIGENCE") or {}).get("plan")
        if not ann or not Path(ann).exists():
            stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"annotation_intelligence_plan_missing"}])
            self.state["current_state"]="BLOCKED"; self.save(); return

        results=[]
        for spec in specs:
            fig_id=load_yaml(spec)["figure"]["id"]
            annotated_spec=out/f"{fig_id}_render_spec.annotated.yaml"
            run_py("apply_annotation_plan_to_render_spec.py",[spec,ann,"--out",annotated_spec])
            if not annotated_spec.exists():
                stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"annotation_plan_injection_failed","figure_id":fig_id}])
                self.state["current_state"]="BLOCKED"; self.save(); return
            sent=out/f"{fig_id}_sentinels.yaml"
            fig_out=out/fig_id
            args=[annotated_spec,"--output-dir",fig_out,"--out",fig_out/"production_summary.json"]
            if sent.exists():
                args += ["--sentinels",sent]
            cp=run_py("produce_real_data_figure.py",args)
            summary=load_json(fig_out/"production_summary.json") if (fig_out/"production_summary.json").exists() else None
            results.append({"figure":fig_id,"returncode":cp["returncode"],"summary":summary,"annotated_render_spec":str(annotated_spec)})
            if not summary or summary.get("status")=="FAIL_SENTINEL":
                stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"real_data_render_failure","figure":fig_id}])
                self.state["current_state"]="BLOCKED"; self.save(); return

        save_json(out/"real_data_stage_summary.json",{"figures":results})
        stage_set(self.state,stage,"COMPLETE",artifacts={"summary":str(out/"real_data_stage_summary.json")})
        self.state["artifacts"]["REAL_DATA"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="REAL_DATA_RENDERED_PRE_PROMOTION"
        self.save()

    def final_figure_review(self):
        stage="FINAL_FIGURE_REVIEW"; clear_pending_for_stage(self.state,stage)
        out=self.work/"08_FINAL_FIGURE_REVIEW"; out.mkdir(exist_ok=True)
        review_path=out/"manual_final_figure_review.yaml"
        review=read_review(review_path)
        require=bool((self.cfg.get("workflow") or {}).get("require_manual_final_figure_review",True))
        if require and (not review or str(review.get("status","")).upper()!="PASS"):
            if not review_path.exists():
                review_path.write_text(
                    (ROOT/"templates/manual_review_record.yaml").read_text(encoding="utf-8")
                    .replace('stage: ""','stage: "FINAL_FIGURE_REVIEW"'),
                    encoding="utf-8"
                )
            stage_set(self.state,stage,"HUMAN_REVIEW_REQUIRED",artifacts={"review_record":str(review_path)})
            add_human_review(
                self.state,stage,
                "Review all real-data figure PDFs/TIFFs at final size and record PASS/FAIL.",
                str(review_path)
            )
            self.state["current_state"]="FINAL_FIGURE_REVIEW_REQUIRED"
            self.save(); return

        stage_set(self.state,stage,"COMPLETE",artifacts={"review_record":str(review_path)})
        self.state["artifacts"]["FINAL_FIGURE_REVIEW"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="FIGURES_PROMOTED"
        self.save()

    def compilation(self):
        stage="COMPILATION"; clear_pending_for_stage(self.state,stage)
        out=self.work/"09_COMPILATION"; out.mkdir(exist_ok=True)
        manifest=out/"figure_set_manifest.yaml"
        if not manifest.exists():
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED")
            add_agent_action(
                self.state,stage,
                "Create figure_set_manifest.yaml using only exact promoted figure versions, legends, source data, provenance, and style contracts.",
                ["figure_set_manifest.yaml"]
            )
            self.state["current_state"]="FIGURE_SET_MANIFEST_REQUIRED"
            self.save(); return

        pkg=out/"COMPILED_PACKAGE"
        run_py("compile_final_submission_figures.py",[
            manifest,"--output-dir",pkg,"--out",out/"compilation_run.json"
        ])
        summary=load_json(pkg/"COMPILATION_SUMMARY.json")
        if summary.get("blocking"):
            stage_set(self.state,stage,"BLOCKED",blocking=summary["blocking"])
            self.state["blocking"]=summary["blocking"]
            self.state["current_state"]="BLOCKED"
            self.save(); return
        stage_set(self.state,stage,"COMPLETE",artifacts={
            "compiled_package":str(pkg),
            "compilation_summary":str(pkg/"COMPILATION_SUMMARY.json"),
            "contact_sheet":str(pkg/"QA/figure_set_contact_sheet.png")
        })
        self.state["artifacts"]["COMPILATION"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="FIGURE_PACKAGE_COMPILED_PRE_SUBMISSION"
        self.save()

    def contact_review(self):
        stage="CONTACT_SHEET_REVIEW"; clear_pending_for_stage(self.state,stage)
        out=self.work/"10_CONTACT_SHEET_REVIEW"; out.mkdir(exist_ok=True)
        review_path=out/"manual_contact_sheet_review.yaml"
        review=read_review(review_path)
        require=bool((self.cfg.get("workflow") or {}).get("require_manual_contact_sheet_review",True))
        if require and (not review or str(review.get("status","")).upper()!="PASS"):
            if not review_path.exists():
                review_path.write_text(
                    (ROOT/"templates/manual_review_record.yaml").read_text(encoding="utf-8")
                    .replace('stage: ""','stage: "CONTACT_SHEET_REVIEW"'),
                    encoding="utf-8"
                )
            stage_set(self.state,stage,"HUMAN_REVIEW_REQUIRED",artifacts={"review_record":str(review_path)})
            add_human_review(
                self.state,stage,
                "Review the manuscript-level figure contact sheet and record PASS/FAIL.",
                str(review_path)
            )
            self.state["current_state"]="CONTACT_SHEET_REVIEW_REQUIRED"
            self.save(); return
        stage_set(self.state,stage,"COMPLETE",artifacts={"review_record":str(review_path)})
        self.state["artifacts"]["CONTACT_SHEET_REVIEW"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="CONTACT_SHEET_REVIEW_COMPLETE"
        self.save()

    def reintegration(self):
        stage="REINTEGRATION"; clear_pending_for_stage(self.state,stage)
        out=self.work/"11_REINTEGRATION"; out.mkdir(exist_ok=True)
        # Exact reintegration needs manuscript + evidence graph + legend architecture.
        graph=self.input("evidence_graph")
        manuscript=self.input("manuscript")
        legend_arch=out/"legend_architecture.yaml"
        if not graph or not graph.exists() or not legend_arch.exists():
            stage_set(self.state,stage,"AGENT_ACTION_REQUIRED")
            add_agent_action(
                self.state,stage,
                "Synchronize the final manuscript's figure/panel citations and legends; provide legend_architecture.yaml, then run exact reintegration QA.",
                ["legend_architecture.yaml","updated_exact_manuscript_if_needed"]
            )
            self.state["current_state"]="MANUSCRIPT_REINTEGRATION_REQUIRED"
            self.save(); return
        run_py("manuscript_figure_reintegration_qa.py",[
            manuscript,graph,legend_arch,"--out",out/"reintegration_qa.json"
        ])
        qa=load_json(out/"reintegration_qa.json")
        if not qa.get("hard_pass"):
            stage_set(self.state,stage,"BLOCKED",blocking=[{"type":"reintegration_qa_failed"}])
            self.state["current_state"]="BLOCKED"; self.save(); return
        stage_set(self.state,stage,"COMPLETE",artifacts={"reintegration_qa":str(out/"reintegration_qa.json")})
        self.state["artifacts"]["REINTEGRATION"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="MANUSCRIPT_REINTEGRATION_COMPLETE"
        self.save()

    def submission_ready(self):
        stage="SUBMISSION_READY"; clear_pending_for_stage(self.state,stage)
        # Require journal verification action to be explicitly cleared by a confirmation file.
        out=self.work/"12_SUBMISSION_READY"; out.mkdir(exist_ok=True)
        confirmation=out/"journal_upload_contract_confirmation.yaml"
        conf=read_review(confirmation)
        if not conf or str(conf.get("status","")).upper()!="PASS":
            if not confirmation.exists():
                confirmation.write_text(
                    (ROOT/"templates/manual_review_record.yaml").read_text(encoding="utf-8")
                    .replace('stage: ""','stage: "SUBMISSION_READY"')
                    .replace('review_id: ""','review_id: "journal_upload_contract"'),
                    encoding="utf-8"
                )
            stage_set(self.state,stage,"HUMAN_REVIEW_REQUIRED",artifacts={"journal_confirmation":str(confirmation)})
            add_human_review(
                self.state,stage,
                "Confirm the current target-journal upload contract / portal requirements are satisfied.",
                str(confirmation)
            )
            self.state["current_state"]="JOURNAL_UPLOAD_CONTRACT_REVIEW_REQUIRED"
            self.save(); return

        stage_set(self.state,stage,"COMPLETE",artifacts={"journal_confirmation":str(confirmation)})
        self.state["artifacts"]["SUBMISSION_READY"]=self.state["stages"][stage]["artifacts"]
        self.state["current_state"]="FIGURE_PACKAGE_SUBMISSION_READY"
        self.save()

    def run_stage(self,stage):
        fn={
            "INGEST":self.ingest,
            "JOURNAL_CONTRACT":self.journal_contract,
            "BENCHMARK":self.benchmark,
            "EVIDENCE":self.evidence,
            "DOMAIN_GRAMMAR":self.domain_grammar,
            "ARCHITECTURE":self.architecture,
            "VISUAL_WEIGHTING":self.visual_weighting,
            "LAYOUT_GRAMMAR":self.layout_grammar,
            "VISUAL_HIERARCHY":self.visual_hierarchy,
            "ANNOTATION_INTELLIGENCE":self.annotation_intelligence,
            "PROTOTYPE":self.prototype,
            "REAL_DATA":self.real_data,
            "FINAL_FIGURE_REVIEW":self.final_figure_review,
            "COMPILATION":self.compilation,
            "CONTACT_SHEET_REVIEW":self.contact_review,
            "REINTEGRATION":self.reintegration,
            "SUBMISSION_READY":self.submission_ready,
        }.get(stage)
        if not fn:
            raise ValueError(stage)
        fn()

    def resume(self):
        for stage in STAGE_ORDER:
            rec=self.state["stages"].get(stage)
            if rec and rec.get("status")=="COMPLETE":
                continue
            if rec and rec.get("status")=="COMPLETE_WITH_VERIFICATION_PENDING":
                continue
            self.run_stage(stage)
            status=self.state["stages"].get(stage,{}).get("status")
            if status not in {"COMPLETE","COMPLETE_WITH_VERIFICATION_PENDING"}:
                break

    def dry_run(self):
        return {
            "project":self.cfg.get("project"),
            "work_dir":str(self.work),
            "current_state":self.state.get("current_state"),
            "stage_order":STAGE_ORDER,
            "next_incomplete":next((
                s for s in STAGE_ORDER
                if self.state["stages"].get(s,{}).get("status") not in {"COMPLETE","COMPLETE_WITH_VERIFICATION_PENDING"}
            ),None),
            "pending_agent_actions":self.state.get("pending_agent_actions",[]),
            "pending_human_reviews":self.state.get("pending_human_reviews",[])
        }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("config")
    g=ap.add_mutually_exclusive_group()
    g.add_argument("--status",action="store_true")
    g.add_argument("--resume",action="store_true")
    g.add_argument("--stage",choices=STAGE_ORDER)
    g.add_argument("--dry-run",action="store_true")
    g.add_argument("--reset-stage",choices=STAGE_ORDER)
    args=ap.parse_args()

    wf=Workflow(Path(args.config))
    if args.status:
        print(json.dumps(wf.status(),indent=2,ensure_ascii=False))
    elif args.dry_run:
        print(json.dumps(wf.dry_run(),indent=2,ensure_ascii=False))
    elif args.reset_stage:
        invalidate_downstream(wf.state,args.reset_stage)
        wf.save()
        print(json.dumps(wf.status(),indent=2,ensure_ascii=False))
    elif args.stage:
        wf.run_stage(args.stage)
        print(json.dumps(wf.status(),indent=2,ensure_ascii=False))
    else:
        wf.resume()
        print(json.dumps(wf.status(),indent=2,ensure_ascii=False))
