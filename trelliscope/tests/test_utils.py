import pytest

from trelliscope import utils

def test_sanitize():
    actual = utils.sanitize("abc def")
    assert actual == "abc_def"

    actual = utils.sanitize("ABC def")
    assert actual == "abc_def"

    actual = utils.sanitize("ABC def", False)
    assert actual == "ABC_def"

    actual = utils.sanitize("abc?:/!@#$%^&*()<>,;:'\"|\\{}~`def")
    assert actual == "abcdef"

def test_get_jsonp_wrap_text_dict():
    json_dict = utils.get_jsonp_wrap_text_dict(False, "__abc_123")
    assert json_dict == {"start": "", "end": ""}

    jsonp_dict = utils.get_jsonp_wrap_text_dict(True, "__abc_123")
    assert jsonp_dict == {"start": "__abc_123(", "end": ")"}


