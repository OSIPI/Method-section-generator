import math
from collections import Counter
from typing import Any


class ReportGenerator:
    from collections import Counter

    # =====================================================================
    # Tier 1 helpers (readability / cohesion)
    # =====================================================================
    @staticmethod
    def _is_missing(value: object) -> bool:
        """Return whether a value carries no usable report information.

        Args:
            value: Extracted parameter value to inspect.

        Returns:
            True when the value is None or a blank / "N/A" string.
        """
        if value is None:
            return True
        if isinstance(value, str) and value.strip() in ("", "N/A"):
            return True
        return False

    @staticmethod
    def _join_and(parts: list[object]) -> str:
        """Join items into natural-language prose with an Oxford comma.

        Args:
            parts: Items to join; falsy items are dropped.

        Returns:
            "" for no items, "a", "a and b", or "a, b, and c".
        """
        text_parts = [str(part) for part in parts if part]
        if not text_parts:
            return ""
        if len(text_parts) == 1:
            return text_parts[0]
        if len(text_parts) == 2:
            return f"{text_parts[0]} and {text_parts[1]}"
        return ", ".join(text_parts[:-1]) + ", and " + text_parts[-1]

    @staticmethod
    def _fmt_num(value: object, sig: int = 4) -> object:
        """Round a number to `sig` significant figures for display.

        Non-numeric values (including booleans) are returned unchanged. A whole
        result is returned as an int so it renders without a trailing ".0".

        Args:
            value: Value to format; only ints and floats are rounded.
            sig: Number of significant figures to keep.

        Returns:
            The rounded number (int when whole), or the value unchanged.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return value
        if value == 0 or not math.isfinite(value):
            return value
        digits = sig - 1 - math.floor(math.log10(abs(value)))
        rounded = round(value, digits)
        return int(rounded) if rounded == int(rounded) else rounded

    @staticmethod
    def _within_tolerance(numbers: list[float], tol: float = 0.01) -> bool:
        """Return whether all numbers lie within a fractional tolerance.

        Args:
            numbers: Numeric values to compare (must be non-empty).
            tol: Maximum fractional spread, e.g. 0.01 for 1%.

        Returns:
            True when the spread (max - min) relative to the mean is <= `tol`.
        """
        lo, hi = min(numbers), max(numbers)
        if lo == hi:
            return True
        mean = sum(numbers) / len(numbers)
        if mean == 0:
            return False
        return (hi - lo) / abs(mean) <= tol

    @staticmethod
    def _format_duration_list(value: object, unit: str = "ms") -> str:
        """Format a duration value or list, collapsing near-identical entries.

        Args:
            value: Scalar duration, list/tuple of durations, or a missing value.
            unit: Unit suffix appended to each rendered number.

        Returns:
            "" when the value is missing, a single "<n><unit>" when a list holds
            values that agree within 1%, otherwise the comma-joined values.
        """
        if ReportGenerator._is_missing(value):
            return ""
        if isinstance(value, (list, tuple)):
            numbers = [
                v
                for v in value
                if isinstance(v, (int, float)) and not isinstance(v, bool)
            ]
            if (
                numbers
                and len(numbers) == len(value)
                and ReportGenerator._within_tolerance(numbers)
            ):
                mean = sum(numbers) / len(numbers)
                return f"{ReportGenerator._fmt_num(mean)}{unit}"
            formatted = [ReportGenerator._fmt_num(v) for v in value]
            uniq = list(dict.fromkeys(formatted))  # de-duplicate, preserve order
            if len(uniq) == 1:
                return f"{uniq[0]}{unit}"
            return ", ".join(f"{v}{unit}" for v in formatted)
        return f"{ReportGenerator._fmt_num(value)}{unit}"

    # Raw internal pattern tokens -> human-readable words
    _PATTERN_DISPLAY = {
        # GE performs control/label subtraction on the scanner and stores only
        # deltaM volumes, but each represents one control-label pair, so it is
        # reported as such (meeting notes, Jan).
        "deltam": "control-label",
        "controllabel": "control-label",
        "labelcontrol": "label-control",
    }

    @staticmethod
    def _pattern_words(global_pattern: str, plural: bool) -> tuple[str, str]:
        """Map an internal volume pattern to a display label and count noun.

        Every ASL volume pattern is reported in control-label "pair" terms; the
        GE "deltam" case is treated as a control-label pair rather than a
        standalone deltaM volume.

        Args:
            global_pattern: Internal token (e.g. "deltam", "controllabel").
            plural: Whether the count noun should be pluralized.

        Returns:
            A (label, noun) pair, e.g. ("control-label", "pairs") or
            ("label-control", "pair").
        """
        label = ReportGenerator._PATTERN_DISPLAY.get(global_pattern, global_pattern)
        noun = "pairs" if plural else "pair"
        return label, noun

    @staticmethod
    def generate_asl_report(
        values: dict[str, Any],
        combined_major_errors: dict[str, Any],
        combined_errors: dict[str, Any],
        global_pattern: str | None,
        m0_type: str | None,
        total_acquired_pairs: int | None,
        slice_number: int,
    ) -> tuple[str, list[tuple[str, Any]]]:
        """Build the ASL Methods paragraph and its structured parameter list.

        Rewritten as a modular, multi-sentence builder: scanner/family,
        timing/suppression, and geometry/repetitions. Clauses whose values are
        missing drop out entirely instead of emitting placeholders.

        Args:
            values: Extracted BIDS parameter values keyed by field name.
            combined_major_errors: Major-error data keyed by field name.
            combined_errors: Non-major error/inconsistency data keyed by field.
            global_pattern: ASL volume pattern token, or None.
            m0_type: M0 acquisition type, or None.
            total_acquired_pairs: Number of acquired control-label pairs, or None.
            slice_number: Number of slices from the NIfTI header.

        Returns:
            A (report_paragraph, asl_parameters) tuple, where asl_parameters is
            a list of (label, value) pairs.
        """
        asl_parameters = []
        is_missing = ReportGenerator._is_missing
        fmt_num = ReportGenerator._fmt_num

        # ---- extraction (unchanged from original) ----
        pld_type = ReportGenerator.handle_bolus_cutoff_technique(
            values, "PLDType", combined_major_errors
        )
        extended_pld_text = ReportGenerator.handle_pld_values(
            values, combined_errors, "PostLabelingDelay", global_pattern, m0_type
        )
        magnetic_field_strength = ReportGenerator.extract_value(
            values, "MagneticFieldStrength", combined_errors
        )
        manufacturer = ReportGenerator.extract_value(
            values, "Manufacturer", combined_errors
        )
        manufacturers_model_name = (
            ReportGenerator.extract_and_format_unique_string_values(
                values, "ManufacturersModelName"
            )
        )
        asl_type = ReportGenerator.extract_value(
            values, "ArterialSpinLabelingType", combined_major_errors
        )
        mr_acq_type = ReportGenerator.extract_value(
            values, "MRAcquisitionType", combined_major_errors
        )
        pulse_seq_type = ReportGenerator.extract_value(
            values, "PulseSequenceType", combined_major_errors
        )
        if pulse_seq_type == "3Dgrase":
            pulse_seq_type = "GRASE"
        echo_time = ReportGenerator.extract_value(values, "EchoTime", combined_errors)
        repetition_time = ReportGenerator.handle_pld_values(
            values, combined_errors, "RepetitionTimePreparation"
        )
        flip_angle = ReportGenerator.extract_value(values, "FlipAngle", combined_errors)
        labeling_duration = ReportGenerator.extract_value(
            values, "LabelingDuration", combined_errors
        )
        voxel_size_1_2, voxel_size_3 = ReportGenerator.handle_voxel_size(
            values, combined_errors
        )
        bolus_cutoff_flag = ReportGenerator.handle_bolus_cutoff_flag(
            values, "BolusCutOffFlag", combined_errors
        )
        bolus_cutoff_technique = ReportGenerator.handle_bolus_cutoff_technique(
            values, "BolusCutOffTechnique", combined_errors
        )
        bolus_cutoff_delay_time = ReportGenerator.handle_bolus_cutoff_delay_time(
            values, combined_errors
        )
        background_suppression = ReportGenerator.handle_bolus_cutoff_flag(
            values, "BackgroundSuppression", combined_errors
        )
        background_suppression_number_pulses = ReportGenerator.extract_value(
            values,
            "BackgroundSuppressionNumberPulses",
            combined_errors,
            report_range=True,
        )
        background_suppression_pulse_time = ReportGenerator.extract_value(
            values, "BackgroundSuppressionPulseTime", combined_errors
        )
        acquisition_duration = ReportGenerator.extract_value(
            values, "AcquisitionDuration", combined_errors, format_duration=True
        )
        pasl_type = ReportGenerator.extract_value(
            values, "PASLType", combined_errors, recommneded=True
        )
        labeling_slab_thickness = ReportGenerator.extract_value(
            values, "LabelingSlabThickness", combined_errors, recommneded=True
        )

        is_pasl = str(asl_type).upper() == "PASL"
        is_pcasl = str(asl_type).upper() in ("PCASL", "CASL")

        # =================================================================
        # Sentence 1: scanner + acquisition family + readout
        # =================================================================
        scanner = ""
        if not is_missing(magnetic_field_strength):
            scanner += f"{magnetic_field_strength}T "
        for part in (manufacturer, manufacturers_model_name):
            if not is_missing(part):
                scanner += f"{part} "
        scanner = scanner.strip()
        s1 = "ASL was acquired on a " + (
            f"{scanner} scanner." if scanner else "scanner."
        )

        # labeling phrase (drop 'N/A' ASL type instead of writing 'N/A labeling')
        family = ReportGenerator._join_and([]) or " ".join(
            [
                p
                for p in (
                    pld_type if not is_missing(pld_type) else "",
                    pasl_type if not is_missing(pasl_type) else "",
                    asl_type if not is_missing(asl_type) else "",
                )
                if p
            ]
        )
        # readout: de-duplicate dimensionality vs readout type ('3D 3D' -> '3D')
        readout_parts = []
        if not is_missing(mr_acq_type):
            readout_parts.append(mr_acq_type)
        if not is_missing(pulse_seq_type) and pulse_seq_type != mr_acq_type:
            readout_parts.append(pulse_seq_type)
        readout = " ".join(readout_parts)

        family_cap = (family[0].upper() + family[1:]) if family else family
        if family and readout:
            s1 += f" {family_cap} labeling was performed with a {readout} readout."
        elif family:
            s1 += f" {family_cap} labeling was performed."
        elif readout:
            s1 += f" A {readout} readout was used."

        asl_parameters.append(
            ("Magnetic Field Strength", f"{magnetic_field_strength}T")
        )
        asl_parameters.append(("Manufacturer", manufacturer))
        asl_parameters.append(("Manufacturer's Model Name", manufacturers_model_name))
        asl_parameters.append(("PLD Type", pld_type))
        if not is_missing(pasl_type):
            asl_parameters.append(("PASL Type", pasl_type))
        asl_parameters.append(("ASL Type", asl_type))
        asl_parameters.append(("MR Acquisition Type", mr_acq_type))
        asl_parameters.append(("Pulse Sequence Type", pulse_seq_type))

        # =================================================================
        # Sentence 2: ASL timing + background suppression
        # =================================================================
        timing = ""
        if is_pcasl:
            ld = ReportGenerator._format_duration_list(labeling_duration, "ms")
            pld = "" if is_missing(extended_pld_text) else str(extended_pld_text)
            if ld:
                asl_parameters.append(("Labeling Duration", labeling_duration))
            if pld:
                asl_parameters.append(("PLD", extended_pld_text))
            pld_word = "a PLD of" if ("," not in pld) else "PLDs of"
            if ld and pld:
                timing = f"The labeling duration was {ld}, followed by {pld_word} {pld}"
            elif ld:
                timing = f"The labeling duration was {ld}"
            elif pld:
                timing = f"{pld_word[0].upper() + pld_word[1:]} {pld}"
        elif is_pasl:
            inv = "" if is_missing(extended_pld_text) else str(extended_pld_text)
            inv_word = (
                "an inversion time of" if ("," not in inv) else "inversion times of"
            )
            if inv:
                timing = f"Labeling used {inv_word} {inv}"
                asl_parameters.append(("Inversion Time", extended_pld_text))
            if not is_missing(labeling_slab_thickness):
                clause = f"a labeling slab thickness of {labeling_slab_thickness}mm"
                timing = (
                    f"{timing}, with {clause}"
                    if timing
                    else clause[0].upper() + clause[1:]
                )
                asl_parameters.append(
                    ("Labeling Slab Thickness", f"{labeling_slab_thickness}mm")
                )
            if bolus_cutoff_flag == "with":
                bolus = "with bolus saturation"
                if not is_missing(bolus_cutoff_technique):
                    bolus += f" using a {bolus_cutoff_technique} pulse"
                    asl_parameters.append(
                        ("Bolus Cutoff Technique", bolus_cutoff_technique)
                    )
                if not is_missing(bolus_cutoff_delay_time):
                    bolus += f" applied {bolus_cutoff_delay_time} after labeling"
                    asl_parameters.append(
                        ("Bolus Cutoff Delay Time", bolus_cutoff_delay_time)
                    )
                timing = (
                    f"{timing}, {bolus}" if timing else bolus[0].upper() + bolus[1:]
                )
                asl_parameters.append(("Bolus Cutoff Flag", bolus_cutoff_flag))
            elif bolus_cutoff_flag == "without":
                asl_parameters.append(("Bolus Cutoff Flag", bolus_cutoff_flag))

        suppression = ""
        if background_suppression == "with":
            suppression = "Background suppression was applied"
            if not is_missing(background_suppression_number_pulses):
                suppression += f" using {background_suppression_number_pulses} pulses"
                asl_parameters.append(
                    (
                        "Background Suppression Number of Pulses",
                        background_suppression_number_pulses,
                    )
                )
            if not is_missing(background_suppression_pulse_time):
                times = ReportGenerator.format_background_suppression(
                    background_suppression_pulse_time
                )
                suppression += f", with pulses at {times} after the start of labeling"
                asl_parameters.append(("Background Suppression Pulse Time", times))
        elif background_suppression == "without":
            suppression = "Background suppression was not applied"
        elif not is_missing(background_suppression):
            suppression = f"Background suppression was {background_suppression}"
        if not is_missing(background_suppression):
            asl_parameters.append(("Background Suppression", background_suppression))

        s2 = ". ".join([c for c in (timing, suppression) if c])
        if s2:
            s2 += "."

        # =================================================================
        # Sentence 3: imaging geometry + repetitions
        # =================================================================
        geo = []
        te_ok, tr_ok = not is_missing(echo_time), not is_missing(repetition_time)
        if te_ok and tr_ok:
            geo.append(f"TR/TE = {repetition_time}/{fmt_num(echo_time)}ms")
        elif te_ok:
            geo.append(f"TE = {fmt_num(echo_time)}ms")
        elif tr_ok:
            geo.append(f"TR = {repetition_time}")
        if not is_missing(voxel_size_1_2):
            geo.append(f"an in-plane resolution of {voxel_size_1_2}mm^2")
        if slice_number:
            geo.append(f"{slice_number} slices")
        if not is_missing(voxel_size_3):
            geo.append(f"a slice thickness of {voxel_size_3}mm")
        if not is_missing(flip_angle):
            geo.append(f"a flip angle of {fmt_num(flip_angle)} degrees")

        asl_parameters.append(("Echo Time", f"{echo_time}ms"))
        asl_parameters.append(("Repetition Time", repetition_time))
        asl_parameters.append(("Flip Angle", flip_angle))
        asl_parameters.append(("In-plane Resolution", f"{voxel_size_1_2}mm^2"))
        asl_parameters.append(("Slice Thickness", f"{voxel_size_3}mm"))

        s3 = (
            f"Images were acquired with {ReportGenerator._join_and(geo)}."
            if geo
            else ""
        )

        # repetitions (guarded so a missing count never prints 'None')
        rep = ""
        pattern_known = global_pattern not in (None, "", "pattern error")
        if (
            not is_missing(total_acquired_pairs)
            and total_acquired_pairs != 0
            and pattern_known
        ):
            plural = total_acquired_pairs != 1
            label, noun = ReportGenerator._pattern_words(global_pattern, plural)
            verb = "were" if plural else "was"
            rep = f"In total, {total_acquired_pairs} {label} {noun} {verb} acquired"
            if acquisition_duration != "N/A":
                rep += f" over a {acquisition_duration} acquisition"
                asl_parameters.append(("Acquisition Duration", acquisition_duration))
            rep += "."
        asl_parameters.append(("Total Acquired Pairs", total_acquired_pairs))

        report_paragraph = " ".join([s for s in (s1, s2, s3, rep) if s])
        return report_paragraph, asl_parameters

    # Function to generate a report for M0 scans based on provided parameters.
    # This adds details about M0 scans and their TR (repetition time).
    @staticmethod
    def generate_m0_report(report_line_on_M0, M0_TR):
        report_lines = []
        if report_line_on_M0:
            report_lines.append(f" {report_line_on_M0}")
        if M0_TR:
            report_lines.append(f" TR for M0 is {M0_TR}ms.")
        report_paragraph = "".join(line for line in report_lines)
        return report_paragraph

    # Function to generate an extended report that includes additional technical details
    # about the ASL acquisition, such as vascular crushing and labeling pulse parameters.
    @staticmethod
    def generate_extended_report(values, combined_major_errors, combined_errors):
        report_lines = []
        extended_parameters = []
        vascular_crushing = ReportGenerator.extract_value(
            values, "VascularCrushing", combined_errors, recommneded=True
        )
        vascular_crushing_VENC = ReportGenerator.extract_value(
            values, "VascularCrushingVENC", combined_errors, recommneded=True
        )
        PCASL_type = ReportGenerator.extract_value(
            values, "PCASLType", combined_errors, recommneded=True
        )
        labeling_pulse_average_gradient = ReportGenerator.extract_value(
            values, "LabelingPulseAverageGradient", combined_errors, recommneded=True
        )
        labeling_pulse_maximum_gradient = ReportGenerator.extract_value(
            values, "LabelingPulseMaximumGradient", combined_errors, recommneded=True
        )
        labeling_pulse_average_B1 = ReportGenerator.extract_value(
            values, "LabelingPulseAverageB1", combined_errors, recommneded=True
        )
        labeling_pulse_flip_angle = ReportGenerator.extract_value(
            values, "LabelingPulseFlipAngle", combined_errors, recommneded=True
        )
        labeling_pulse_interval = ReportGenerator.extract_value(
            values, "LabelingPulseInterval", combined_errors, recommneded=True
        )
        labeling_pulse_duration = ReportGenerator.extract_value(
            values, "LabelingPulseDuration", combined_errors, recommneded=True
        )
        if isinstance(vascular_crushing, bool) and vascular_crushing:
            report_lines.append(" Vascular crushing was applied")
            extended_parameters.append(("Vascular Crushing", vascular_crushing))
            if vascular_crushing_VENC == "":
                report_lines.append(".")
            else:
                report_lines.append(f" with a {vascular_crushing_VENC}cm/s threshold.")
                extended_parameters.append(
                    ("Vascular Crushing VENC", vascular_crushing_VENC)
                )
        elif isinstance(vascular_crushing, str) and vascular_crushing:
            report_lines.append(f" Vascular crushing was {vascular_crushing}")
            extended_parameters.append(("Vascular Crushing", vascular_crushing))
            if vascular_crushing_VENC == "":
                report_lines.append(".")
            else:
                report_lines.append(f" with a {vascular_crushing_VENC}cm/s threshold.")
                extended_parameters.append(
                    ("Vascular Crushing VENC", vascular_crushing_VENC)
                )

        if PCASL_type:
            if PCASL_type == "balanced":
                report_lines.append(f" Balanced")
            elif PCASL_type == "unbalanced":
                report_lines.append(f" Unbalanced")
            extended_parameters.append(("PCASL Type", PCASL_type))
        if (
            labeling_pulse_average_gradient
            or labeling_pulse_maximum_gradient
            or labeling_pulse_average_B1
            or labeling_pulse_flip_angle
            or labeling_pulse_interval
            or labeling_pulse_duration
        ):
            report_lines.append(
                f" PCASL labeling was applied with the following pulse parameters: "
            )
        if labeling_pulse_average_gradient:
            if not labeling_pulse_maximum_gradient:
                report_lines.append(
                    f"average pulse gradient {labeling_pulse_average_gradient}mT/m"
                )
            else:
                report_lines.append(
                    f"average {labeling_pulse_average_gradient}mT/m and "
                )
            extended_parameters.append(
                (
                    "Labeling Pulse Average Gradient",
                    f"{labeling_pulse_average_gradient}mT/m",
                )
            )
        if labeling_pulse_maximum_gradient:
            report_lines.append(
                f"maximum pulse gradient {labeling_pulse_maximum_gradient}mT/m"
            )
            extended_parameters.append(
                (
                    "Labeling Pulse Maximum Gradient",
                    f"{labeling_pulse_maximum_gradient}mT/m",
                )
            )
        if (labeling_pulse_average_gradient or labeling_pulse_maximum_gradient) and (
            labeling_pulse_duration
            or labeling_pulse_interval
            or labeling_pulse_average_B1
            or labeling_pulse_flip_angle
        ):
            report_lines.append(", ")

        if labeling_pulse_duration:
            report_lines.append(f"with {labeling_pulse_duration}ms pulses")
            extended_parameters.append(
                ("Labeling Pulse Duration", f"{labeling_pulse_duration}ms")
            )
        if labeling_pulse_interval:
            report_lines.append(f" applied at {labeling_pulse_interval}ms intervals")
            extended_parameters.append(
                ("Labeling Pulse Interval", f"{labeling_pulse_interval}ms")
            )
        if (labeling_pulse_duration or labeling_pulse_interval) and (
            labeling_pulse_average_B1 or labeling_pulse_flip_angle
        ):
            report_lines.append(", ")

        if labeling_pulse_average_B1:
            report_lines.append(
                f"average B1-field strength {labeling_pulse_average_B1}mT"
            )
            extended_parameters.append(
                (
                    "Labeling Pulse Average B1-field Strength",
                    f"{labeling_pulse_average_B1}mT",
                )
            )
        elif labeling_pulse_flip_angle:
            report_lines.append(f"with {labeling_pulse_flip_angle} degree flip angle")
            extended_parameters.append(
                ("Labeling Pulse Flip Angle", labeling_pulse_flip_angle)
            )

        if (
            labeling_pulse_average_gradient
            or labeling_pulse_maximum_gradient
            or labeling_pulse_average_B1
            or labeling_pulse_flip_angle
            or labeling_pulse_interval
            or labeling_pulse_duration
        ):
            report_lines.append(".")
        report_paragraph = "".join(line for line in report_lines)
        return report_paragraph, extended_parameters

    # Function to extract a specific value from the provided values dictionary.
    # This function also handles inconsistencies and formats the value based on the context (e.g., reporting range, duration).
    @staticmethod
    def extract_value(
        values,
        key,
        combined_errors,
        report_range=False,
        format_duration=False,
        recommneded=False,
    ):
        status, most_common_value, value_range = ReportGenerator.handle_inconsistency(
            values, key, combined_errors
        )

        if format_duration and isinstance(most_common_value, (int, float)):
            most_common_value = ReportGenerator.format_acquisition_duration(
                most_common_value
            )

        if status == "consistent":
            if most_common_value == "N/A" and recommneded:
                return ""
            return most_common_value
        elif status == "inconsistent_common":
            return (
                f"(inconsistent, {most_common_value} is the most common data)"
                if not report_range
                else f"(inconsistent, {most_common_value} is the most common data, {value_range})"
            )
        else:
            return (
                f"(inconsistent, no common data, {value_range})"
                if report_range
                else "(inconsistent, no common data)"
            )

    # Helper function to handle inconsistencies in the extracted values.
    # This function checks for inconsistencies across different sources and identifies the most common value or range.
    @staticmethod
    def handle_inconsistency(values, key, combined_errors):
        inconsistencies = [
            error for error in combined_errors.get(key, []) if "INCONSISTENCY" in error
        ]
        value_range = None

        if inconsistencies:
            key_values = [entry[1] for entry in values.get(key, [])]

            normalized_values = []
            for val in key_values:
                if isinstance(val, list):
                    if len(val) == 1:
                        normalized_values.append(val[0])
                    else:
                        normalized_values.append(tuple(val))
                else:
                    normalized_values.append(val)

            counter = Counter(normalized_values)
            most_common_value, count = counter.most_common(1)[0]

            flattened_values = [
                item
                for sublist in normalized_values
                for item in (sublist if isinstance(sublist, tuple) else [sublist])
            ]
            value_range = f"Range: {min(flattened_values)}-{max(flattened_values)}"

            if count > len(normalized_values) // 2:
                return "inconsistent_common", most_common_value, value_range
            else:
                return "inconsistent_no_common", None, value_range
        else:
            first_value = values.get(key, [["N/A"]])
            if (
                first_value
                and isinstance(first_value[0], list)
                and len(first_value[0]) > 1
            ):
                value = tuple(first_value[0])
            else:
                value = first_value[0][1] if first_value else "N/A"

            return "consistent", value, value_range

    # Function to handle the extraction and consistency checking of the bolus cutoff technique.
    # This function examines the provided values for the specified key (bolus cutoff technique) and checks
    # whether the data is consistent across multiple sources.
    @staticmethod
    def handle_bolus_cutoff_technique(values, key, combined_errors):
        status, technique = ReportGenerator.handle_string_inconsistency(
            values, key, combined_errors
        )
        if status == "consistent":
            return technique
        elif status == "inconsistent_common":
            return f"(inconsistent, {technique} is the most common)"
        else:
            return "(inconsistent, no common data)"

    # Helper function to manage inconsistencies in string values.
    # This function checks for common values across different sources and handles inconsistency cases.
    @staticmethod
    def handle_string_inconsistency(values, key, combined_errors):
        inconsistencies = [
            error for error in combined_errors.get(key, []) if "INCONSISTENCY" in error
        ]
        if inconsistencies:
            key_values = [entry[1] for entry in values.get(key, [])]
            normalized_values = [str(val) for val in key_values]
            counter = Counter(normalized_values)
            most_common_value, count = counter.most_common(1)[0]
            if count > len(normalized_values) // 2:
                return "inconsistent_common", most_common_value
            else:
                return "inconsistent_no_common", None
        else:
            first_value = values.get(key, [["N/A"]])
            return "consistent", str(first_value[0][1]) if first_value else "N/A"

    # Helper function to handle voxel size extraction and format the results.
    # It accounts for inconsistencies in the voxel sizes and formats them appropriately for reporting.
    @staticmethod
    def handle_voxel_size(values, combined_errors):
        status, acquisition_voxel_size, _ = ReportGenerator.handle_inconsistency(
            values, "AcquisitionVoxelSize", combined_errors
        )
        if status == "consistent":
            if (
                isinstance(acquisition_voxel_size, (list, tuple))
                and len(acquisition_voxel_size) >= 3
            ):
                voxel_size_1_2 = (
                    f"{acquisition_voxel_size[0]}x{acquisition_voxel_size[1]}"
                )
                voxel_size_3 = acquisition_voxel_size[2]
            else:
                voxel_size_1_2 = "N/A"
                voxel_size_3 = "N/A"
        elif status == "inconsistent_common":
            if (
                isinstance(acquisition_voxel_size, (list, tuple))
                and len(acquisition_voxel_size) >= 3
            ):
                voxel_size_1_2 = f"(inconsistent, {acquisition_voxel_size[0]}x{acquisition_voxel_size[1]} is the most common)"
                voxel_size_3 = (
                    f"(inconsistent, {acquisition_voxel_size[2]} is the most common)"
                )
            else:
                voxel_size_1_2 = "N/A"
                voxel_size_3 = "N/A"
        else:
            voxel_size_1_2 = "N/A (inconsistent, with no common data.)"
            voxel_size_3 = "N/A (inconsistent, with no common data.)"
        return voxel_size_1_2, voxel_size_3

    # Helper function to handle PLD (Post-Labeling Delay) values and format them for reporting.
    # The function manages cases where the PLD values are consistent or inconsistent across different sources.
    @staticmethod
    def handle_pld_values(
        values, combined_errors, key, global_pattern=False, m0_type=""
    ):
        status, pld_values, _ = ReportGenerator.handle_inconsistency(
            values, key, combined_errors
        )
        # Round PLD values to 4 significant figures for display.
        if isinstance(pld_values, (list, tuple)):
            pld_values = [ReportGenerator._fmt_num(v) for v in pld_values]
        else:
            pld_values = ReportGenerator._fmt_num(pld_values)

        @staticmethod
        def format_pld_array(pld_array):
            filtered_array = [pld for pld in pld_array if pld != 0]
            pld_counter = Counter(filtered_array)

            if global_pattern != "deltam":
                formatted_pld = ", ".join(
                    [
                        f"{pld}ms ({count // 2} {'repeat' if (count // 2) == 1 else 'repeats'})"
                        for pld, count in sorted(pld_counter.items())
                    ]
                )
            else:
                formatted_pld = ", ".join(
                    [
                        f"{pld}ms ({count} {'volume' if count == 1 else 'volumes'})"
                        for pld, count in sorted(pld_counter.items())
                    ]
                )
            return formatted_pld

        if status == "consistent":
            if isinstance(pld_values, (list, tuple)):
                unique_values = set(pld_values)
                if len(unique_values) == 1:
                    extended_pld_text = f"{unique_values.pop()}ms"
                else:
                    extended_pld_text = format_pld_array(pld_values)
            elif isinstance(pld_values, (int, float)):
                extended_pld_text = f"{pld_values}ms"
            else:
                extended_pld_text = "N/A"
        elif status == "inconsistent_common":
            if isinstance(pld_values, (list, tuple)):
                unique_values = set(pld_values)
                if len(unique_values) == 1:
                    extended_pld_text = (
                        f"(inconsistent, {unique_values.pop()}ms is the most common)"
                    )
                else:
                    extended_pld_text = f"(inconsistent, {format_pld_array(pld_values)} is the most common)"
            elif isinstance(pld_values, (int, float)):
                extended_pld_text = f"(inconsistent, {pld_values}ms is the most common)"
            else:
                extended_pld_text = "N/A"
        else:
            extended_pld_text = "(inconsistent, no common data)"

        return extended_pld_text

    # Helper function to handle bolus cutoff flag extraction and manage inconsistencies.
    # This function formats the bolus cutoff flag for reporting.
    @staticmethod
    def handle_bolus_cutoff_flag(values, key, combined_errors):
        status, flag = ReportGenerator.handle_boolean_inconsistency(
            values, key, combined_errors
        )
        if status == "consistent":
            return "without" if not flag else "with"
        elif status == "inconsistent_common":
            return f"(inconsistent, {'without' if not flag else 'with'} is the most common)"
        else:
            return "(inconsistent, no common data)"

    # Helper function to manage inconsistencies in boolean values.
    # It identifies the most common value or returns an indication of inconsistency.
    @staticmethod
    def handle_boolean_inconsistency(values, key, combined_errors):
        inconsistencies = [
            error for error in combined_errors.get(key, []) if "INCONSISTENCY" in error
        ]
        if inconsistencies:
            key_values = [entry[1] for entry in values.get(key, [])]
            normalized_values = [bool(val) for val in key_values]
            counter = Counter(normalized_values)
            most_common_value, count = counter.most_common(1)[0]
            if count > len(normalized_values) // 2:
                return "inconsistent_common", most_common_value
            else:
                return "inconsistent_no_common", None
        else:
            first_value = values.get(key, [["N/A"]])
            return "consistent", bool(first_value[0][1]) if first_value else "N/A"

    # Helper function to format bolus cutoff delay time.
    # It accounts for consistency or inconsistency in the values across different sources.
    @staticmethod
    def handle_bolus_cutoff_delay_time(values, combined_errors):
        status, bolus_cutoff_delay_time, _ = ReportGenerator.handle_inconsistency(
            values, "BolusCutOffDelayTime", combined_errors
        )
        if status == "consistent":
            if (
                isinstance(bolus_cutoff_delay_time, (list, tuple))
                and len(bolus_cutoff_delay_time) >= 2
            ):
                return f"from {bolus_cutoff_delay_time[0]}ms to {bolus_cutoff_delay_time[len(bolus_cutoff_delay_time) - 1]}ms"
            elif isinstance(bolus_cutoff_delay_time, (list, tuple)):
                return f"at {bolus_cutoff_delay_time[0]}ms"
            else:
                return f"at {bolus_cutoff_delay_time}ms"
        elif status == "inconsistent_common":
            return f"(inconsistent, {bolus_cutoff_delay_time}ms is the most common)"
        else:
            return "(inconsistent, no common data)"

    # Helper function to format background suppression timing information.
    # The function returns the formatted string based on the provided timing values.
    @staticmethod
    def format_background_suppression(values):
        if not values:
            return ""

        if all(isinstance(val, (int, float)) for val in values):
            values = list(map(str, values))
            if len(values) == 1:
                return values[0] + "ms"
            elif len(values) == 2:
                return "ms and ".join(values) + "ms"
            else:
                return "ms, ".join(values[:-1]) + "ms, and " + values[-1] + "ms"
        else:
            return values

    # Helper function to format acquisition duration.
    # Converts duration in seconds to a human-readable format (e.g., minutes and seconds).
    @staticmethod
    def format_acquisition_duration(duration):
        if isinstance(duration, (int, float)):
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes}:{seconds:02d}min"
        return "N/A"

    # Helper function to extract and format unique string values for reporting.
    # Combines all unique values into a single string, separated by slashes.
    @staticmethod
    def extract_and_format_unique_string_values(values, key):
        key_values = [entry[1] for entry in values.get(key, [])]
        normalized_values = [str(val) for val in key_values]
        value_counter = Counter(normalized_values)
        sorted_unique_values = [val for val, count in value_counter.most_common()]
        formatted_values = "/".join(sorted_unique_values)
        return formatted_values

    # Helper function to extract unique values from an array and format them as a comma-separated string.
    @staticmethod
    def extract_unique_values_from_array(values):
        unique_values = sorted(set(values))
        return ", ".join(map(str, unique_values))

    # Function to extract inconsistencies from the error map and clean up the error dictionary.
    # This helps isolate specific inconsistency issues for better reporting.
    @staticmethod
    def extract_inconsistencies(error_map):
        inconsistency_errors = []
        fields_to_remove = []

        for field, errors in error_map.items():
            for error in errors:
                if "INCONSISTENCY" in error:
                    inconsistency_errors.append(
                        f"{field}: {error.replace('INCONSISTENCY: ', '')}\n"
                    )
                    errors.remove(error)

                if not errors:
                    fields_to_remove.append(field)

        for field in fields_to_remove:
            del error_map[field]
        return inconsistency_errors
