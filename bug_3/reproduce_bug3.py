"""Bug 3 reproduction: Silent field overwrite in _rename_fields"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'package', 'src'))

from pyaslreport.modalities.asl.processor import ASLProcessor

results = []

# We need a minimal ASLProcessor instance - it requires config but we only test _rename_fields
# So we call _rename_fields directly on a dummy instance
proc = object.__new__(ASLProcessor)  # skip __init__

# T1: Only InversionTime present -> should rename to PostLabelingDelay
s1 = {"InversionTime": 1.5}
proc._rename_fields(s1)
ok1 = s1.get("PostLabelingDelay") == 1.5 and "InversionTime" not in s1
results.append({"test": "InversionTime only -> PostLabelingDelay", "pass": ok1, "detail": "" if ok1 else f"got {s1}"})

# T2: Only InitialPostLabelDelay present -> should rename to PostLabelingDelay
s2 = {"InitialPostLabelDelay": 2.0}
proc._rename_fields(s2)
ok2 = s2.get("PostLabelingDelay") == 2.0 and "InitialPostLabelDelay" not in s2
results.append({"test": "InitialPostLabelDelay only -> PostLabelingDelay", "pass": ok2, "detail": "" if ok2 else f"got {s2}"})

# T3: BOTH present with DIFFERENT values -> silent overwrite BUG
s3 = {"InversionTime": 1.5, "InitialPostLabelDelay": 2.0}
proc._rename_fields(s3)
# After processing: InversionTime sets PLD=1.5, then InitialPostLabelDelay overwrites PLD=2.0
# The value 1.5 is silently lost with no warning
overwritten = s3.get("PostLabelingDelay") == 2.0  # second value wins silently
no_warning = True  # no logging/warning mechanism exists
bug_present = overwritten and no_warning
results.append({"test": "Both fields with diff values -> silent overwrite", "pass": not bug_present,
                "detail": f"PLD={s3.get('PostLabelingDelay')} (1.5 silently lost)" if bug_present else ""})

# T4: BOTH present with SAME value -> no data loss but still no warning
s4 = {"InversionTime": 1.5, "InitialPostLabelDelay": 1.5}
proc._rename_fields(s4)
ok4 = s4.get("PostLabelingDelay") == 1.5
results.append({"test": "Both fields with same value -> no data loss", "pass": ok4, "detail": "" if ok4 else f"got {s4}"})

passed = sum(1 for r in results if r["pass"])
failed = sum(1 for r in results if not r["pass"])
print(f"PASSED={passed} FAILED={failed}")
for r in results:
    status = "PASS" if r["pass"] else "FAIL"
    detail = f" -- {r['detail']}" if r["detail"] else ""
    print(f"  [{status}] {r['test']}{detail}")

with open(os.path.join(os.path.dirname(__file__), 'results.json'), 'w') as f:
    json.dump({"passed": passed, "failed": failed, "results": results}, f, indent=2)
