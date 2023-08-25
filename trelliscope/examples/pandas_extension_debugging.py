import pandas as pd


class SubclassedSeries(pd.Series):
    # normal properties
    _metadata = ["added_property"]

    @property
    def _constructor(self):
        def f(*args, **kwargs):
            # workaround for https://github.com/pandas-dev/pandas/issues/13208
            return SubclassedSeries(*args, **kwargs).__finalize__(self)
        return f

    @property
    def _constructor_expanddim(self):
        def f(*args, **kwargs):
            # workaround for https://github.com/pandas-dev/pandas/issues/13208
            return SubclassedDataFrame(*args, **kwargs).__finalize__(self)
        return f
        # return SubclassedDataFrame


class SubclassedDataFrame(pd.DataFrame):
    # # normal properties
    _metadata = ["added_property"]

    @property
    def _constructor(self):
        def f(*args, **kwargs):
            # workaround for https://github.com/pandas-dev/pandas/issues/13208
            return SubclassedDataFrame(*args, **kwargs).__finalize__(self)
        return f
        # return SubclassedDataFrame

    @property
    def _constructor_sliced(self, *args, **kwargs):
        def f(*args, **kwargs):
            # workaround for https://github.com/pandas-dev/pandas/issues/13208
            print(kwargs)
            x = SubclassedSeries(*args, **kwargs)
            return x.__finalize__(x)
        return f
        # return SubclassedSeries


df = SubclassedDataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

# df.added_property = "test"
# df["A"].added_property = "test2"

s = pd.Series([1, 2, 3])
s.added_property = "test3"
df["D"] = s

print(s.added_property)
print(df["D"].added_property)

print(df["D"])

# print(df.added_property)
# print(df[["A", "B"]].added_property)

#print(df["A"].added_property)


