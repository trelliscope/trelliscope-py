from trelliscope.metas import Meta, NumberMeta, StringMeta
from fruit import get_fruit_data_frame

# from sklearn.datasets import load_iris
import pandas as pd

import statsmodels.api as sm
#import seaborn as sns

import pytest
import ssl


def main():
    m = Meta("str", "name", True, True)
    print(m.to_json())

    number_meta = NumberMeta("size")
    print(number_meta.to_json())

    fruit_df = get_fruit_data_frame()
    number_meta.check_variable(fruit_df)

    string_meta = StringMeta("name")
    print(string_meta.to_json())
    string_meta.check_variable(fruit_df)

    # iris = load_iris(as_frame=True)
    # df = iris["frame"]
    # print(df)
    # print(df.columns)
    # print(df.dtypes)

    # Python on macOS needs to have certificates installed.
    # This can be done in the OS, or we can allow unsafe certificates.
    # See: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    ssl._create_default_https_context = ssl._create_unverified_context
    iris = sm.datasets.get_rdataset('iris').data


    # iris = sns.load_dataset('iris')
    print(iris)
    print(iris.dtypes)

if __name__ == "__main__":
    main()
