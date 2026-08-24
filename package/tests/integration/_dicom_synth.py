"""Synthetic DICOM writers for the DICOM integration harness tests.

Lets the harness build minimal in-memory ASL DICOMs with no committed fixtures,
so the DICOM machinery is exercised on every push. Adapted from
``tests/test_ge_dicom_metadata.py``.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

import pydicom
import pydicom.config as pydicom_config
from pydicom.dataelem import DataElement
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from pyaslreport.utils import dicom_tags_utils as dcm_tags


def _binary_double(value: float) -> str:
    """Encode a float as the anonymization-damaged raw-double string."""
    return struct.pack("<d", value).decode("latin-1")


def write_dicom(path: Path, tags: dict[Any, tuple[str, Any]]) -> Path:
    """Write a minimal DICOM file from a ``{tag: (VR, value)}`` mapping."""
    dataset = Dataset()
    dataset.SpecificCharacterSet = "ISO_IR 100"

    old_read = pydicom_config.settings.reading_validation_mode
    old_write = pydicom_config.settings.writing_validation_mode
    pydicom_config.settings.reading_validation_mode = pydicom_config.IGNORE
    pydicom_config.settings.writing_validation_mode = pydicom_config.IGNORE
    try:
        for tag, (vr, value) in tags.items():
            if (
                vr in {"DS", "IS"}
                and isinstance(value, str)
                and any(ord(char) < 32 or ord(char) > 126 for char in value)
            ):
                dataset.add(DataElement(tag, vr, value, already_converted=True))
            else:
                dataset.add_new(tag, vr, value)
    finally:
        pydicom_config.settings.reading_validation_mode = old_read
        pydicom_config.settings.writing_validation_mode = old_write

    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = generate_uid()
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    dataset.file_meta = file_meta

    old_write = pydicom_config.settings.writing_validation_mode
    pydicom_config.settings.writing_validation_mode = pydicom_config.IGNORE
    try:
        pydicom.dcmwrite(str(path), dataset, enforce_file_format=True)
    finally:
        pydicom_config.settings.writing_validation_mode = old_write
    return path


def write_ge_asl_dicom(
    path: Path,
    *,
    sequence_name: str = "3dpcasl",
    label_duration: str = "1450",
    inversion_time: str = "2025",
) -> Path:
    """Write a minimal GE single-PLD ASL DICOM (yields a (metadata, context) pair)."""
    tags = {
        dcm_tags.MANUFACTURER: ("LO", "GE MEDICAL SYSTEMS"),
        dcm_tags.MR_ACQUISITION_TYPE: ("CS", "3D"),
        dcm_tags.MAGNETIC_FIELD_STRENGTH: ("DS", "3"),
        dcm_tags.ECHO_TIME: ("DS", "10.5"),
        dcm_tags.FLIP_ANGLE: ("DS", "111"),
        dcm_tags.GE_INTERNAL_SEQUENCE_NAME: ("LO", sequence_name),
        dcm_tags.GE_LABEL_DURATION: ("IS", label_duration),
        dcm_tags.GE_INVERSION_TIME: ("DS", inversion_time),
    }
    return write_dicom(path, tags)


def write_siemens_asl_dicom(path: Path) -> Path:
    """Write a minimal Siemens PASL DICOM (yields a bare dict today)."""
    tags = {
        dcm_tags.MANUFACTURER: ("LO", "SIEMENS"),
        dcm_tags.MR_ACQUISITION_TYPE: ("CS", "2D"),
        dcm_tags.MAGNETIC_FIELD_STRENGTH: ("DS", "3"),
        dcm_tags.ECHO_TIME: ("DS", "12"),
        dcm_tags.FLIP_ANGLE: ("DS", "90"),
    }
    return write_dicom(path, tags)
