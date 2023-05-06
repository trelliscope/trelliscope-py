import pytest
import os
import tempfile
import re
import pandas as pd
from trelliscope import utils


def get_error_message(text: str):
    return f"error text contains {text}"

def test_check_int():
    utils.check_int(3, "the var", get_error_message)
    utils.check_int(0, "the var", get_error_message)
    utils.check_int(-3, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be an integer"):
        utils.check_int(3.6, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be an integer"):
        utils.check_int([3], "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be an integer"):
        utils.check_int("stuff", "the var", get_error_message)

def test_check_bool():
    utils.check_bool(True, "the var", get_error_message)
    utils.check_bool(False, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a boolean"):
        utils.check_bool(3, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a boolean"):
        utils.check_bool(3.6, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a boolean"):
        utils.check_bool([3], "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a boolean"):
        utils.check_bool("stuff", "the var", get_error_message)

def test_check_scalar(iris_df:pd.DataFrame):
    utils.check_scalar(3, "the var", get_error_message)
    utils.check_scalar(0, "the var", get_error_message)
    utils.check_scalar(-3, "the var", get_error_message)
    utils.check_scalar(3.6, "the var", get_error_message)
    utils.check_scalar("stuff", "the var", get_error_message)
    utils.check_scalar("more stuff", "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar([3], "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar([3, 6], "the var", get_error_message)

    # We are not going to check (3), because python will automatically
    # unwrap this to be a single scalar value.

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar((3, 6), "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar({3}, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar({3, 6}, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar({"k":3}, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar({"a":3, "b":6}, "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar(iris_df["Sepal.Length"], "the var", get_error_message)

    with pytest.raises(TypeError, match=r"the var.*must be a scalar"):
        utils.check_scalar(iris_df, "the var", get_error_message)

def test_check_enum():
    utils.check_enum("trucks", ["cars", "trucks", "bikes"], get_error_message)

    with pytest.raises(ValueError, match="must be one of"):
        utils.check_enum("planes", ["cars", "trucks", "bikes"], get_error_message)

def test_check_is_list():
    utils.check_is_list(["a", "b", "c"], get_error_message)

    with pytest.raises(ValueError, match=r"Expected value .+ to be a list"):
        utils.check_is_list("a", get_error_message)

def test_check_has_variable(iris_df):
    utils.check_has_variable(iris_df, "Sepal.Length", get_error_message)

    with pytest.raises(ValueError, match="Could not find variable"):
        utils.check_has_variable(iris_df, "stuff", get_error_message)

def test_check_numeric(iris_df):
    utils.check_numeric(iris_df, "Sepal.Length", get_error_message)

    with pytest.raises(ValueError, match="must be numeric"):
        utils.check_numeric(iris_df, "Species", get_error_message)

def test_check_range(iris_df):
    utils.check_range(iris_df, "Sepal.Length", 0, 10, get_error_message)

    with pytest.raises(ValueError, match="must be in the range"):
        utils.check_range(iris_df, "Sepal.Length", 11, 15, get_error_message)

    with pytest.raises(ValueError, match="must be in the range"):
        utils.check_range(iris_df, "Sepal.Length", 0, 0.5, get_error_message)

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

def test_get_file_path():
    # TODO: Verify this path test works on windows...
    jsonp_path = utils.get_file_path("/test1/test2", "file", True)
    assert jsonp_path == "/test1/test2/file.jsonp"

    json_path = utils.get_file_path("/test1/test2", "file", False)
    assert json_path == "/test1/test2/file.json"

def test_read_jsonp():
    # From https://stackoverflow.com/a/8577226
    # using tempfile in a standard with block doesn't allow a second open
    # on Windows, hence the more complicated way here.
    
    content = """__loadAppConfig__07e09065({
        "name": "Trelliscope App",
        "data_type": "jsonp",
        "id": "07e09065"
        })"""
    
    # Note the suffix here is jsonp not json
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonp")
    try:
        tmp.write(content.encode("utf8"))
        tmp.close()
        dict = utils.read_jsonp(tmp.name)

        assert dict == {"name": "Trelliscope App",
                        "data_type": "jsonp",
                        "id": "07e09065"
                        }
    finally:
        tmp.close()
        os.unlink(tmp.name)

def test_read_jsonp_with_json():
    # From https://stackoverflow.com/a/8577226
    # using tempfile in a standard with block doesn't allow a second open
    # on Windows, hence the more complicated way here.
    
    content = """{
        "name": "Trelliscope App",
        "data_type": "jsonp",
        "id": "07e09065"
        }"""
    
    # Note the suffix here is json not jsonp
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    try:
        tmp.write(content.encode("utf8"))
        tmp.close()
        dict = utils.read_jsonp(tmp.name)

        assert dict == {"name": "Trelliscope App",
                        "data_type": "jsonp",
                        "id": "07e09065"
                        }
    finally:
        tmp.close()
        os.unlink(tmp.name)

def test_write_jsonp():
    # From https://stackoverflow.com/a/8577226
    # using tempfile in a standard with block doesn't allow a second open
    # on Windows, hence the more complicated way here.
    
    content = """{
        "name": "Trelliscope App",
        "data_type": "jsonp",
        "id": "07e09065"
        }"""

    expected_jsonp = """__abc_123(
        {
        "name": "Trelliscope App",
        "data_type": "jsonp",
        "id": "07e09065"
        })"""


    # Note the suffix here is jsonp not json
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonp")
    try:
        utils.write_json_file(tmp.name, True, "__abc_123", content)

        with open(tmp.name) as file:
            actual_content = file.read()

        actual_cleaned = re.sub(r"\s", "", actual_content)
        expected_cleaned = re.sub(r"\s", "", expected_jsonp)

        assert actual_cleaned == expected_cleaned

    finally:
        tmp.close()
        os.unlink(tmp.name)

def test_write_jsonp_with_json():
    # From https://stackoverflow.com/a/8577226
    # using tempfile in a standard with block doesn't allow a second open
    # on Windows, hence the more complicated way here.
    
    content = """{
        "name": "Trelliscope App",
        "data_type": "jsonp",
        "id": "07e09065"
        }"""

    # Note the suffix here is json not jsonp
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    try:
        utils.write_json_file(tmp.name, False, "__abc_123", content)

        with open(tmp.name) as file:
            actual_content = file.read()

        actual_cleaned = re.sub(r"\s", "", actual_content)
        expected_cleaned = re.sub(r"\s", "", content)

        assert actual_cleaned == expected_cleaned

    finally:
        tmp.close()
        os.unlink(tmp.name)

def test_check_image_extension():
    files = ["a.jpg", "b.png", "c.svg"]
    utils.check_image_extension(files)

    files.append("/a/b.c/d.gif")
    utils.check_image_extension(files)

    files.append("bad.docx")
    with pytest.raises(ValueError, match=r"All file extensions must be one of"):
        utils.check_image_extension(files)

def test_check_positive_numeric():
    utils.check_positive_numeric(1, "x")
    utils.check_positive_numeric(1000000, "x")
    utils.check_positive_numeric(3.6, "x")
    utils.check_positive_numeric(0.000001, "x")

    with pytest.raises(ValueError, match=r"must be a positive number"):
        utils.check_positive_numeric("stuff", "x")

    with pytest.raises(ValueError, match=r"must be a positive number"):
        utils.check_positive_numeric(-3, "x")

def test_is_all_remote_with_local(mars_df:pd.DataFrame):
    assert utils.is_all_remote(mars_df["img_src"])

    # Change one to not be remote
    mars_df["img_src"][0] = "local.png"
    assert not utils.is_all_remote(mars_df["img_src"])

def test_extension_matches():
    text = "file.png"
    assert utils._extension_matches(text, "png")
    assert not utils._extension_matches(text, "jpg")
    assert not utils._extension_matches(text, "doc")
    assert not utils._extension_matches(text, "")

    text = "file"
    assert not utils._extension_matches(text, "png")
    assert not utils._extension_matches(text, "jpg")
    assert not utils._extension_matches(text, "doc")
    assert  utils._extension_matches(text, "")

    text = "file.jpg"
    assert not utils._extension_matches(text, "png")
    assert utils._extension_matches(text, "jpg")
    assert not utils._extension_matches(text, "doc")
    assert not utils._extension_matches(text, "")

def test_extension_matches_match_case():
    text = "file.png"
    assert utils._extension_matches(text, "png")
    
    assert utils._extension_matches(text, "PNG") # uses default value
    assert utils._extension_matches(text, "PNG", False)
    assert not utils._extension_matches(text, "PNG", True)

def test_find_image_columns(mars_df:pd.DataFrame):
    cols = utils.find_image_columns(mars_df)
    assert len(cols) == 1
    assert cols[0] == "img_src"

    # Try changing the extension of one image and make
    # sure it is no longer a valid column
    mars_df["img_src"][0] = "test.doc"
    cols = utils.find_image_columns(mars_df)
    assert len(cols) == 0

    # Try changing the extension of one image
    # to another (but different) image extension
    # and make sure it is no longer a valid column
    mars_df["img_src"][0] = "test.png"
    cols = utils.find_image_columns(mars_df)
    assert len(cols) == 0


