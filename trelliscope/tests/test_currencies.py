from trelliscope.currencies import get_valid_currencies


def test_currency_list():
    valid_list = get_valid_currencies()
    minimum_expected_values = 11
    assert len(valid_list) >= minimum_expected_values
    assert "USD" in valid_list
    assert "EUR" in valid_list
    assert "ASD" not in valid_list
