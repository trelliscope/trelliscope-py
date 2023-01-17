from trelliscope.metas import Meta, NumberMeta, StringMeta
#from sklearn.datasets import load_iris
import pandas as pd
import pytest
import json

def test_string_meta_init(iris_df):
    #iris_df = get_iris_dataset()
    meta = StringMeta(varname="Species", label="label", tags=[])
    
    assert meta.type == "string"
    assert meta.varname == "Species"
    assert meta.filterable == True
    assert meta.sortable == False
    assert meta.label == "label"
    assert type(meta.tags) == list

    meta.check_variable(iris_df)

    meta.varname = "Sepal.Length"
    with pytest.raises(ValueError):
        meta.check_variable(iris_df)

def test_number_meta_init(iris_df):
    #iris_df = get_iris_dataset()

    number_meta = NumberMeta("Sepal.Length")
    assert number_meta.type == "number"
    assert number_meta.varname == "Sepal.Length"
    assert number_meta.filterable == True
    assert number_meta.sortable == True
    assert number_meta.label is "Sepal.Length"
    assert number_meta.tags == []

    number_meta.check_variable(iris_df)

def test_number_meta_with_string(iris_df):
    #iris_df = get_iris_dataset()

    number_meta = NumberMeta("Species")
    assert number_meta.type == "number"
    assert number_meta.varname == "Species"
    assert number_meta.filterable == True
    assert number_meta.sortable == True
    assert number_meta.label == "Species"
    assert number_meta.tags == []

    with pytest.raises(ValueError):
        number_meta.check_variable(iris_df)

def test_check_varname(iris_df):
    #iris_df = get_iris_dataset()

    meta = NumberMeta("Sepal.Length", tags="stuff")
    meta.check_with_data(iris_df)

    meta.varname = "abcdef"
    with pytest.raises(ValueError):
        meta.check_with_data(iris_df)

def test_check_with_data(iris_df):
    #iris_df = get_iris_dataset()

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
    #iris_df = get_iris_dataset()

    meta = NumberMeta("Sepal.Length", tags="stuff")

    # TODO: verify this is expected behavior
    assert meta.label == "Sepal.Length"

    meta.check_with_data(iris_df)

    assert meta.tags == ["stuff"]

    actual_json = json.loads(meta.to_json())
    expected_json = json.loads('{"locale":true,"digits":null,"sortable":true,"filterable":true,"tags":["stuff"],"label":"Sepal.Length","type":"number","varname":"Sepal.Length"}')
    assert actual_json == expected_json

    meta = NumberMeta("Sepal.Length", label="Sepal length of the iris")
    assert meta.label == "Sepal length of the iris"

    meta = NumberMeta("whatever", digits = 2, locale = False)
    assert meta.digits == 2
    assert meta.locale == False

    with pytest.raises(ValueError) as ex:
        meta.check_with_data(iris_df)
    assert ex.match("Could not find variable")

    with pytest.raises(ValueError) as ex:
        meta = NumberMeta("Species")
        meta.check_with_data(iris_df)
    assert ex.match("must be numeric")

    with pytest.raises(TypeError) as ex:
        meta = NumberMeta("Sepal.Length", digits = "a")
    assert ex.match("must be an integer")

    with pytest.raises(TypeError) as ex:
        meta = NumberMeta("Sepal.Length", locale = "a")
    assert ex.match("must be logical")

    ######
    ### TODO: 1/16 Pick up here.
    ### 1. Build out tests for additional meta types
    ### 2. Check for regular expression terms in expected exceptions.
    ### 3. Document dependencies (both in writing and in requirements.txt file)
    ###    pytest
    ###    pandas
    ###    statsmodels
    ####


