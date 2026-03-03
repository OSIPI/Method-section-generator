import pytest
from pyaslreport.modalities.registry import (
    register_modality,
    get_processor,
    MODALITY_REGISTRY,
)


class DummyProcessor:
    pass


def test_register_and_get_processor():
    register_modality("test_modality", processor_cls=DummyProcessor)

    processor = get_processor("test_modality")
    assert processor == DummyProcessor


def test_get_unknown_processor_raises():
    with pytest.raises(KeyError):
        get_processor("unknown_modality")