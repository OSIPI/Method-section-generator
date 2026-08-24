"""In-memory overlay of a BIDS-style JSON sidecar onto DICOM-derived metadata.

This module loads a BIDS-style JSON "sidecar" that ships alongside the DICOMs
(for example ``studyPar.json``) and overlays its fields onto the metadata
extracted from the DICOM headers. The overlay happens entirely in memory; the
source DICOM files are never modified, consistent with the anonymization-repair
philosophy used elsewhere in the package.

The sidecar is treated as authoritative ("JSON wins"): when a field is present
in both the extracted metadata and the sidecar, the sidecar value replaces the
extracted one. Replacing a *differing* extracted value is recorded as a conflict
so the caller can surface a warning instead of changing a value silently.

Discovery, field scope, and name-aliasing are driven by module-level constants
so behaviour can be adjusted without touching call sites.
"""

from __future__ import annotations

import glob
import json
import logging as log
import os
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "SIDECAR_GLOBS",
    "SIDECAR_NAME_EXCLUDES",
    "SEARCH_PARENT",
    "OVERRIDE_ALLOWLIST",
    "FIELD_ALIASES",
    "OverrideReport",
    "discover_sidecars",
    "load_sidecar",
    "apply_overrides",
    "apply_sidecar_overrides",
]

# ---------------------------------------------------------------------------
# Configurable knobs
# ---------------------------------------------------------------------------

#: Filename patterns that count as a sidecar, searched in the given order.
SIDECAR_GLOBS: tuple[str, ...] = ("*.json",)

#: Case-insensitive substrings that DISQUALIFY a JSON from being treated as a
#: sidecar. Guards against report/golden files (e.g. ``expected_output.json``)
#: that sit next to the DICOMs, especially in integration example folders.
SIDECAR_NAME_EXCLUDES: tuple[str, ...] = ("output",)

#: Whether to also search the parent (session) folder of the DICOM directory.
SEARCH_PARENT: bool = True

#: When not ``None``, only these post-alias keys are allowed to be overlaid.
OVERRIDE_ALLOWLIST: set[str] | None = None

