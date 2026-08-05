import pytest
from pyaslreport.enums.modality_enum import ModalityTypeValues


def test_enum_values():
    assert ModalityTypeValues.ASL.value == "ASL"
    assert ModalityTypeValues.DCE.value == "DCE"
    assert ModalityTypeValues.DSC.value == "DSC"


def test_invalid_enum_raises():
    with pytest.raises(ValueError):
        ModalityTypeValues("INVALID")