#    Copyright 2022 @jack-tee
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import abc
import json
import logging
import random
import string
from dataclasses import dataclass, field
from decimal import Decimal
from itertools import chain, zip_longest
from typing import List, Optional

import numpy as np
import pandas as pd

pandas_type_mapping = {
    "Int": "Int64",
    "String": "string",
    "Float": "float64",
    "Decimal": "float",
    "Timestamp": "datetime64[ns]",
    "TimestampAsInt": "Int64",
    "Bool": "bool",
    "Date": "object",
}


@dataclass(kw_only=True)
class Column(abc.ABC):
    id: str = ""
    name: str
    column_type: str
    data_type: str = None
    output_type: Optional[str] = None
    null_percentage: int = 0
    decimal_places: int = 4
    date_format: str = "%Y-%m-%d %H:%M:%S"

    def maybe_add_column(self, df: pd.DataFrame) -> None:
        try:
            self.add_column(df)
            self.post_process(df)
        except Exception as e:
            raise ColumnGenerationException(
                f"Error on column [{self.name}]. Caused by: {e}.")

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = self.generate(len(df))

    def post_process(self, df: pd.DataFrame) -> None:
        
        if self.null_percentage > 0:
            nanidx = df.sample(frac=self.null_percentage / 100).index
            df.loc[nanidx,self.name] = np.nan 

        match self.data_type:
            case None:
                pass
            case 'Decimal':
                df[self.name] = df[self.name][df[self.name].notnull()] \
                                    .round(decimals=self.decimal_places) \
                                    .astype("string") \
                                    .apply(lambda v: Decimal(v)) \
                                    .astype("object")
            case _:
                pandas_type = self.pandas_type()
                if pandas_type is None:
                    logging.warning(f"column: [{self.name}] -> data_type [{self.data_type}] not recognised, ignoring.")
                else:
                    df[self.name] = df[self.name].astype(self.pandas_type())

        match self.output_type:
            case None:
                pass
            case 'String':
                if df[self.name].dtype == 'datetime64[ns]':
                    df[self.name] = df[self.name].dt.strftime(self.date_format).astype('string')
                else:
                    df[self.name] = df[self.name].astype(pandas_type_mapping[self.output_type])
            case _:
                raise Exception(f"output_type: [{self.output_type}] not recognised")

    def generate(self, rows: int) -> pd.Series:
        raise NotImplementedError("Subclasses of Column should implement either `generate` or `add_column`")

    def pandas_type(self) -> str | None:
        if self.data_type:
            return pandas_type_mapping.get(self.data_type)
        return None


@dataclass(kw_only=True)
class Fixed(Column):
    """
    A column filled with a single fixed `value:`.

    Fixed supports the following `data_types:` - Int, Bool, Float, Decimal, String and Timestamp.

    **Usage:**
    ```
    - name: my_fixed_col
      column_type: Fixed
      data_type: String
      value: banana
    ```

    **Concise syntax:**
    ```
    - col: my_fixed_col Fixed String banana
    ```
    """

    value: any

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int':
                return pd.Series(np.full(rows, self.value)).astype('float64').astype(self.pandas_type())
            case 'Bool':
                return pd.Series(np.full(rows, bool(self.value)), dtype=self.pandas_type())
            case _:
                return pd.Series(np.full(rows, self.value), dtype=self.pandas_type())


@dataclass(kw_only=True)
class Empty(Column):
    """
    An empty column.

    """
    def add_column(self, df: pd.DataFrame):
        df[self.name] = pd.Series(np.full(len(df), np.nan), dtype=self.pandas_type())


@dataclass(kw_only=True)
class MapValues(Column):
    """
    A maps the `source_column:` values to the output column.
    
    MapValues supports the following `data_types:` - Int, Bool, Float, Decimal, String and Timestamp.

    **Usage:**
    ```
    - col: currency Selection String
      values:
        - EUR
        - GBP
        - USD

    - name: currency_symbol
      column_type: MapValues
      source_column: currency
      values:
        EUR: €
        GBP: £
    ```

    **Concise syntax:**
    ```
    - col: my_fixed_col Fixed String banana
    ```

    Required params:
    - `source_column:` the column to base on
    - `values:` the mapping to use

    Optional params:
    - `default:` the output value to use for source values that don't exist in `values`

    """
    source_column: str
    values: dict
    default: any = np.nan

    def add_column(self, df: pd.DataFrame):
        df[self.name] = df[self.source_column].map(self.values).fillna(self.default)



