"""Utilities for repairing anonymization-damaged DICOM metadata in memory.

Some anonymizers preserve a DICOM element's numeric-string VR (DS/IS) but write
raw binary floating-point bytes into the value. The helpers here only repair a
small allowlist of GE ASL tags used by the extractor, and only mutate the
already-loaded pydicom Dataset. The source DICOM files are never written.
"""

from __future__ import annotations

import logging
import math
import struct
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import pydicom
from pydicom.dataset import Dataset

from pyaslreport.utils import dicom_tags_utils as dcm_tags

LOGGER = logging.getLogger(__name__)

NUMERIC_STRING_VRS = frozenset({"DS", "IS"})

# Conservative bounds for MR metadata values such as times, counts, factors,
# angles, and field strength. Values outside this range are likely mis-decodes.
_MAX_PLAUSIBLE = 1e7
_MIN_PLAUSIBLE = 1e-6

GE_ASL_REPAIR_TAGS = frozenset(
    {
        dcm_tags.ECHO_TIME,
        dcm_tags.GE_INVERSION_TIME,
        dcm_tags.MAGNETIC_FIELD_STRENGTH,
        dcm_tags.FLIP_ANGLE,
        dcm_tags.GE_LABEL_DURATION,
        dcm_tags.GE_PRIVATE_CV4,
        dcm_tags.GE_PRIVATE_CV5,
        dcm_tags.GE_PRIVATE_CV6,
        dcm_tags.GE_PRIVATE_CV7,
        dcm_tags.GE_ASSET_R_FACTOR,
        dcm_tags.GE_EFFECTIVE_ECHO_SPACING,
        dcm_tags.GE_NUMBER_OF_EXCITATIONS,
    }
)

GE_ASL_ESSENTIAL_REPAIR_TAGS = frozenset(
    {
        dcm_tags.GE_INVERSION_TIME,
        dcm_tags.GE_LABEL_DURATION,
        dcm_tags.GE_PRIVATE_CV4,
        dcm_tags.GE_PRIVATE_CV5,
        dcm_tags.GE_PRIVATE_CV6,
        dcm_tags.GE_PRIVATE_CV7,
    }
)


@dataclass(frozen=True)
class DicomTagRepair:
    """One in-memory DICOM element repair."""

    tag: Any
    vr: str
    decoded: list[float]


@dataclass
class DicomRepairReport:
    """Summary of repairs applied to a Dataset."""

    repaired: list[DicomTagRepair] = field(default_factory=list)
    skipped_auxiliary: list[Any] = field(default_factory=list)


class DicomAnonymizationRepairError(ValueError):
    """Raised when an essential GE ASL tag is damaged but cannot be decoded."""


def _plausible(values: Iterable[float]) -> bool:
    """Return whether decoded numeric values are plausible MR metadata values.

    Args:
        values: Numeric values decoded from a damaged DICOM element.

    Returns:
        True when every value is finite and inside conservative bounds.
    """
    for value in values:
        if not math.isfinite(value):
            return False
        if value != 0.0 and not (_MIN_PLAUSIBLE <= abs(value) <= _MAX_PLAUSIBLE):
            return False
    return True


def _raw_bytes(value: Any) -> bytes | None:
    """Return raw bytes from pydicom values that may contain binary payloads.

    Args:
        value: DICOM element value to inspect.

    Returns:
        Raw bytes when the value can be interpreted losslessly, otherwise None.
    """
    if isinstance(value, bytes):
        return value
    if type(value) is str:
        try:
            return value.encode("latin-1")
        except UnicodeEncodeError:
            return None
    return None


def _is_text_number(value: str) -> bool:
    """Return whether a string is already a valid numeric text value.

    Args:
        value: DICOM DS/IS string value.

    Returns:
        True when all separated components parse as floats.
    """
    parts = [part.strip() for part in value.replace("\\", " ").split() if part.strip()]
    if not parts:
        return False
    try:
        for part in parts:
            float(part)
    except ValueError:
        return False
    return True


def _looks_binary_damaged(value: Any) -> bool:
    """Return whether a DICOM value looks like binary data in a text VR.

    Args:
        value: DICOM element value to inspect.

    Returns:
        True when the value should be considered for binary numeric repair.
    """
    if not isinstance(value, (bytes, str)) or value == "":
        return False
    if type(value) is str:
        if _is_text_number(value):
            return False
        if all(32 <= ord(char) <= 126 for char in value):
            return False
    return True


def decode_binary_numeric(value: Any) -> list[float] | None:
    """Decode binary bytes accidentally stored in a DS/IS value.

    Args:
        value: DICOM value that may contain little-endian float/double bytes.

    Returns:
        Decoded finite numeric values, or None when decoding is unsafe.
    """

    raw = _raw_bytes(value)
    if not raw:
        return None

    for width, fmt in ((8, "d"), (4, "f")):
        if len(raw) % width != 0:
            continue
        try:
            decoded = list(struct.unpack(f"<{len(raw) // width}{fmt}", raw))
        except struct.error:
            continue
        if _plausible(decoded):
            return decoded
    return None


def repair_dicom_dataset_in_memory(ds: Dataset) -> DicomRepairReport:
    """Repair allowlisted GE ASL numeric tags in a loaded Dataset.

    The Dataset is mutated in memory only. No DICOM file is written.

    Args:
        ds: Loaded DICOM dataset to inspect and repair.

    Returns:
        Summary of applied repairs and skipped auxiliary tags.

    Raises:
        DicomAnonymizationRepairError: If an essential damaged GE ASL tag cannot
            be decoded safely.
    """

    report = DicomRepairReport()
    for elem in ds:
        if elem.VR == "SQ":
            for item in elem.value:
                nested = repair_dicom_dataset_in_memory(item)
                report.repaired.extend(nested.repaired)
                report.skipped_auxiliary.extend(nested.skipped_auxiliary)
            continue

        if elem.tag not in GE_ASL_REPAIR_TAGS or elem.VR not in NUMERIC_STRING_VRS:
            continue

        value = elem.value
        if not _looks_binary_damaged(value):
            continue

        decoded = decode_binary_numeric(value)
        if decoded is None:
            if elem.tag in GE_ASL_ESSENTIAL_REPAIR_TAGS:
                raise DicomAnonymizationRepairError(
                    "Cannot repair anonymization-damaged essential GE ASL tag "
                    f"{elem.tag}: value is not safely decodable."
                )
            report.skipped_auxiliary.append(elem.tag)
            LOGGER.warning(
                "Skipping anonymization-damaged auxiliary GE ASL tag %s; "
                "value is not safely decodable.",
                elem.tag,
            )
            continue

        if elem.VR == "IS":
            new_value: Any = [int(round(item)) for item in decoded]
        else:
            new_value = decoded

        elem.value = new_value[0] if len(new_value) == 1 else new_value
        report.repaired.append(DicomTagRepair(elem.tag, elem.VR, decoded))
        LOGGER.info(
            "Repaired anonymization-damaged GE ASL tag %s in memory: %s",
            elem.tag,
            decoded[0] if len(decoded) == 1 else decoded,
        )

    return report


def dicom_value_to_python(value: Any) -> Any:
    """Convert common pydicom value containers to JSON-friendly Python values.

    Args:
        value: Value returned by pydicom.

    Returns:
        A scalar or list made from built-in Python value types where possible.
    """

    if isinstance(value, (list, tuple, pydicom.multival.MultiValue)):
        return [dicom_value_to_python(item) for item in value]
    if isinstance(value, pydicom.valuerep.IS):
        return int(value)
    if isinstance(value, pydicom.valuerep.DSfloat):
        return float(value)
    return value
