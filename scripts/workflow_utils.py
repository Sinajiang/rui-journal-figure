from __future__ import annotations
from pathlib import Path
import hashlib, json, datetime, yaml, uuid, shutil

STAGE_ORDER=[
    "INGEST",
    "JOURNAL_CONTRACT",
    "BENCHMARK",
    "EVIDENCE",
    "DOMAIN_GRAMMAR",
    "ARCHITECTURE",
    "VISUAL_WEIGHTING",
    "LAYOUT_GRAMMAR",
    "VISUAL_HIERARCHY",
    "ANNOTATION_INTELLIGENCE",
    "PROTOTYPE",
    "REAL_DATA",
    "FINAL_FIGURE_REVIEW",
    "COMPILATION",
    "CONTACT_SHEET_REVIEW",
    "REINTEGRATION",
    "SUBMISSION_READY",
]

def now():
    return datetime.datetime.now().astimezone().isoformat()

def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def resolve(base: Path, value):
    if not value:
        return None
    p=Path(value)
    return p if p.is_absolute() else (base/p).resolve()

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding="utf-8")

def new_state(project_id):
    return {
        "project_id":project_id,
        "run_id":str(uuid.uuid4()),
        "current_state":"INIT",
        "updated_at":now(),
        "stages":{},
        "pending_agent_actions":[],
        "pending_human_reviews":[],
        "artifacts":{},
        "blocking":[]
    }

def stage_set(state, stage, status, **kwargs):
    rec=state["stages"].get(stage,{})
    rec.update({"status":status,"updated_at":now(),**kwargs})
    state["stages"][stage]=rec
    state["updated_at"]=now()

def clear_pending_for_stage(state, stage):
    state["pending_agent_actions"]=[
        x for x in state.get("pending_agent_actions",[])
        if x.get("stage")!=stage
    ]
    state["pending_human_reviews"]=[
        x for x in state.get("pending_human_reviews",[])
        if x.get("stage")!=stage
    ]

def add_agent_action(state, stage, action, required_artifacts=None):
    item={
        "stage":stage,
        "action":action,
        "required_artifacts":required_artifacts or []
    }
    if item not in state["pending_agent_actions"]:
        state["pending_agent_actions"].append(item)

def add_human_review(state, stage, review, required_artifact=None):
    item={"stage":stage,"review":review}
    if required_artifact:
        item["required_artifact"]=required_artifact
    if item not in state["pending_human_reviews"]:
        state["pending_human_reviews"].append(item)

def invalidate_downstream(state, stage):
    if stage not in STAGE_ORDER:
        return
    idx=STAGE_ORDER.index(stage)
    for s in STAGE_ORDER[idx:]:
        if s in state["stages"]:
            state["stages"][s]["status"]="INVALIDATED"
            state["stages"][s]["invalidated_at"]=now()
    state["current_state"]=f"{stage}_RESET"
    state["updated_at"]=now()
