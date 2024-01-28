import json
import tempfile

import pandas as pd
import pytest
from pandas.api.types import is_string_dtype

from trelliscope import Trelliscope, utils
from trelliscope.metas import (
    CurrencyMeta,
    DateMeta,
    DatetimeMeta,
    FactorMeta,
    GeoMeta,
    GraphMeta,
    HrefMeta,
    NumberMeta,
    PanelMeta,
    StringMeta,
)
from trelliscope.panel_source import FilePanelSource
from trelliscope.panels import ImagePanel


def test_string_meta_init(iris_df):
    meta = StringMeta(varname="Species", label="label", tags=[])

    assert meta.type == "string"
    assert meta.varname == "Species"
    assert meta.filterable == True
    assert meta.sortable == True
    assert meta.label == "label"
    assert type(meta.tags) == list

    meta.check_variable(iris_df)

    # This is expected behavior. Even though the column is an integer
    # if the user wants to explicitly put a StringMeta, we allow that because
    # it can be easily coerced.
    meta.varname = "Sepal.Length"
    meta.check_variable(iris_df)


def test_number_meta_init(iris_df):
    number_meta = NumberMeta("Sepal.Length")
    assert number_meta.type == "number"
    assert number_meta.varname == "Sepal.Length"
    assert number_meta.filterable == True
    assert number_meta.sortable == True
    assert number_meta.label is None
    assert number_meta.tags == []

    number_meta.check_variable(iris_df)


def test_number_meta_with_string(iris_df):
    number_meta = NumberMeta("Species")
    assert number_meta.type == "number"
    assert number_meta.varname == "Species"
    assert number_meta.filterable == True
    assert number_meta.sortable == True
    assert number_meta.label == None
    assert number_meta.tags == []

    with pytest.raises(ValueError):
        number_meta.check_variable(iris_df)


def test_check_varname(iris_df):
    meta = NumberMeta("Sepal.Length", tags="stuff")
    meta.check_with_data(iris_df)

    meta.varname = "abcdef"
    with pytest.raises(ValueError):
        meta.check_with_data(iris_df)


def test_check_with_data(iris_df):
    meta = NumberMeta("Sepal.Length", tags="stuff")

    # This should not cause an exception
    meta.check_with_data(iris_df)

    meta.varname = "abcdef"
    with pytest.raises(ValueError):
        # Now an exception should be raised
        meta.check_with_data(iris_df)

    meta.varname = "Species"
    with pytest.raises(ValueError):
        # Now an exception should be raised
        meta.check_with_data(iris_df)

    meta.varname = "Sepal.Length"

    meta.check_variable(iris_df)


def test_number_meta(iris_df):
    meta = NumberMeta("Sepal.Length", tags="stuff")

    meta.check_with_data(iris_df)

    assert meta.tags == ["stuff"]

    actual_json = meta.to_json()
    expected_json = '{"locale":true,"digits":null,"sortable":true,"filterable":true,"tags":["stuff"],"label":"Sepal.Length","type":"number","varname":"Sepal.Length"}'
    assert json.loads(actual_json) == json.loads(expected_json)

    meta = NumberMeta("Sepal.Length", label="Sepal length of the iris")
    assert meta.label == "Sepal length of the iris"

    meta = NumberMeta("whatever", digits=2, locale=False)
    assert meta.digits == 2
    assert meta.locale == False

    with pytest.raises(ValueError, match=r"Could not find variable"):
        meta.check_with_data(iris_df)

    meta = NumberMeta("Species")
    with pytest.raises(ValueError, match=r"must be numeric"):
        meta.check_with_data(iris_df)

    with pytest.raises(TypeError, match=r"must be an integer"):
        meta = NumberMeta("Sepal.Length", digits="a")

    with pytest.raises(TypeError, match=r"must be logical"):
        meta = NumberMeta("Sepal.Length", locale="a")


def test_currency_meta(iris_df):
    meta = CurrencyMeta(
        "Sepal.Length", label="Sepal length of the iris", tags="a tag", code="EUR"
    )
    assert meta.varname == "Sepal.Length"
    assert meta.label == "Sepal length of the iris"
    assert meta.tags == ["a tag"]
    assert meta.code == "EUR"


def test_currency_meta(iris_df):
    meta = CurrencyMeta("Sepal.Length", tags="stuff")

    meta.check_with_data(iris_df)
    assert meta.tags == ["stuff"]

    actual_json = meta.to_json(pretty=False)
    expected_json = '{"code":"USD","sortable":true,"filterable":true,"tags":["stuff"],"label":"Sepal.Length","type":"currency","varname":"Sepal.Length"}'
    assert json.loads(actual_json) == json.loads(expected_json)

    meta2 = CurrencyMeta("Sepal.Length", label="Sepal length of the iris")
    assert meta2.varname == "Sepal.Length"
    assert meta2.label == "Sepal length of the iris"

    meta3 = CurrencyMeta("whatever")
    with pytest.raises(ValueError, match=r"Could not find variable"):
        meta3.check_with_data(iris_df)

    meta4 = CurrencyMeta("Species")
    with pytest.raises(ValueError, match=r"must be numeric"):
        meta4.check_with_data(iris_df)

    with pytest.raises(ValueError, match=r"must be one of"):
        meta5 = CurrencyMeta("Sepal.Length", code="ASD")


