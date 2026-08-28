from app.services.repair_ai import RepairAI

def test_power_diagnosis():
    r=RepairAI().diagnose("برد روشن نمی شود")
    assert r.confidence > .7
    assert len(r.steps) >= 4

def test_default_diagnosis():
    r=RepairAI().diagnose("تصویر نامشخص")
    assert r.risk == "medium"
