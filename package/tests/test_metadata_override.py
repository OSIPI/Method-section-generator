"""Tests for the sidecar-JSON metadata override utility (C12)."""

from __future__ import annotations

import os
from pathlib import Path

from pyaslreport.utils.metadata_override_utils import (
    apply_overrides,
    apply_sidecar_overrides,
    discover_sidecars,
    load_sidecar,
)


def _make_session(tmp_path: Path, sidecar_json: str | None) -> Path:
    """Build a session/ASL layout and return the DICOM (ASL) directory.

    Args:
        tmp_path: Pytest-provided per-test temporary directory.
        sidecar_json: Raw JSON text to write as ``session/studyPar.json``, or
            ``None`` to create no sidecar.

    Returns:
        Path to the ``ASL`` subfolder, mirroring the real layout where the
        sidecar sits in the session folder one level above the DICOMs.
    """
    session = tmp_path / "GE_PCASL_DV25.0"
    asl_dir = session / "ASL"
    asl_dir.mkdir(parents=True)
    if sidecar_json is not None:
        (session / "studyPar.json").write_text(sidecar_json, encoding="utf-8")
    return asl_dir


class TestDiscoverSidecars:
    """Discovery of sidecar JSON files next to a DICOM directory."""

    def test_finds_sidecar_in_session_folder(self, tmp_path: Path) -> None:
        """A studyPar.json one level above the DICOMs is discovered."""
        asl_dir = _make_session(tmp_path, "{}")

        found = discover_sidecars(str(asl_dir))

        assert len(found) == 1
        assert os.path.basename(found[0]) == "studyPar.json"

    def test_returns_empty_when_no_json(self, tmp_path: Path) -> None:
        """No JSON anywhere yields an empty list."""
        asl_dir = _make_session(tmp_path, None)

        assert discover_sidecars(str(asl_dir)) == []

    def test_empty_dicom_dir_returns_empty(self) -> None:
        """A falsy dicom_dir disables discovery."""
        assert discover_sidecars("") == []
        assert discover_sidecars(None) == []

    def test_excludes_output_named_json(self, tmp_path: Path) -> None:
        """A report/golden JSON (name contains 'output') is not a sidecar."""
        asl_dir = _make_session(tmp_path, "{}")  # writes studyPar.json in session
        (asl_dir.parent / "expected_output.json").write_text("{}", encoding="utf-8")

        found = [os.path.basename(f) for f in discover_sidecars(str(asl_dir))]

        assert "studyPar.json" in found
        assert "expected_output.json" not in found


class TestLoadSidecar:
    """Loading and shape-checking of sidecar files."""

    def test_loads_json_object(self, tmp_path: Path) -> None:
        """A JSON object is returned as a dict."""
        path = tmp_path / "s.json"
        path.write_text('{"BackgroundSuppression": true}', encoding="utf-8")

        assert load_sidecar(str(path)) == {"BackgroundSuppression": True}

    def test_non_object_returns_empty_dict(self, tmp_path: Path) -> None:
        """A top-level JSON array is ignored and yields an empty dict."""
        path = tmp_path / "s.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")

        assert load_sidecar(str(path)) == {}


