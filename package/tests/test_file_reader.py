"""Tests for FileReader TSV parsing (aslcontext volume types)."""

from __future__ import annotations

from pathlib import Path

from pyaslreport.io.readers.file_reader import FileReader


class TestReadTsv:
    """Reading a single-column aslcontext.tsv into volume-type tokens."""

    def test_strips_surrounding_quotes(self, tmp_path: Path) -> None:
        """Quoted values are unwrapped so downstream matching works."""
        path = tmp_path / "_aslcontext.tsv"
        path.write_text('volume_type\n"deltam"\n"m0scan"\n', encoding="utf-8")

        assert FileReader.read(str(path)) == ["deltam", "m0scan"]

    def test_unquoted_values_unchanged(self, tmp_path: Path) -> None:
        """Standard unquoted BIDS values pass through untouched."""
        path = tmp_path / "_aslcontext.tsv"
        path.write_text("volume_type\ncontrol\nlabel\n", encoding="utf-8")

        assert FileReader.read(str(path)) == ["control", "label"]