def test_string_meta(iris_df):
    meta = StringMeta("Species")
    meta.check_with_data(iris_df)

    # For the following test, even though Sepal.Length is NOT a string
    # this should work, because this type can be easily coerced to a string.
    # So if the user has explicitly used a StringMeta and it can work,
    # we should let it work.
    meta2 = StringMeta("Sepal.Length")
    meta2.check_with_data(iris_df)

    assert not is_string_dtype(iris_df["Sepal.Length"])
    new_df = meta2.cast_variable(iris_df)

    # verify changed in the returned value
    assert is_string_dtype(new_df["Sepal.Length"])

    # verify changed in the original df
    # NOTE: This may be a "feature" that is altered in the future
    # to make it so the original data frame is left unchanged
    assert is_string_dtype(iris_df["Sepal.Length"])


def test_factor_meta(iris_df):
    # Try a case where we don't specify the levels but they get inferred
    meta = FactorMeta("Species")
    meta.check_with_data(iris_df)
    assert set(meta.levels) == set(["setosa", "virginica", "versicolor"])

    # Try a case where the levels don't contain all the data (Error)
    meta2 = FactorMeta("Species", levels=["setosa", "virginica"])
    with pytest.raises(ValueError, match=r"contains values not specified"):
        meta2.check_with_data(iris_df)

    # Try a case where the levels have extra items (this is ok)
    meta3 = FactorMeta("Species", levels=["setosa", "virginica", "versicolor", "stuff"])
    meta3.check_with_data(iris_df)

    # Try a case where the levels variable is are not a list
    with pytest.raises(ValueError, match="to be a list"):
        meta4 = FactorMeta("Species", levels="this is a string")


def test_date_meta(iris_plus_df: pd.DataFrame):
    meta = DateMeta("date")
    meta.check_with_data(iris_plus_df)


def test_datetime_meta(iris_plus_df):
    meta = DatetimeMeta("datetime")
    meta.check_with_data(iris_plus_df)

    # The value is not a dt yet
    assert not utils.is_datetime_column(
        iris_plus_df["datetime"], must_be_datetime_objects=True
    )

    df2 = meta.cast_variable(iris_plus_df)

    # The original df is changed
    assert utils.is_datetime_column(
        iris_plus_df["datetime"], must_be_datetime_objects=True
    )
    assert utils.is_datetime_column(df2["datetime"], must_be_datetime_objects=False)


def test_geo_meta(iris_plus_df):
    meta = GeoMeta("coords", latvar="lat", longvar="long")
    meta.check_with_data(iris_plus_df)


@pytest.mark.skip("Feature is not implemented yet")
def test_graph_meta(iris_plus_df):
    # TODO: The iris_plus_df will need to have extra columns added for this

    meta = GraphMeta("lst", "id", "to")
    meta.check_with_data(iris_plus_df)


def test_href_meta(iris_plus_df):
    # First use a proper href category
    meta = HrefMeta("href")
    meta.check_with_data(iris_plus_df)

    # Try a numeric category (error)
    meta2 = HrefMeta("Sepal.Length")
    with pytest.raises(ValueError, match="Data type is not a string"):
        meta2.check_with_data(iris_plus_df)


def test_panel_meta(iris_df_no_duplicates: pd.DataFrame):
    iris_df = iris_df_no_duplicates

    with tempfile.TemporaryDirectory() as temp_dir_name:
        # this is test code that just sets all images to this test_image.png string
        # it is not a proper use of the images, but gives us something to use in testing.
        iris_df["img_panel"] = "test_image.png"

        pnl = ImagePanel(
            "img_panel",
            source=FilePanelSource(is_local=True),
            aspect_ratio=1.5,
            should_copy_to_output=False,
        )

        tr = Trelliscope(iris_df, "Iris", path=temp_dir_name).add_panel(pnl)

        meta = PanelMeta(pnl, "img_panel")

        meta.check_with_data(iris_df)

        actual_json = meta.to_json(pretty=False)
        expected_json = """
        {
            "source": {
                "isLocal": true,
                "type": "file"
            },
            "aspect": 1.5,
            "paneltype": "img",
            "sortable": false,
            "filterable": false,
            "tags": [],
            "label": "img_panel",
            "type": "panel",
            "varname": "img_panel"
            }"""

        assert json.loads(actual_json) == json.loads(expected_json)
