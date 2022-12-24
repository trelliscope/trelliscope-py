from trelliscope.metas import Meta, NumberMeta, StringMeta
#from sklearn.datasets import load_iris
import statsmodels.api as sm
import pandas as pd
import pytest

import ssl

def test_meta_init():
    meta = Meta(type="string", varname="name", filterable=True,
        sortable=True, label="label", tags=[])
    
    assert meta.type == "string"
    assert meta.varname == "name"
    assert meta.filterable == True
    assert meta.sortable == True
    assert meta.label == "label"
    assert type(meta.tags) == list

def test_number_meta_init():
    # iris = load_iris(as_frame=True)
    # iris_df = iris["frame"]


    # Python on macOS needs to have certificates installed.
    # This can be done in the OS, or we can allow unsafe certificates.
    # See: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    ssl._create_default_https_context = ssl._create_unverified_context
    iris_df = sm.datasets.get_rdataset('iris').data


    number_meta = NumberMeta("Sepal.Length")
    assert number_meta.type == "number"
    assert number_meta.varname == "Sepal.Length"
    assert number_meta.filterable == True
    assert number_meta.sortable == True
    assert number_meta.label is None
    assert number_meta.tags == []

    number_meta.check_variable(iris_df)

    # print(number_meta.to_json())

    # fruit_df = get_fruit_data_frame()
    # number_meta.check_variable(fruit_df)


    # assert meta.type == "string"
    # assert meta.varname == "name"
    # assert meta.filterable == True
    # assert meta.sortable == True
    # assert meta.label == "label"
    # assert type(meta.tags) == list

def test_number_meta_with_string():
    # Python on macOS needs to have certificates installed.
    # This can be done in the OS, or we can allow unsafe certificates.
    # See: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    ssl._create_default_https_context = ssl._create_unverified_context
    iris_df = sm.datasets.get_rdataset('iris').data


    number_meta = NumberMeta("Species")
    assert number_meta.type == "number"
    assert number_meta.varname == "Species"
    assert number_meta.filterable == True
    assert number_meta.sortable == True
    assert number_meta.label is None
    assert number_meta.tags == []

    with pytest.raises(ValueError):
        number_meta.check_variable(iris_df)


    ######
    ### TODO: Pick up here.
    ### 1. Add a common, pre-test, section to get datasets
    ### 2. Look at the R unit tests and follow them
    ### 3. Document dependencies (both in writing and in requirements.txt file)
    ###    pytest
    ###    pandas
    ###    statsmodels
    ####