#: Sidecar field names mapped onto the tool's internal metadata keys.
FIELD_ALIASES: dict[str, str] = {
    "LabelingType": "ArterialSpinLabelingType",
    "M0": "M0Type",
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------
@dataclass
class OverrideReport:
    """Record of what a sidecar overlay changed.

    Attributes:
        sidecar_path: Path of the sidecar that was applied, or ``None`` when no
            sidecar was found or applied.
        applied: Post-alias keys newly added to the metadata (absent before).
        conflicts: ``(key, dicom_value, sidecar_value)`` for each field whose
            differing extracted value was overridden by the sidecar.
        aliased: ``(sidecar_name, internal_key)`` for each remapped field.
        skipped: Sidecar field names skipped because of the allowlist.
    """

    sidecar_path: str | None = None
    applied: list[str] = field(default_factory=list)
    conflicts: list[tuple[str, Any, Any]] = field(default_factory=list)
    aliased: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------
def discover_sidecars(dicom_dir: str | None) -> list[str]:
    """Find sidecar JSON files next to a DICOM directory.

    Searches ``dicom_dir`` and, when :data:`SEARCH_PARENT` is set, its parent
    (session) folder for files matching :data:`SIDECAR_GLOBS`.

    Args:
        dicom_dir: Directory the DICOM files were read from.

    Returns:
        Absolute sidecar paths, de-duplicated and in a stable (sorted) order,
        excluding any whose name matches :data:`SIDECAR_NAME_EXCLUDES`. Empty when
        ``dicom_dir`` is falsy or nothing matches.
    """
    if not dicom_dir:
        return []

    roots = [dicom_dir]
    if SEARCH_PARENT:
        roots.append(os.path.dirname(os.path.normpath(dicom_dir)))

    found: list[str] = []
    seen: set[str] = set()
    for root in roots:
        for pattern in SIDECAR_GLOBS:
            for path in sorted(glob.glob(os.path.join(root, pattern))):
                name = os.path.basename(path).lower()
                if any(excl in name for excl in SIDECAR_NAME_EXCLUDES):
                    continue
                abs_path = os.path.abspath(path)
                if abs_path not in seen:
                    seen.add(abs_path)
                    found.append(abs_path)
    return found


def load_sidecar(path: str) -> dict[str, Any]:
    """Load a sidecar JSON file into a dictionary.

    Args:
        path: Path to the JSON sidecar.

    Returns:
        The parsed JSON object, or an empty dict when the file does not contain
        a JSON object (for example a top-level array).

    Raises:
        OSError: If the file cannot be read.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        log.warning("Sidecar %s is not a JSON object; ignoring its contents.", path)
        return {}
    return data


# ---------------------------------------------------------------------------
# Overlay
# ---------------------------------------------------------------------------
def _resolve_metadata_dict(metadata: Any) -> dict[str, Any] | None:
    """Return the mutable metadata mapping within an extraction result.

    ``extract_bids_metadata`` returns a plain ``dict`` for some sequences and a
    ``[dict, asl_context]`` pair for others. This returns the first ``dict`` to
    overlay onto, or ``None`` when no mapping is present.

    Args:
        metadata: The result of ``extract_bids_metadata``.

    Returns:
        The metadata mapping to mutate, or ``None``.
    """
    if isinstance(metadata, dict):
        return metadata
    if isinstance(metadata, (list, tuple)):
        for item in metadata:
            if isinstance(item, dict):
                return item
    return None


def apply_overrides(
    metadata: Any,
    sidecar: dict[str, Any],
    *,
    allowlist: set[str] | None = None,
    aliases: dict[str, str] | None = None,
    sidecar_path: str | None = None,
) -> tuple[Any, OverrideReport]:
    """Overlay a loaded sidecar onto extracted metadata in memory.

    The sidecar is authoritative: each field replaces the corresponding
    extracted value. Replacing a *differing* extracted value is recorded as a
    conflict (and logged at WARNING level) so nothing changes silently.

    Args:
        metadata: The extraction result to mutate in place. Either a ``dict`` or
            a ``[dict, asl_context]`` sequence.
        sidecar: Parsed sidecar fields to overlay.
        allowlist: When not ``None``, only these post-alias keys are overlaid;
            all other sidecar keys are skipped.
        aliases: Sidecar-to-internal key remapping. Defaults to
            :data:`FIELD_ALIASES`.
        sidecar_path: Path recorded on the returned report, for diagnostics.

    Returns:
        A ``(metadata, report)`` tuple. ``metadata`` is the same object passed
        in (mutated); ``report`` is an :class:`OverrideReport` describing the
        changes.
    """
    if aliases is None:
        aliases = FIELD_ALIASES

    report = OverrideReport(sidecar_path=sidecar_path)
    target = _resolve_metadata_dict(metadata)
    if target is None:
        log.warning("No metadata mapping found to overlay the sidecar onto; skipping.")
        return metadata, report

    for raw_key, new_value in sidecar.items():
        key = aliases.get(raw_key, raw_key)
        if key != raw_key:
            report.aliased.append((raw_key, key))

        if allowlist is not None and key not in allowlist:
            report.skipped.append(raw_key)
            continue

        if key in target:
            old_value = target[key]
            if old_value != new_value:
                report.conflicts.append((key, old_value, new_value))
                log.warning(
                    "Sidecar override: '%s' %r -> %r (DICOM-derived value replaced).",
                    key,
                    old_value,
                    new_value,
                )
        else:
            report.applied.append(key)

        target[key] = new_value

    return metadata, report


def apply_sidecar_overrides(
    metadata: Any,
    dicom_dir: str | None,
    *,
    allowlist: set[str] | None = OVERRIDE_ALLOWLIST,
) -> tuple[Any, OverrideReport]:
    """Discover a sidecar for a DICOM directory and overlay it onto metadata.

    Locates a sidecar next to ``dicom_dir`` (see :data:`SIDECAR_GLOBS` and
    :data:`SEARCH_PARENT`), loads it, and overlays it onto ``metadata`` in
    memory. When several sidecars are found the first (stable order) is applied
    and the rest are logged and ignored.

    Args:
        metadata: The extraction result to mutate in place.
        dicom_dir: Directory the DICOMs were read from. ``None`` or empty
            disables the overlay (no-op).
        allowlist: Optional post-alias key allowlist. Defaults to
            :data:`OVERRIDE_ALLOWLIST`.

    Returns:
        A ``(metadata, report)`` tuple, as described in :func:`apply_overrides`.
        When no sidecar is found, ``metadata`` is returned unchanged with an
        empty report.
    """
    report = OverrideReport()
    if not dicom_dir:
        return metadata, report

    sidecars = discover_sidecars(dicom_dir)
    if not sidecars:
        return metadata, report

    if len(sidecars) > 1:
        log.warning(
            "Multiple sidecar JSON files found for %s; applying '%s' and ignoring %s.",
            dicom_dir,
            sidecars[0],
            sidecars[1:],
        )

    sidecar = load_sidecar(sidecars[0])
    return apply_overrides(
        metadata, sidecar, allowlist=allowlist, sidecar_path=sidecars[0]
    )