class TestApplyOverrides:
    """In-memory overlay semantics: JSON wins, conflicts recorded."""

    def test_adds_absent_field(self) -> None:
        """A DICOM-absent field (pulse times) is added to the metadata."""
        metadata = {"BackgroundSuppression": True}

        _, report = apply_overrides(
            metadata,
            {"BackgroundSuppressionPulseTime": [1.465, 2.1, 2.6, 2.88]},
        )

        assert metadata["BackgroundSuppressionPulseTime"] == [1.465, 2.1, 2.6, 2.88]
        assert report.applied == ["BackgroundSuppressionPulseTime"]
        assert report.conflicts == []

    def test_json_wins_and_conflict_recorded(self) -> None:
        """A differing present value is overridden and recorded as a conflict."""
        metadata = {"BackgroundSuppressionNumberPulses": 4}

        _, report = apply_overrides(metadata, {"BackgroundSuppressionNumberPulses": 2})

        assert metadata["BackgroundSuppressionNumberPulses"] == 2
        assert report.conflicts == [("BackgroundSuppressionNumberPulses", 4, 2)]
        assert report.applied == []

    def test_matching_value_is_not_a_conflict(self) -> None:
        """Overriding with an identical value records neither applied nor conflict."""
        metadata = {"BackgroundSuppression": True}

        _, report = apply_overrides(metadata, {"BackgroundSuppression": True})

        assert report.conflicts == []
        assert report.applied == []

    def test_alias_maps_labeling_type(self) -> None:
        """LabelingType is remapped onto the internal ArterialSpinLabelingType."""
        metadata: dict[str, object] = {}

        _, report = apply_overrides(metadata, {"LabelingType": "PCASL"})

        assert metadata == {"ArterialSpinLabelingType": "PCASL"}
        assert report.aliased == [("LabelingType", "ArterialSpinLabelingType")]
        assert report.applied == ["ArterialSpinLabelingType"]

    def test_allowlist_skips_unlisted_keys(self) -> None:
        """With an allowlist, only listed post-alias keys are overlaid."""
        metadata: dict[str, object] = {}

        _, report = apply_overrides(
            metadata,
            {"SliceTiming": 0.0374, "BackgroundSuppression": True},
            allowlist={"BackgroundSuppression"},
        )

        assert metadata == {"BackgroundSuppression": True}
        assert report.skipped == ["SliceTiming"]

    def test_accept_all_passes_unknown_keys(self) -> None:
        """With no allowlist, DICOM-unknown keys pass through unchanged."""
        metadata: dict[str, object] = {}

        apply_overrides(metadata, {"SliceTiming": 0.0374, "NumberSegments": 4})

        assert metadata == {"SliceTiming": 0.0374, "NumberSegments": 4}

    def test_overlays_first_dict_of_list_result(self) -> None:
        """For a [dict, asl_context] result, only the dict is overlaid."""
        metadata = [{"BackgroundSuppression": True}, ["deltaM", "m0scan"]]

        apply_overrides(
            metadata,
            {"BackgroundSuppressionPulseTime": [1.465, 2.1, 2.6, 2.88]},
        )

        assert metadata[0]["BackgroundSuppressionPulseTime"] == [1.465, 2.1, 2.6, 2.88]
        assert metadata[1] == ["deltaM", "m0scan"]

    def test_no_metadata_mapping_is_noop(self) -> None:
        """A result with no dict is left untouched with an empty report."""
        metadata = ["only", "strings"]

        result, report = apply_overrides(metadata, {"BackgroundSuppression": True})

        assert result == ["only", "strings"]
        assert report.applied == []
        assert report.conflicts == []


class TestApplySidecarOverrides:
    """End-to-end discovery + overlay driven from a DICOM directory."""

    def test_discovers_and_applies(self, tmp_path: Path) -> None:
        """A real studyPar.json is found and its fields reach the metadata."""
        asl_dir = _make_session(
            tmp_path,
            '{"BackgroundSuppression": true,'
            ' "BackgroundSuppressionNumberPulses": 4,'
            ' "BackgroundSuppressionPulseTime": [1.465, 2.1, 2.6, 2.88]}',
        )
        metadata = {"BackgroundSuppression": True}

        _, report = apply_sidecar_overrides(metadata, str(asl_dir))

        assert metadata["BackgroundSuppressionPulseTime"] == [1.465, 2.1, 2.6, 2.88]
        assert metadata["BackgroundSuppressionNumberPulses"] == 4
        assert report.applied == [
            "BackgroundSuppressionNumberPulses",
            "BackgroundSuppressionPulseTime",
        ]
        assert report.sidecar_path is not None

    def test_none_dicom_dir_is_noop(self) -> None:
        """A None dicom_dir leaves the metadata untouched."""
        metadata = {"BackgroundSuppression": True}

        result, report = apply_sidecar_overrides(metadata, None)

        assert result == {"BackgroundSuppression": True}
        assert report.sidecar_path is None
        assert report.applied == []

    def test_no_sidecar_found_is_noop(self, tmp_path: Path) -> None:
        """When no sidecar exists, the metadata is unchanged."""
        asl_dir = _make_session(tmp_path, None)
        metadata = {"BackgroundSuppression": True}

        _, report = apply_sidecar_overrides(metadata, str(asl_dir))

        assert metadata == {"BackgroundSuppression": True}
        assert report.applied == []
        assert report.sidecar_path is None
