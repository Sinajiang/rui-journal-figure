from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/"tests"/"fixtures"
sys.path.insert(0,str(ROOT/"scripts"))

from extract_figure_mentions import extract
from audit_evidence_graph import audit as audit_graph
from audit_figure_citations import audit as audit_citations
from audit_legend_architecture import audit as audit_legend
from audit_supplementary_numbering import audit as audit_supp

def test_mention_extractor_handles_panel_ranges():
    r=extract(FIX/"synthetic_manuscript.txt")
    hit=[x for x in r["figures"] if x["figure"]=="2"][0]
    assert hit["panels"] == ["A","B"]

def test_good_evidence_graph_passes():
    r=audit_graph(FIX/"synthetic_evidence_graph.yaml")
    assert r["pass"] is True

def test_bad_graph_missing_source_fails():
    r=audit_graph(FIX/"synthetic_bad_graph.yaml")
    assert r["pass"] is False
    assert any(x["type"]=="missing_source" for x in r["blocking"])

def test_good_citations_pass():
    r=audit_citations(FIX/"synthetic_manuscript.txt",FIX/"synthetic_evidence_graph.yaml")
    assert r["pass"] is True

def test_wrong_panel_citation_fails():
    r=audit_citations(FIX/"synthetic_bad_manuscript.txt",FIX/"synthetic_evidence_graph.yaml")
    assert r["pass"] is False
    assert any(x["type"]=="citation_missing_panel" for x in r["blocking"])

def test_legend_architecture_passes():
    r=audit_legend(FIX/"synthetic_evidence_graph.yaml",FIX/"synthetic_legend_architecture.yaml")
    assert r["pass"] is True

def test_supplementary_sequence_passes():
    r=audit_supp(FIX/"synthetic_manuscript.txt")
    assert r["pass"] is True
