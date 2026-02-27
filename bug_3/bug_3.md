# Bug 3: Silent Field Overwrite in `_rename_fields`

## Issue Title
Silent field overwrite in `_rename_fields` — conflicting PostLabelingDelay sources silently lost

## Location
`package/src/pyaslreport/modalities/asl/processor.py:236-246`

## Description
`field_mappings` maps both `InversionTime` and `InitialPostLabelDelay` to `PostLabelingDelay`. If a session contains both fields with different values, the loop silently overwrites the first mapping with the second, losing the original value with no warning. In medical imaging, silently changing physical scan properties like PLD compromises data integrity.

## Reproduction (on `main` branch)

### Script
```python
from pyaslreport.modalities.asl.processor import ASLProcessor

proc = object.__new__(ASLProcessor)

# Both fields present with different values
session = {
    "InversionTime": 1.5,
    "InitialPostLabelDelay": 2000.0,
    "RepetitionTime": 4000.0,
    "MagneticFieldStrength": 3.0,
    "MRAcquisitionType": "3D",
    "Manufacturer": "Generic"
}
proc._rename_fields(session)
# Result: PostLabelingDelay = 2000.0, InversionTime value 1.5 safely LOST
```

### Processor / API Normalized Response

When the frontend sends the above JSON payload to the FastAPI `/api/report/process/bids` endpoint, the `ASLProcessor` normalizes it before generating the BIDS metadata. Due to the bug, the API produces this state where `1.5` is entirely lost:

```json
{
  "MagneticFieldStrength": 3.0,
  "MRAcquisitionType": "3D",
  "Manufacturer": "Generic",
  "RepetitionTimePreparation": 4000.0,
  "PostLabelingDelay": 2000.0
}
```

### Automated Results on `main` branch

| # | Test | Status | Detail |
|---|------|--------|--------|
| 1 | InversionTime only -> PostLabelingDelay | PASS | |
| 2 | InitialPostLabelDelay only -> PostLabelingDelay | PASS | |
| 3 | Both fields with diff values -> silent overwrite | FAIL | PLD=2000.0 (1.5 silently lost) |
| 4 | Both fields with same value -> no data loss | PASS | |

**Summary: PASSED=3 FAILED=1**
