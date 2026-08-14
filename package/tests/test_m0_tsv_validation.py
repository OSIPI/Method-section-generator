"""Tests for M0 contradiction paths, TSV validation, and BS warnings."""

from typing import Callable

from pyaslreport.modalities.asl.processor import ASLProcessor, ProcessingContext

# ---------- _validate_m0_data ----------


class TestValidateM0Data:
    def test_separate_with_no_m0_file_errors(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """M0Type=Separate but m0_json missing -> error appended."""
        proc = make_processor()
        ctx = make_context(m0_type="Separate")
        group = {
            "asl_json": ("asl.json", {"M0Type": "Separate"}),
            "m0_json": None,
            "tsv": None,
        }
        proc._validate_m0_data(group, ctx, "asl.json", group["asl_json"][1])
        assert any("Separate" in e and "not provided" in e for e in ctx.errors)

    def test_absent_with_m0_file_errors(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """M0Type=Absent but m0_json present -> error appended."""
        proc = make_processor()
        ctx = make_context(m0_type="Absent")
        m0_data = {"EchoTime": 0.012}
        group = {
            "asl_json": ("asl.json", {"M0Type": "Absent"}),
            "m0_json": ("m0.json", m0_data),
            "tsv": None,
        }
        proc._validate_m0_data(group, ctx, "asl.json", group["asl_json"][1])
        assert any("Absent" in e and "is present" in e for e in ctx.errors)

    def test_included_with_separate_m0_file_errors(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """M0Type=Included but separate m0_json provided -> error."""
        proc = make_processor()
        ctx = make_context(m0_type="Included")
        m0_data = {"EchoTime": 0.012}
        group = {
            "asl_json": ("asl.json", {"M0Type": "Included"}),
            "m0_json": ("m0.json", m0_data),
            "tsv": None,
        }
        proc._validate_m0_data(group, ctx, "asl.json", group["asl_json"][1])
        assert any("Included" in e for e in ctx.errors)

    def test_separate_with_m0_file_no_error(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """M0Type=Separate with m0_json present -> no contradiction.

        Both ASL and M0 dicts agree on the five compare_params fields to avoid
        spurious errors from that helper.
        """
        proc = make_processor()
        ctx = make_context(m0_type="Separate")
        m0_data = {
            "EchoTime": 0.012,
            "FlipAngle": 90,
            "MagneticFieldStrength": 3,
            "MRAcquisitionType": "3D",
            "PulseSequenceType": "GRASE",
        }
        asl_data = dict(m0_data, M0Type="Separate")
        group = {
            "asl_json": ("asl.json", asl_data),
            "m0_json": ("m0.json", m0_data),
            "tsv": None,
        }
        proc._validate_m0_data(group, ctx, "asl.json", asl_data)
        m0_type_errors = [
            e for e in ctx.errors if "M0 type" in e or "specified as" in e
        ]
        assert m0_type_errors == []


# ---------- TSV: _analyze_tsv_volume_types and _validate_m0scan_consistency ----------


class TestTSVValidation:
    def test_absent_with_m0scan_in_tsv_errors(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """M0Type=Absent but TSV contains 'm0scan' -> error."""
        proc = make_processor()
        ctx = make_context(m0_type="Absent")
        asl_data = {"M0Type": "Absent"}
        tsv_data = ["m0scan", "control", "label"]
        proc._analyze_tsv_volume_types(
            tsv_data, ctx, "asl.json", asl_data, "context.tsv"
        )
        assert any("Absent" in e and "m0scan" in e for e in ctx.errors)

    def test_separate_with_m0scan_in_tsv_errors(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """M0Type=Separate but TSV contains 'm0scan' -> error."""
        proc = make_processor()
        ctx = make_context(m0_type="Separate")
        asl_data = {"M0Type": "Separate"}
        tsv_data = ["m0scan", "control", "label"]
        proc._analyze_tsv_volume_types(
            tsv_data, ctx, "asl.json", asl_data, "context.tsv"
        )
        assert any("Separate" in e and "m0scan" in e for e in ctx.errors)

    def test_total_acquired_pairs_set(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """A clean TSV populates TotalAcquiredPairs."""
        proc = make_processor()
        ctx = make_context(m0_type="Included")
        asl_data = {
            "M0Type": "Included",
            "RepetitionTimePreparation": 4.0,
            "BackgroundSuppression": False,
        }
        tsv_data = ["m0scan", "control", "label", "control", "label"]
        proc._analyze_tsv_volume_types(
            tsv_data, ctx, "asl.json", asl_data, "context.tsv"
        )
        assert asl_data["TotalAcquiredPairs"] == 2  # two control-label pairs

    def test_m0scan_with_missing_repetition_time_warns_without_crashing(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """M0 timing cannot be assessed without RepetitionTimePreparation."""
        proc = make_processor()
        ctx = make_context(m0_type="Included")
        asl_data = {"M0Type": "Included", "BackgroundSuppression": False}
        tsv_data = ["deltaM", "m0scan"]

        proc._analyze_tsv_volume_types(
            tsv_data, ctx, "asl.json", asl_data, "context.tsv"
        )

        expected_warning = (
            "Warning: Cannot determine M0 preparation timing for ASL file "
            "'asl.json' because neither 'RepetitionTimePreparation' nor "
            "'RepetitionTime' is present, but TSV file 'context.tsv' contains "
            "m0scan."
        )
        assert ctx.warnings == [expected_warning]


# ---------- _handle_no_m0scan_warnings ----------


class TestBackgroundSuppressionWarnings:
    def test_bs_off_no_warning(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """BackgroundSuppression off -> no warnings."""
        proc = make_processor()
        ctx = make_context()
        asl_data = {"BackgroundSuppression": False}
        proc._handle_no_m0scan_warnings(ctx, "asl.json", asl_data)
        assert ctx.warnings == []

    def test_bs_on_with_pulse_time_warns_about_efficiency(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """BS on with pulse times -> efficiency warning."""
        proc = make_processor()
        ctx = make_context()
        asl_data = {
            "BackgroundSuppression": True,
            "BackgroundSuppressionPulseTime": [0.15, 0.5],
        }
        proc._handle_no_m0scan_warnings(ctx, "asl.json", asl_data)
        assert any("BS-pulse efficiency" in w for w in ctx.warnings)

    def test_bs_on_no_pulse_time_warns_about_relative_quantification(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """BS on without pulse times -> relative-quantification warning."""
        proc = make_processor()
        ctx = make_context()
        asl_data = {"BackgroundSuppression": True}
        proc._handle_no_m0scan_warnings(ctx, "asl.json", asl_data)
        assert any("relative quantification" in w for w in ctx.warnings)


# ---------- _warn_if_voxel_geometry_missing ----------


class TestVoxelGeometryWarnings:
    def test_missing_voxel_geometry_warns(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """Absent AcquisitionVoxelSize surfaces a warning to the user."""
        proc = make_processor()
        ctx = make_context()
        asl_data = {"M0Type": "Included"}

        proc._warn_if_voxel_geometry_missing(ctx, "asl.json", asl_data)

        expected = (
            "Warning: Acquisition voxel geometry is missing for ASL file "
            "'asl.json'; 'AcquisitionVoxelSize' is absent or incomplete, so "
            "in-plane resolution and slice thickness are omitted from the "
            "report."
        )
        assert ctx.warnings == [expected]

    def test_incomplete_voxel_geometry_warns(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """A voxel array with fewer than three values still warns."""
        proc = make_processor()
        ctx = make_context()
        asl_data = {"AcquisitionVoxelSize": [3.0, 3.0]}

        proc._warn_if_voxel_geometry_missing(ctx, "asl.json", asl_data)

        assert len(ctx.warnings) == 1
        assert "voxel geometry is missing" in ctx.warnings[0]

    def test_present_voxel_geometry_no_warning(
        self,
        make_processor: Callable[..., ASLProcessor],
        make_context: Callable[..., ProcessingContext],
    ) -> None:
        """A complete AcquisitionVoxelSize produces no warning."""
        proc = make_processor()
        ctx = make_context()
        asl_data = {"AcquisitionVoxelSize": [3.0, 3.0, 4.0]}

        proc._warn_if_voxel_geometry_missing(ctx, "asl.json", asl_data)

        assert ctx.warnings == []
