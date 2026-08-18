"""Tests for GE DICOM header repair and representative-header selection."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

import pydicom
import pydicom.config as pydicom_config
import pytest
from pydicom.dataelem import DataElement
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.tag import Tag
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from pyaslreport import get_bids_metadata
from pyaslreport.enums import ModalityTypeValues
from pyaslreport.modalities.asl.processor import ASLProcessor
from pyaslreport.utils import dicom_tags_utils as dcm_tags
from pyaslreport.utils.dicom_repair_utils import GE_ASL_REPAIR_TAGS


def _binary_double(value: float) -> str:
    """Encode a float as the anonymization-damaged value used in fixtures.

    Args:
        value: Numeric value to encode as a little-endian double.

    Returns:
        Latin-1 string preserving the raw double bytes.
    """
    return struct.pack("<d", value).decode("latin-1")


def _write_dicom(path: Path, tags: dict[Any, tuple[str, Any]]) -> Path:
    """Write a minimal DICOM file for metadata extraction tests.

    Args:
        path: Destination file path.
        tags: Mapping of DICOM tags to ``(VR, value)`` pairs.

    Returns:
        The path that was written.
    """
    ds = Dataset()
    ds.SpecificCharacterSet = "ISO_IR 100"

    old_reading_mode = pydicom_config.settings.reading_validation_mode
    old_writing_mode = pydicom_config.settings.writing_validation_mode
    pydicom_config.settings.reading_validation_mode = pydicom_config.IGNORE
    pydicom_config.settings.writing_validation_mode = pydicom_config.IGNORE
    try:
        for tag, (vr, value) in tags.items():
            if (
                vr in {"DS", "IS"}
                and isinstance(value, str)
                and any(ord(char) < 32 or ord(char) > 126 for char in value)
            ):
                ds.add(DataElement(tag, vr, value, already_converted=True))
            else:
                ds.add_new(tag, vr, value)
    finally:
        pydicom_config.settings.reading_validation_mode = old_reading_mode
        pydicom_config.settings.writing_validation_mode = old_writing_mode

    fm = FileMetaDataset()
    fm.MediaStorageSOPClassUID = generate_uid()
    fm.MediaStorageSOPInstanceUID = generate_uid()
    fm.TransferSyntaxUID = ExplicitVRLittleEndian
    ds.file_meta = fm

    old_writing_mode = pydicom_config.settings.writing_validation_mode
    pydicom_config.settings.writing_validation_mode = pydicom_config.IGNORE
    try:
        pydicom.dcmwrite(str(path), ds, enforce_file_format=True)
    finally:
        pydicom_config.settings.writing_validation_mode = old_writing_mode
    return path


def _base_ge_tags(
    sequence_name: str | None = "3dpcasl",
) -> dict[Any, tuple[str, Any]]:
    """Return common GE tags shared by synthetic ASL DICOM fixtures.

    Args:
        sequence_name: Optional value for the GE internal sequence-name tag.

    Returns:
        Mapping of DICOM tags to ``(VR, value)`` pairs.
    """
    tags = {
        dcm_tags.MANUFACTURER: ("LO", "GE MEDICAL SYSTEMS"),
        dcm_tags.MR_ACQUISITION_TYPE: ("CS", "3D"),
        dcm_tags.MAGNETIC_FIELD_STRENGTH: ("DS", "3"),
        dcm_tags.ECHO_TIME: ("DS", "10.5"),
    }
    if sequence_name is not None:
        tags[dcm_tags.GE_INTERNAL_SEQUENCE_NAME] = ("LO", sequence_name)
    return tags


def test_ge_asl_missing_internal_sequence_name_falls_back_to_single_pld(
    tmp_path: Path,
) -> None:
    """A missing GE internal sequence name (0019,109E) is treated as single-PLD.

    Per GE guidance, absence of the tag (or any value other than 'easl') can be
    safely handled as a basic GE single-PLD sequence instead of raising.
    """
    tags = _base_ge_tags(sequence_name=None)
    tags[dcm_tags.GE_LABEL_DURATION] = ("IS", "1450")
    tags[dcm_tags.GE_INVERSION_TIME] = ("DS", "2025")
    _write_dicom(tmp_path / "0001.dcm", tags)

    metadata, asl_context = get_bids_metadata(
        {"modality": ModalityTypeValues.ASL, "dicom_dir": str(tmp_path)}
    )

    # Single-PLD extractor path: GE milliseconds are normalized to BIDS seconds
    # (1450 ms -> 1.45 s, 2025 ms -> 2.025 s); single deltaM + m0scan context.
    assert metadata["LabelingDuration"] == pytest.approx(1.45)
    assert float(metadata["PostLabelingDelay"]) == pytest.approx(2.025)
    assert asl_context == ["deltaM", "m0scan"]


def test_single_pld_repairs_binary_label_duration_and_selects_pld_header(
    tmp_path: Path,
) -> None:
    """The chosen single-PLD header should include InversionTime when available."""
    tags_without_pld = _base_ge_tags("3dpcasl")
    tags_without_pld.update(
        {
            dcm_tags.INSTANCE_NUMBER: ("IS", "1"),
            dcm_tags.GE_LABEL_DURATION: ("IS", _binary_double(1450.0)),
        }
    )
    _write_dicom(tmp_path / "0001.dcm", tags_without_pld)

    tags_with_pld = _base_ge_tags("3dpcasl")
    tags_with_pld.update(
        {
            dcm_tags.INSTANCE_NUMBER: ("IS", "2"),
            dcm_tags.GE_LABEL_DURATION: ("IS", _binary_double(1450.0)),
            dcm_tags.GE_INVERSION_TIME: ("DS", "2025"),
        }
    )
    _write_dicom(tmp_path / "0002.dcm", tags_with_pld)

    metadata, asl_context = get_bids_metadata(
        {"modality": ModalityTypeValues.ASL, "dicom_dir": str(tmp_path)}
    )

    # Extractor emits BIDS seconds: 1450 ms -> 1.45 s, 2025 ms -> 2.025 s.
    assert metadata["LabelingDuration"] == pytest.approx(1.45)
    assert float(metadata["PostLabelingDelay"]) == pytest.approx(2.025)
    assert asl_context == ["deltaM", "m0scan"]


def test_easl_repairs_binary_cv_tags_and_generates_multi_pld(tmp_path: Path) -> None:
    """Damaged eASL CV tags should be repaired before PLD arrays are computed."""
    tags = _base_ge_tags("easl")
    tags.update(
        {
            dcm_tags.GE_PRIVATE_CV4: ("DS", _binary_double(1000.0)),
            dcm_tags.GE_PRIVATE_CV5: ("DS", _binary_double(3500.0)),
            dcm_tags.GE_PRIVATE_CV6: ("DS", _binary_double(3.0)),
            dcm_tags.GE_PRIVATE_CV7: ("DS", _binary_double(0.2)),
        }
    )
    _write_dicom(tmp_path / "0001.dcm", tags)

    metadata, asl_context = get_bids_metadata(
        {"modality": ModalityTypeValues.ASL, "dicom_dir": str(tmp_path)}
    )

    # CV4/CV5 are normalized ms -> s before the eASL timing math, so the
    # emitted arrays are in BIDS seconds (previously x1000 too large).
    assert metadata["LabelingDuration"] == pytest.approx(
        [1.1666667, 1.1666667, 1.1666667]
    )
    assert metadata["PostLabelingDelay"] == pytest.approx([1.0, 2.1666667, 3.3333333])
    assert asl_context == ["deltaM", "deltaM", "m0scan"]


def test_ge_asl_repair_allowlist_covers_extractor_numeric_tags() -> None:
    """Numeric GE ASL tags read by the extractors must be repair-aware."""
    extractor_tags = {
        Tag(0x0018, 0x0081),
        Tag(0x0018, 0x0082),
        Tag(0x0018, 0x0087),
        Tag(0x0018, 0x1314),
        Tag(0x0043, 0x10A5),
        Tag(0x0019, 0x10AB),
        Tag(0x0019, 0x10AC),
        Tag(0x0019, 0x10AD),
        Tag(0x0019, 0x10AE),
        Tag(0x0043, 0x1083),
        Tag(0x0043, 0x192C),
        Tag(0x0027, 0x1062),
    }

    assert extractor_tags <= GE_ASL_REPAIR_TAGS


def test_acquisition_voxel_size_from_dicom_geometry(tmp_path: Path) -> None:
    """PixelSpacing + SliceThickness populate AcquisitionVoxelSize in mm."""
    tags = _base_ge_tags("3dpcasl")
    tags[dcm_tags.PIXEL_SPACING] = ("DS", [3.4, 3.4])
    tags[dcm_tags.SLICE_THICKNESS] = ("DS", "4.0")
    tags[dcm_tags.GE_LABEL_DURATION] = ("IS", "1450")
    tags[dcm_tags.GE_INVERSION_TIME] = ("DS", "2025")
    _write_dicom(tmp_path / "0001.dcm", tags)

    metadata, _ = get_bids_metadata(
        {"modality": ModalityTypeValues.ASL, "dicom_dir": str(tmp_path)}
    )

    assert metadata["AcquisitionVoxelSize"] == pytest.approx([3.4, 3.4, 4.0])


def test_ge_single_pld_timing_survives_processor_conversion_once(
    tmp_path: Path,
) -> None:
    """GE timing round-trips to report milliseconds exactly once.

    The GE extractor normalizes LabelingDuration/PostLabelingDelay to BIDS
    seconds, and the ASL processor multiplies the time fields back to
    milliseconds for the report. Chaining both must reproduce the original
    GE millisecond values (1450 / 2025) rather than inflating them by 1000,
    proving the conversion is applied a single time end to end.
    """
    tags = _base_ge_tags(sequence_name=None)
    tags[dcm_tags.GE_LABEL_DURATION] = ("IS", "1450")
    tags[dcm_tags.GE_INVERSION_TIME] = ("DS", "2025")
    _write_dicom(tmp_path / "0001.dcm", tags)

    metadata, _ = get_bids_metadata(
        {"modality": ModalityTypeValues.ASL, "dicom_dir": str(tmp_path)}
    )

    # Extractor output is in BIDS seconds.
    assert metadata["LabelingDuration"] == pytest.approx(1.45)
    assert float(metadata["PostLabelingDelay"]) == pytest.approx(2.025)

    processor = ASLProcessor.__new__(ASLProcessor)
    session = dict(metadata)
    processor._convert_units_to_milliseconds(session)

    # Processor converts BIDS seconds back to milliseconds exactly once.
    assert session["LabelingDuration"] == pytest.approx(1450)
    assert session["PostLabelingDelay"] == pytest.approx(2025)
