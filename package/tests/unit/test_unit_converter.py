from pyaslreport.utils.unit_conversion_utils import UnitConverterUtils


def test_convert_single_value_to_milliseconds():
    assert UnitConverterUtils.convert_to_milliseconds(1) == 1000
    assert UnitConverterUtils.convert_to_milliseconds(0.5) == 500


def test_convert_list_to_milliseconds():
    result = UnitConverterUtils.convert_to_milliseconds([1, 0.5])
    assert result == [1000, 500]


def test_convert_milliseconds_to_seconds():
    assert UnitConverterUtils.convert_milliseconds_to_seconds(1000) == 1.0
    assert UnitConverterUtils.convert_milliseconds_to_seconds([2000, 500]) == [2.0, 0.5]


def test_invalid_input_raises_type_error():
    try:
        UnitConverterUtils.convert_to_milliseconds("invalid")
    except TypeError:
        assert True
    else:
        assert False