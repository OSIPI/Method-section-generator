# Bug 3 PR: Prevent Silent Field Overwrite in `_rename_fields`

## PR Title
fix: Prevent silent field overwrite when mapping conflicting fields to PostLabelingDelay

## PR Description
In `ASLProcessor._rename_fields`, `field_mappings` maps both `InversionTime` and `InitialPostLabelDelay` to `PostLabelingDelay`. If a parsed session dict contains both fields with different values, the loop previously overwrote the first parsed mapping with the second mapping silently, resulting in data loss. This could silently change physical scan properties like PLD.

### Fix
Added a conflict detection check to the field mapping loop:
- If the target key already exists and the new source value is different, it logs a warning and retains the existing key/value rather than overwriting it.

### File Changed
`package/src/pyaslreport/modalities/asl/processor.py`

```diff
         for old_key, new_key in field_mappings.items():
             if old_key in session:
-                session[new_key] = session[old_key]
+                if new_key in session and session[new_key] != session[old_key]:
+                    import logging
+                    logging.warning(
+                        f"Field conflict: '{old_key}' ({session[old_key]}) maps to '{new_key}' "
+                        f"which already has value {session[new_key]}. Retaining existing '{new_key}'."
+                    )
+                else:
+                    session[new_key] = session[old_key]
                 del session[old_key]
```

---

## API/Processor JSON Responses Comparison

When sending the following payload to the FastAPI `/api/report/process/bids` endpoint:
```json
{
  "InversionTime": 1.5,
  "InitialPostLabelDelay": 2000.0,
  "RepetitionTime": 4000.0,
  "MagneticFieldStrength": 3.0,
  "MRAcquisitionType": "3D",
  "Manufacturer": "Generic"
}
```

### `main` branch (before fix)
The API normalizes the parameters silently losing the 1.5 value:
```json
{
  "MagneticFieldStrength": 3.0,
  "MRAcquisitionType": "3D",
  "Manufacturer": "Generic",
  "RepetitionTimePreparation": 4000.0,
  "PostLabelingDelay": 2000.0
}
```
*Result: The `InversionTime` of 1.5 is silently overwritten and lost.*

### `issue10` branch (after fix)
The API correctly spots the conflict and retains the first value (1.5), logging a warning:
```json
{
  "MagneticFieldStrength": 3.0,
  "MRAcquisitionType": "3D",
  "Manufacturer": "Generic",
  "RepetitionTimePreparation": 4000.0,
  "PostLabelingDelay": 1.5
}
```
*Server logs WARNING:*
```
WARNING:root:Field conflict: 'InitialPostLabelDelay' (2000.0) maps to 'PostLabelingDelay' which already has value 1.5. Retaining existing 'PostLabelingDelay'.
```

---

## Python API Suite Results

### `main` branch (before fix)

| # | Test | Status | Detail |
|---|------|--------|--------|
| 1 | InversionTime only -> PostLabelingDelay | PASS | |
| 2 | InitialPostLabelDelay only -> PostLabelingDelay | PASS | |
| 3 | Both fields with diff values -> silent overwrite | FAIL | PLD=2000.0 (1.5 silently lost) |
| 4 | Both fields with same value -> no data loss | PASS | |

**Summary: PASSED=3 FAILED=1**

### `issue10` branch (after fix)

| # | Test | Status | Detail |
|---|------|--------|--------|
| 1 | InversionTime only -> PostLabelingDelay | PASS | |
| 2 | InitialPostLabelDelay only -> PostLabelingDelay | PASS | |
| 3 | Both fields with diff values -> silent overwrite | PASS | Retains 1.5, logs warning |
| 4 | Both fields with same value -> no data loss | PASS | |

**Summary: PASSED=4 FAILED=0**

---

## Sanity Checks

| Check | Result |
|-------|--------|
| Pytest suite passed | Yes |