unit_factor = {
    's' :1E9,
    'ms':1E6,
    'us':1E3,
    'ns':1
}

@dataclass(kw_only=True)
class Random(Column):
    """
    Generates a column of values uniformly between `min:` and `max:`.
    Random supports the following `data_types:` - Int, Bool, Float, Decimal, String, Timestamp and TimestampAsInt.

    **Usage:**
    ```
    - name: my_random_col
      column_type: Random
      data_type: Decimal
      min: 1000
      max: 5000
    ```

    **Concise syntax:**
    ```
    - col: my_random_col Random Timestamp "2022-01-01 12:00:00" 2022-04-05
      time_unit: us
    ```

    Required params:
    - `min:` the lower bound
    - `max:` the uppper bound

    Optional params:
    - `decimal_places:` applies to Decimal and Float, rounds the output values to the specified decimal places, default 4.
    - `time_unit:` one of 's', 'ms', 'us', 'ns'. Applies to Timestamp and TimestampAsInt, controls the resolution of the resulting Timestamps or Ints, default is 'ms'.
    - `str_max_chars:` when using the String data_type this column will generate random strings of length between min and max. This value provides an extra limit on how long the strings can be. It exists to prevent enormous strings being generated accidently. Default limit is 5000.
    """

    data_type: str = "Int"
    min: any = 0
    max: any = 1
    str_max_chars: int = 5000
    time_unit: str = 'ms'

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int' | 'Bool':
                return pd.Series(np.random.randint(int(self.min), int(self.max)+1, rows), dtype=self.pandas_type())

            case 'Float' | 'Decimal':
                return pd.Series(np.random.uniform(float(self.min), float(self.max)+1, rows)
                                          .round(decimals=self.decimal_places),
                                 dtype=self.pandas_type())

            case 'String':
                # limit how long strings can be
                self.min = min(int(self.min), self.str_max_chars)
                self.max = min(int(self.max), self.str_max_chars)
                return pd.Series(list(''.join(random.choices(string.ascii_letters, k=random.randint(self.min, self.max))) for _ in range(rows)), dtype=self.pandas_type())

            case 'Timestamp':
                date_ints_series = self.random_date_ints(self.min, self.max, rows, self.time_unit)
                return pd.to_datetime(date_ints_series, unit=self.time_unit)

            case 'TimestampAsInt':
                date_ints_series = self.random_date_ints(self.min, self.max, rows, self.time_unit)
                return date_ints_series

            case _:
                raise ColumnGenerationException(f"Data type [{self.data_type}] not recognised")


    def random_date_ints(self, start, end, rows, unit='ms'):
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        return pd.Series(np.random.uniform(start.value // unit_factor[unit], end.value // unit_factor[unit], rows)).astype(int)


@dataclass(kw_only=True)
class Selection(Column):
    """
    Generates a column by randomly selecting from a list of `values:`.

    Random supports the following `data_types:` - Int, Bool, Float, Decimal, String and Timestamp.

    **Usage:**
    ```
    - name: my_selection_col
      column_type: Selection
      data_type: String
      values:
        - foo
        - bar
        - baz
      weights:
        - 10
        - 2
    ```

    **Concise syntax:**
    ```
    - col: my_selection_col Selection Int
      values:
        - 0
        - 10
        - 100
    ```

    Required params:
    - `values:` the list of values to pick from, if the Bool `data_type` is specified then `values` is automatically set to [True, False].

    Optional params:
    - `weights:` increases the likelyhood that certain `values` will be selected. Weights are applied in the same order as the list of `values`. All `values` are assigned a weight of 1 by default so only differing weights need to be specified.

    """
    

    values: List[any] = field(default_factory=list)
    #source_columns: List[any] = field(default_factory=list)
    weights: List[int] = field(default_factory=list)

    def __post_init__(self):
        if self.data_type == 'Bool' and not self.values:
            self.values = [True, False]
        elif not self.values:
            raise Exception("no `values:` were provided ")

        if self.weights:
            value_weight_pairs = list(zip_longest(self.values, self.weights[0:len(self.values)], fillvalue=1))
            self.values = list(chain(*[list([k] * v) for k, v in value_weight_pairs]))


    def generate(self, rows: int) -> pd.Series:
        return pd.Series(np.random.choice(self.values, rows, replace=True), dtype=self.pandas_type())


@dataclass(kw_only=True)
class Sequential(Column):
    """
    Generates a column starting at `start:` and increasing by `step:` for each row.

    Sequential supports the following `data_types:` - Int, Float, Decimal and Timestamp.

    **Usage:**
    ```
    - name: my_sequential_col
      column_type: Sequential
      data_type: Int
      start: 0
      step: 1
    ```

    **Concise syntax:**
    ```
    - col: my_sequential_col Sequential Timestamp 1H30min
    ```

    Required params:
    - `start:` the value to start from
    - `step:` the amount to increment by per row

    For the Timestamp data_type the step parameter should be specified in pandas offset format see https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases.
    """
    start: any = 0
    step: any = 1

    def add_column(self, df: pd.DataFrame) -> None:
        if self.data_type in ['Int', 'Decimal', 'Float', None]:
            df[self.name] = (df['rowId'] * float(self.step) + float(self.start)).round(decimals=self.decimal_places)

        elif self.data_type == 'Timestamp':
            df[self.name] = pd.date_range(start=self.start, periods=len(df), freq=self.step)

        else:
            raise ColumnGenerationException(f"Data type [{self.data_type}] not recognised")


@dataclass(kw_only=True)
class Map(Column):
    """
    Creates a Map based on the specified `columns:` or `source_columns:`.

    Typically you would not specify data_type for this column, the only exception is if you want the output serialised as a JSON string, use `data_type: String`.

    You can either specify a list of `source_columns:` that refer to previously created data, or defined further `columns:` to generate them inline.

    **Usage with `source_columns`:**
    ```
    # generate some data
    - col: id Sequential Int 1 1
    - col: name Random Sting 3 10

    # use the columns in a Map col
    - name: my_map_col
      column_type: Map
      source_columns: [id, name]
    ```

    **Usage with sub `columns:` and concise syntax:**
    ```
    - col: my_map_col Map
      columns:
        - col: id Sequential Int 1 1
        - col: name Random String 3 10

    ```

    Required params:
    - `source_columns:` or `columns:` the columns to combine into a Map

    Optional params:
    - `drop:` whether to drop the `source_columns:` from the data after combining them into a Map, default False for `source_columns:` and True for `columns:`.
    - `select_one:` whether to randomly pick one of the fields in the Map and set all the others to null. Default False.

    """

    source_columns: List[str] = field(default_factory=list)
    columns: List = field(default_factory=list)
    drop: bool = False
    select_one: bool = False

    def add_column(self, df: pd.DataFrame) -> None:
        if self.columns:
            self.drop = True
            for sub_col in self.columns:
                self.source_columns.append(sub_col.name)
                sub_col.maybe_add_column(df)


        if self.select_one:
            # randomly select one source_column per row and blank all other columns on that row
            chosen_cols = df[self.source_columns].columns.to_series().sample(len(df), replace=True, ignore_index=True)
            for col in self.source_columns:
                df.loc[chosen_cols != col, col] = np.nan

        if self.data_type == 'String':
            df[self.name] = pd.Series(df[self.source_columns].to_json(orient='records', lines=True).splitlines()).astype("string")
        else:
            df[self.name] = df[self.source_columns].to_dict(orient='records')

        if self.drop:
            df.drop(columns=self.source_columns, inplace=True)

def pandas_types_json_serialiser(val):
    if pd.isnull(val):
        return None
    else:
        return val

@dataclass(kw_only=True)
class Array(Column):
    """
    Creates a Array based on the specified `source_columns:`.

    Typically you would not specify data_type for this column, the only exception is if you want the output serialised as a JSON string, use `data_type: String`.

    **Usage:**
    ```
    # generate some data
    - col: int1 Sequential Int 1 1
    - col: int2 Random Sting 3 10
    - col: int3 Random Sting 40 200

    # use the columns in an Array col
    - name: my_array_col
      column_type: Array
      source_columns: [int1, int2, int3]
    ```

    **Concise syntax:**
    ```
    - col: my_array_col Array String
      source_columns: [int1, int2, int3]

    ```

    Required params:
    - `source_columns:` the columns to combine into an Array

    Optional params:
    - `drop:` whether to drop the `source_columns:` from the data after combining them into an Array, default True.
    - `drop_nulls:` whether to drop null values when combining them into an Array, some targets, like BigQuery do not accept null values within an Array. This can also be used in combination with `null_percentage:` to create variable length Arrays.

    """

    source_columns: List[str] = field(default_factory=list)
    drop: bool = True
    drop_nulls: bool = False

    def add_column(self, df: pd.DataFrame) -> None:
        if self.drop_nulls:
            fields = df[self.source_columns].apply(lambda x: np.array(x[x.notnull()]), axis=1)
        else:
            fields = pd.Series(list(df[self.source_columns].values))
        
        if self.data_type == 'String':
            df[self.name] = fields.apply(lambda x: json.dumps(list(x), default=pandas_types_json_serialiser)).astype('string')
        else:
            df[self.name] = fields
        
        if self.drop:
            df.drop(columns=self.source_columns, inplace=True)


@dataclass(kw_only=True)
class Series(Column):
    """
    Fills a column with a series of repeating `values:`.

    **Usage:**
    ```
    - name: my_series_col
      column_type: Series
      values:
        - A
        - B
        - C
    ```

    **Concise syntax:**
    ```
    - col: my_series_col Series Int
      values:
        - 1
        - 10
        - 100
    ```

    Required params:
    - `values:` the values to repeat

    """

    values: List[str] = field(default_factory=list)

    def generate(self, rows: int) -> pd.Series:
        repeats = rows // len(self.values) + 1
        return pd.Series(np.tile(self.values, repeats)[0:rows])


@dataclass(kw_only=True)
class ExtractDate(Column):
    """
    Extracts and manipulates Dates from a Timestamp `source_column:`.

    ExtractDate supports the following `data_types:` - Date, String, Int.

    **Usage:**
    ```
    # given a source timestamp column
    - col: event_time Random Timestamp 2022-01-01 2022-02-01

    # extract the date from it
    - name: dt
      column_type: ExtractDate
      data_type: Date
      source_column: event_time
    ```

    **Concise syntax:**
    ```
    - col: my_date_col ExtractDate Date my_source_col

    ```

    Required params:
    - `source_column:` - the column to base on

    Optional params:
    - `date_format:` used when `data_type:` is String or Int to format the timestamp. Follows python's strftime syntax. For `Int` the result of the formatting must be castable to an Integer i.e `%Y%m` but not `%Y-%m`.
    
    """

    source_column: str

    def add_column(self, df: pd.DataFrame) -> None:
        match self.data_type:
            case 'String' | 'Int':
                df[self.name] = df[self.source_column].dt.strftime(self.date_format)
            case 'Date':
                df[self.name] = df[self.source_column].dt.date
            case _:
                raise NotImplementedError(f"data_type: [{self.data_type}] is not implemented for the ExtractDate column_type")


@dataclass(kw_only=True)
class Eval(Column):
    """
    An eval column

    """

    expression: str

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = df.eval(self.expression)


@dataclass(kw_only=True)
class TimestampOffset(Column):
    """
    Create a new column by adding or removing random time deltas from a Timestamp `source_column:`.

    **Usage:**
    ```
    - col: start_time Random Timestamp 2021-01-01 2021-12-31

    - name: end_time
      column_type: TimestampOffset
      min: 4H
      max: 30D
    ```

    **Concise syntax:**
    ```
    - col: end_time TimestampOffset Timestamp 4H 30D
    ```

    Required params:
    - `min:` the lower bound
    - `max:` the uppper bound

    `min:` and `max:` should  be specified in pandas offset format see https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases.
    """
    min: str
    max: str
    source_column: str
    time_unit: str = "s"

    def add_column(self, df: pd.DataFrame) -> None:
        low = pd.Timedelta(self.min).total_seconds()
        high = pd.Timedelta(self.max).total_seconds()

        df[self.name] = df[self.source_column] + pd.to_timedelta(np.random.uniform(low, high, size=len(df)), 's').round(self.time_unit)


class ColumnGenerationException(Exception):
    pass
