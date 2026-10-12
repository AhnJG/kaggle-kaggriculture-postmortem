import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mirror_edge_exp022", ROOT / "tools/mirror_edge_exp022.py")
EXP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXP)


def test_candidate_is_exactly_import_only():
    manifest = EXP.prepare_variant()
    assert manifest["import_only_assertion"] is True
    old = EXP.OLD_VARIANT.read_text()
    new = EXP.VARIANT.read_text()
    assert new.replace(EXP.MARKER + EXP.IMPORT_LINE, EXP.MARKER, 1) == old


def test_step0_mutation_is_exactly_one_unit_and_persisted():
    result = EXP.unit_test()
    assert result["status"] == "PASS"
    assert len(result["rows"]) == 2
    assert all(row["difference"]["quantity_delta"] == -1 for row in result["rows"])
    persisted = json.loads((EXP.OUT / "unit-step0-action.json").read_text())
    assert persisted == result


def test_frozen_seed_ranges_and_workers():
    frozen = EXP.verify_frozen_inputs()
    assert frozen["workers"] == 5
    assert frozen["screen"]["candidate_and_parent_seeds"] == [6200, 6249]
    assert frozen["confirmation"]["primary_o"]["seeds"] == [6250, 6449]
    assert frozen["confirmation"]["dp_noninferiority"]["seeds"] == [6450, 6549]
    assert frozen["confirmation"]["public_guard"]["seeds"] == [6550, 6559]
    assert frozen["final_confirmation"]["seeds"] == [6600, 6799]
