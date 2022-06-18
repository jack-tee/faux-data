# Faux Data

[![PyPI Latest Release](https://img.shields.io/pypi/v/faux-data.svg)](https://pypi.org/project/faux-data/)
![Tests](https://github.com/jack-tee/faux-data/actions/workflows/Tests.yaml/badge.svg)

Faux Data is a library for generating data using configuration files.

The configuration files are called templates. Within a template, `columns` define the structure of the data and `targets` define where to load the data.

The main aims of Faux Data are:
- Make it easy to generate schematically correct datasets
- Provide easy integration with cloud services specifically on the Google Cloud Platform
- Support serverless generation of data e.g. using a Cloud Function invocation to generate data

Faux Data was originally a Python port of the scala application [dunnhumby/data-faker](https://github.com/dunnhumby/data-faker), but has evolved from there. The templates are still similar but are not directly compatible.

## Contents

- [Quick Start](#quick-start)
- [Columns](#columns)
  - [Random](#random), [Selection](#selection), [Sequential](#sequential), [MapValues](#mapvalues), [Series](#series), [Fixed](#fixed), [Empty](#empty), [Map](#map), [Array](#array), [ExtractDate](#extractdate), [TimestampOffset](#timestampoffset)
- [Targets](#targets)
  - [BigQuery](#bigquery), [CloudStorage](#cloudstorage), [LocalFile](#localfile), [Pubsub](#pubsub)
- [Usage](#usage)
- [Concepts](#concepts)

## Quick Start

### Install

Install faux-data locally via pip

`> pip install faux-data`

check the install has been successful with

`> faux --help`


### A Simple Template

Create a file `mytable.yaml` with the following contents:

```
tables:
  - name: mytable
    rows: 100
    targets: []
    columns:
      - name: id
        column_type: Sequential
        data_type: Int
        start: 1
        step: 1
    
      - name: event_time
        column_type: Random
        data_type: Timestamp
        min: '{{ start }}'
        max: '{{ end }}'
```

You can render this template with:

```
> faux render mytable.yaml

====================== Rendered Template =======================
tables:
  - name: mytable
    rows: 100
    targets: []
    columns:
      - name: id
        column_type: Sequential
        data_type: Int
        start: 1
        step: 1
    
      - name: event_time
        column_type: Random
        data_type: Timestamp
        min: '2022-05-20 00:00:00'
        max: '2022-05-21 00:00:00'
```

Notice that {{ start }} and {{ end }} are replaced with start and end dates automatically. Start and end are built-in variables that you can use in templates.
Start defaults to the start of yesterday and end defaults to the end of yesterday.

If you run:

```
> faux render mytable.yaml --start 2022-06-10

====================== Rendered Template =======================
    
    ...

      - name: event_time
        column_type: Random
        data_type: Timestamp
        min: '2022-06-10 00:00:00'
        max: '2022-06-11 00:00:00'
      
```

Notice now that {{ start }} and {{ end }} are now based on the provided `--start` value.


The two columns we have added so far use the long form syntax, which can get a bit verbose, there's a shorter syntax that can be used as well. Lets add another column using the more concise syntax
add the following column to your file.
```
      - col: currency Selection String
        values:
          - USD
          - GBP
          - EUR
```

Now let's test that the data is generated correctly run the following to see a sample of generated data.

```
> faux sample mytable.yaml

Table: mytable
Sample:
   id              event_time currency
0   1 2022-05-20 14:47:56.866      EUR
1   2 2022-05-20 09:24:11.971      GBP
2   3 2022-05-20 14:11:00.144      GBP
3   4 2022-05-20 22:32:35.579      EUR
4   5 2022-05-20 00:31:02.248      GBP

Schema:
id                     Int64
event_time    datetime64[ns]
currency              string
dtype: object
``` 

### Running the Template
In order for the data to be useful we need to load it somewhere, let's add a target to load the data to bigquery.

Add the following into the template replacing `targets: []`

```
    targets: 
      - target: BigQuery
        dataset: mydataset
        table: mytable
```

> To run this step you will need a google cloud project and to have your environment set up with google application credentials. 

Then run 

`> faux run mytable.yaml`

This will create a dataset in your google cloud project named mydataset and a table within called mytable and will load 100 rows of data to it.

## Columns

faux-data templates support the following `column_type:`s:

- **[Random](#random) - Generates columns of random data**
   
   _Examples: [Random Ints](#random), [Random Timestamps](#random), [Random Strings](#random)_

- **[Selection](#selection) - Generates columns by selecting random values**
   
   _Examples: [Simple Selection](#selection), [Selection with Weighting](#selection)_

- **[Sequential](#sequential) - Generates a column by incrementing a field from a `start:` by a `step:` for each row.**
   
   _Examples: [Sequential Ints](#sequential), [Sequential Timestamps](#sequential)_

- **[MapValues](#mapvalues) - Maps the values in one column to values in another**
   
   _Examples: [A Simple MapValues](#mapvalues), [Mapping a subset of values](#mapvalues), [MapValues with Default](#mapvalues)_

- **[Series](#series) - Repeats a series of values to fill a column**
   
   _Examples: [Simple Series](#series)_

- **[Fixed](#fixed) - Generates a column with a single fixed value**
   
   _Examples: [A Fixed String](#fixed)_

- **[Empty](#empty) - Generates and empty (null) column of data**
   
   _Examples: [An Empty Float](#empty)_

- **[Map](#map) - Map columns create a record style field from other fields**
   
   _Examples: [A Simple Map](#map), [Map with Json Output](#map), [Nested Map](#map), [Usage of `select_one:`](#map)_

- **[Array](#array) - Builds an array from the specified `source_columns:`.**
   
   _Examples: [Simple Array with primitive types](#array), [Use of `drop: False`](#array), [With nulls in `source_columns:`](#array), [Use of `drop_nulls: True`](#array), [Outputting a Json array](#array)_

- **[ExtractDate](#extractdate) - Extracts a date from a timestamp `source_column:`**
   
   _Examples: [Simple ExtractDate](#extractdate), [ExtractDate with custom formatting](#extractdate), [ExtractDate to an Int](#extractdate), [ExtractDate concise syntax](#extractdate)_

- **[TimestampOffset](#timestampoffset) - TimestampOffset produces a Timestamp column by adding some timedelta onto an existing timestamp column.**
   
   _Examples: [Simple TimestampOffset](#timestampoffset), [Fixed TimestampOffset](#timestampoffset)_




### Random

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


#### Examples



<a id="random1"></a>
<details>
  <summary>Random Ints</summary>

  A Random column generates random values between `min:` and `max:`.

  Template:
  ```
  name: simple_random_int
column_type: Random
data_type: Int
min: 5
max: 200
```

  Result:
  |    |   simple_random_int |
|----|---------------------|
|  0 |                 180 |
|  1 |                  30 |
|  2 |                  72 |
|  3 |                 156 |
|  4 |                 108 |

</details>



<a id="random2"></a>
<details>
  <summary>Random Timestamps</summary>

  You can generate random timestamps as well.

  Template:
  ```
  name: event_time
column_type: Random
data_type: Timestamp
min: 2022-01-01
max: 2022-01-02 12:00:00
```

  Result:
  |    | event_time                 |
|----|----------------------------|
|  0 | 2022-01-02 11:12:27.440000 |
|  1 | 2022-01-01 19:23:09.064000 |
|  2 | 2022-01-01 18:02:25.212000 |
|  3 | 2022-01-01 02:35:37.826000 |
|  4 | 2022-01-01 09:39:49.691000 |

</details>



<a id="random3"></a>
<details>
  <summary>Random Strings</summary>

  Or random strings, where min and max are the length of the string.

  Template:
  ```
  name: message_id
column_type: Random
data_type: String
min: 4
max: 12
```

  Result:
  |    | message_id   |
|----|--------------|
|  0 | EgVyEFV      |
|  1 | nmZyRyHhHTB  |
|  2 | IdNE         |
|  3 | OQoEVuOw     |
|  4 | YgtbznIOSvR  |

</details>




---

### Selection

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


#### Examples



<a id="selection1"></a>
<details>
  <summary>Simple Selection</summary>

  A simple Selection column fills a column with a random selection from the provided `values`.

  Template:
  ```
  name: simple_selection
column_type: Selection
values: 
  - first
  - second
```

  Result:
  |    | simple_selection   |
|----|--------------------|
|  0 | second             |
|  1 | first              |
|  2 | first              |
|  3 | first              |
|  4 | second             |

</details>



<a id="selection2"></a>
<details>
  <summary>Selection with Weighting</summary>

  You can apply weighting to the provided `values` to make some more likely to be selected. In this example USD is 10 times more likely than GBP and EUR is 3 times more likely than GBP. A specific weighting is not needed for GBP since it defaults to 1.

  Template:
  ```
  name: weighted_selection
column_type: Selection
values: 
  - USD
  - EUR
  - GBP
weights:
  - 10
  - 3
```

  Result:
  |    | weighted_selection   |
|----|----------------------|
|  0 | USD                  |
|  1 | EUR                  |
|  2 | USD                  |
|  3 | EUR                  |
|  4 | USD                  |

</details>




---

### Sequential

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


#### Examples



<a id="sequential1"></a>
<details>
  <summary>Sequential Ints</summary>

  A simple Sequential column can be used for generating incrementing Ids.

  Template:
  ```
  name: id
column_type: Sequential
data_type: Int
start: 1
step: 1
```

  Result:
  |    |   id |
|----|------|
|  0 |    1 |
|  1 |    2 |
|  2 |    3 |
|  3 |    4 |
|  4 |    5 |

</details>



<a id="sequential2"></a>
<details>
  <summary>Sequential Timestamps</summary>

  They can also be used for timestamps and can be written in the following concise syntax.

  Template:
  ```
  col: event_time Sequential Timestamp "1999-12-31 23:56:29" 1min45S
```

  Result:
  |    | event_time          |
|----|---------------------|
|  0 | 1999-12-31 23:56:29 |
|  1 | 1999-12-31 23:58:14 |
|  2 | 1999-12-31 23:59:59 |
|  3 | 2000-01-01 00:01:44 |
|  4 | 2000-01-01 00:03:29 |

</details>




---

### MapValues

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


#### Examples



<a id="mapvalues1"></a>
<details>
  <summary>A Simple MapValues</summary>

  A simple mapping

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: currency Selection String
    values:
      - EUR
      - USD
      - GBP
  - name: symbol
    column_type: MapValues
    source_column: currency
    values:
      EUR: €
      USD: $
      GBP: £
```

  Result:
  | currency   | symbol   |
|------------|----------|
| GBP        | £        |
| GBP        | £        |
| EUR        | €        |
| EUR        | €        |
| USD        | $        |

</details>



<a id="mapvalues2"></a>
<details>
  <summary>Mapping a subset of values</summary>

  Any values not specified in the mapping are left empty / null

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: currency Selection String
    values:
      - EUR
      - USD
      - GBP
  - name: symbol
    column_type: MapValues
    source_column: currency
    data_type: String
    values:
      EUR: €
```

  Result:
  | currency   | symbol   |
|------------|----------|
| EUR        | €        |
| EUR        | €        |
| USD        | <NA>     |
| EUR        | €        |
| USD        | <NA>     |

</details>



<a id="mapvalues3"></a>
<details>
  <summary>MapValues with Default</summary>

  You can provide a default value to fill any gaps

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: currency Selection String
    values:
      - EUR
      - USD
      - GBP
  - name: symbol
    column_type: MapValues
    source_column: currency
    data_type: String
    values:
      EUR: €
    default: "n/a"
```

  Result:
  | currency   | symbol   |
|------------|----------|
| EUR        | €        |
| GBP        | n/a      |
| EUR        | €        |
| USD        | n/a      |
| GBP        | n/a      |

</details>




---

### Series

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


#### Examples



<a id="series1"></a>
<details>
  <summary>Simple Series</summary>

  A simple series

  Template:
  ```
  name: group
column_type: Series
values:
  - A
  - B
```

  Result:
  |    | group   |
|----|---------|
|  0 | A       |
|  1 | B       |
|  2 | A       |
|  3 | B       |
|  4 | A       |

</details>




---

### Fixed

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


#### Examples



<a id="fixed1"></a>
<details>
  <summary>A Fixed String</summary>

  A fixed string

  Template:
  ```
  name: currency
column_type: Fixed
value: BTC
```

  Result:
  |    | currency   |
|----|------------|
|  0 | BTC        |
|  1 | BTC        |
|  2 | BTC        |
|  3 | BTC        |
|  4 | BTC        |

</details>




---

### Empty

An empty column.


#### Examples



<a id="empty1"></a>
<details>
  <summary>An Empty Float</summary>

  A simple empty column

  Template:
  ```
  name: pending_balance
column_type: Empty
data_type: Float
```

  Result:
  |    |   pending_balance |
|----|-------------------|
|  0 |               nan |
|  1 |               nan |
|  2 |               nan |
|  3 |               nan |
|  4 |               nan |

</details>




---

### Map

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


#### Examples



<a id="map1"></a>
<details>
  <summary>A Simple Map</summary>

  You can create a Map field by specifing sub `columns:`. Note that the intermediate format here is a python dict and so it renders with single quotes.

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: mymap Map
    columns:
      - col: id Random Int 100 300
      - col: name Random String 2 5
```

  Result:
  | mymap                       |
|-----------------------------|
| {'id': 138, 'name': 'Bvmr'} |
| {'id': 104, 'name': 'SZ'}   |
| {'id': 237, 'name': 'KqC'}  |
| {'id': 187, 'name': 'Lk'}   |
| {'id': 295, 'name': 'odSZ'} |

</details>



<a id="map2"></a>
<details>
  <summary>Map with Json Output</summary>

  If you want a valid json field specify `data_type: String`.

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: mymap Map
    data_type: String
    columns:
      - col: id Random Int 100 300
      - col: name Random String 2 5
```

  Result:
  | mymap                    |
|--------------------------|
| {"id":172,"name":"rd"}   |
| {"id":183,"name":"bwv"}  |
| {"id":276,"name":"cF"}   |
| {"id":101,"name":"tE"}   |
| {"id":292,"name":"AZqe"} |

</details>



<a id="map3"></a>
<details>
  <summary>Nested Map</summary>

  Similarly you can nest to any depth by adding Map columns within Map columns.

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: mymap Map
    data_type: String
    columns:
      - col: id Random Int 100 300
      - col: nestedmap Map
        columns:
          - col: balance Sequential Float 5.4 1.15
          - col: status Selection String
            values:
              - active
              - inactive
```

  Result:
  | mymap                                                       |
|-------------------------------------------------------------|
| {"id":244,"nestedmap":{"balance":5.4,"status":"active"}}    |
| {"id":218,"nestedmap":{"balance":6.55,"status":"active"}}   |
| {"id":259,"nestedmap":{"balance":7.7,"status":"inactive"}}  |
| {"id":193,"nestedmap":{"balance":8.85,"status":"inactive"}} |
| {"id":272,"nestedmap":{"balance":10.0,"status":"active"}}   |

</details>



<a id="map4"></a>
<details>
  <summary>Usage of `select_one:`</summary>

  Specifying `select_one: True`, picks one field and masks all the others.

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: mymap Map String
    select_one: True
    columns:
      - col: id Random Int 100 300
      - col: name Random String 3 6
      - col: status Selection
        values:
          - Y
          - N
```

  Result:
  | mymap                                    |
|------------------------------------------|
| {"id":null,"name":"XYp","status":null}   |
| {"id":null,"name":"icTqX","status":null} |
| {"id":161,"name":null,"status":null}     |
| {"id":null,"name":"wLmpY","status":null} |
| {"id":null,"name":null,"status":"Y"}     |

</details>




---

### Array

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


#### Examples



<a id="array1"></a>
<details>
  <summary>Simple Array with primitive types</summary>

  A simple array of primitive types

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: int1 Random Int 20 50
  - col: int2 Random Int 50 90
  - name: array_col
    column_type: Array
    source_columns: [int1, int2]
```

  Result:
  | array_col   |
|-------------|
| [45 81]     |
| [25 52]     |
| [29 69]     |
| [49 68]     |
| [37 71]     |

</details>



<a id="array2"></a>
<details>
  <summary>Use of `drop: False`</summary>

  The source columns are removed by default but you can leave them with `drop: False`

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: int1 Random Int 20 50
  - col: int2 Random Int 50 90
  - name: array_col
    drop: False
    column_type: Array
    source_columns: [int1, int2]
```

  Result:
  |   int1 |   int2 | array_col   |
|--------|--------|-------------|
|     43 |     66 | [43 66]     |
|     23 |     62 | [23 62]     |
|     31 |     79 | [31 79]     |
|     46 |     59 | [46 59]     |
|     35 |     62 | [35 62]     |

</details>



<a id="array3"></a>
<details>
  <summary>With nulls in `source_columns:`</summary>

  Nulls in the source_columns are included in the array by default

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: int1 Random Int 20 50
  - col: int2 Random Int 50 90
    null_percentage: 90
  - name: array_col
    drop: False
    column_type: Array
    source_columns: [int1, int2]
```

  Result:
  |   int1 | int2   | array_col   |
|--------|--------|-------------|
|     23 | <NA>   | [23 <NA>]   |
|     34 | <NA>   | [34 <NA>]   |
|     34 | 54     | [34 54]     |
|     48 | <NA>   | [48 <NA>]   |
|     40 | <NA>   | [40 <NA>]   |

</details>



<a id="array4"></a>
<details>
  <summary>Use of `drop_nulls: True`</summary>

  Add `drop_nulls: True` to remove them from the array

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: int1 Random Int 20 50
  - col: int2 Random Int 50 90
    null_percentage: 90
  - name: array_col
    drop: False
    drop_nulls: True
    column_type: Array
    source_columns: [int1, int2]
```

  Result:
  |   int1 | int2   | array_col   |
|--------|--------|-------------|
|     27 | <NA>   | [27]        |
|     23 | <NA>   | [23]        |
|     49 | <NA>   | [49]        |
|     32 | <NA>   | [32]        |
|     32 | 56     | [32 56]     |

</details>



<a id="array5"></a>
<details>
  <summary>Outputting a Json array</summary>

  You can get a Json formatted string using data_type: String

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: int1 Random Int 20 50
  - col: int2 Empty Int
  - col: str1 Fixed String foo
  - name: array_col
    data_type: String
    column_type: Array
    source_columns: [int1, int2, str1]
```

  Result:
  | array_col         |
|-------------------|
| [35, null, "foo"] |
| [25, null, "foo"] |
| [24, null, "foo"] |
| [40, null, "foo"] |
| [29, null, "foo"] |

</details>




---

### ExtractDate

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


#### Examples



<a id="extractdate1"></a>
<details>
  <summary>Simple ExtractDate</summary>

  You may want to use a timestamp column to populate another column. For example populating a `dt` column with the date. The ExtractDate column provides an easy way to do this.

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: event_time Random Timestamp 2022-02-02 2022-04-01
  - name: dt
    column_type: ExtractDate
    data_type: Date
    source_column: event_time
```

  Result:
  | event_time                 | dt         |
|----------------------------|------------|
| 2022-02-26 01:32:35.762000 | 2022-02-26 |
| 2022-02-27 23:47:02.238000 | 2022-02-27 |
| 2022-03-18 22:39:40.763000 | 2022-03-18 |
| 2022-03-20 04:34:33.079000 | 2022-03-20 |
| 2022-03-04 07:10:01.409000 | 2022-03-04 |

</details>



<a id="extractdate2"></a>
<details>
  <summary>ExtractDate with custom formatting</summary>

  You can also extract the date as a string and control the formatting

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: event_time Random Timestamp 2022-02-02 2022-04-01
  - name: day_of_month
    column_type: ExtractDate
    data_type: String
    date_format: "A %A in %B"
    source_column: event_time
```

  Result:
  | event_time                 | day_of_month         |
|----------------------------|----------------------|
| 2022-02-28 17:11:50.540000 | A Monday in February |
| 2022-03-19 03:16:24        | A Saturday in March  |
| 2022-03-25 11:06:22.395000 | A Friday in March    |
| 2022-03-13 03:29:12.939000 | A Sunday in March    |
| 2022-03-20 10:16:00.610000 | A Sunday in March    |

</details>



<a id="extractdate3"></a>
<details>
  <summary>ExtractDate to an Int</summary>

  Or extract part of the date as an integer

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: event_time Random Timestamp 2000-01-01 2010-12-31
  - name: year
    column_type: ExtractDate
    data_type: Int
    date_format: "%Y"
    source_column: event_time
```

  Result:
  | event_time                 |   year |
|----------------------------|--------|
| 2010-04-30 09:50:50.606000 |   2010 |
| 2000-06-12 07:32:42.994000 |   2000 |
| 2009-08-18 13:45:34.744000 |   2009 |
| 2003-01-15 22:53:33.679000 |   2003 |
| 2005-03-26 03:30:13.897000 |   2005 |

</details>



<a id="extractdate4"></a>
<details>
  <summary>ExtractDate concise syntax</summary>

  The concise format for an ExtractDate column

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: event_time Random Timestamp 2000-01-01 2010-12-31
  - col: dt ExtractDate Date event_time
```

  Result:
  | event_time                 | dt         |
|----------------------------|------------|
| 2008-10-05 14:07:49.209000 | 2008-10-05 |
| 2007-11-21 03:53:20.865000 | 2007-11-21 |
| 2001-08-14 02:12:11.216000 | 2001-08-14 |
| 2007-03-31 04:36:07.737000 | 2007-03-31 |
| 2000-10-05 04:27:12.835000 | 2000-10-05 |

</details>




---

### TimestampOffset

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


#### Examples



<a id="timestampoffset1"></a>
<details>
  <summary>Simple TimestampOffset</summary>

  This example shows adding a random timedelta onto a timestamp field

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: game_id Random Int 2 8
  - col: game_start Random Timestamp 2022-02-02 2022-04-01
  - name: game_end
    column_type: TimestampOffset
    source_column: game_start
    min: 1min30s
    max: 25min
```

  Result:
  |   game_id | game_start                 | game_end                   |
|-----------|----------------------------|----------------------------|
|         8 | 2022-03-28 17:27:34.087000 | 2022-03-28 17:33:16.087000 |
|         2 | 2022-03-16 19:00:59.738000 | 2022-03-16 19:11:42.738000 |
|         3 | 2022-02-04 09:52:10.625000 | 2022-02-04 10:15:45.625000 |
|         7 | 2022-03-17 22:49:48.922000 | 2022-03-17 22:56:18.922000 |
|         7 | 2022-03-03 18:39:15.099000 | 2022-03-03 18:59:52.099000 |

</details>



<a id="timestampoffset2"></a>
<details>
  <summary>Fixed TimestampOffset</summary>

  If you want a fixed offset from the source timestamp you can set min and max to the same value

  Template:
  ```
  name: mytbl
rows: 5
columns:
  - col: promo_id Sequential Int 100 1
  - col: promo_start Sequential Timestamp 2022-02-02T12:00:00 1min15s
  - name: promo_end
    column_type: TimestampOffset
    source_column: promo_start
    min: 1min15s
    max: 1min15s
```

  Result:
  |   promo_id | promo_start         | promo_end           |
|------------|---------------------|---------------------|
|        100 | 2022-02-02 12:00:00 | 2022-02-02 12:01:15 |
|        101 | 2022-02-02 12:01:15 | 2022-02-02 12:02:30 |
|        102 | 2022-02-02 12:02:30 | 2022-02-02 12:03:45 |
|        103 | 2022-02-02 12:03:45 | 2022-02-02 12:05:00 |
|        104 | 2022-02-02 12:05:00 | 2022-02-02 12:06:15 |

</details>




---


## Targets

faux-data templates support the following `targets:`:

- [BigQuery](#bigquery)
- [CloudStorage](#cloudstorage)
- [LocalFile](#localfile)
- [Pubsub](#pubsub)



### BigQuery

Target that loads data to BigQuery tables.

This will create datasets / tables that don't currently exist, or load data to existing tables.

Usage:

    targets:
    - target: BigQuery
      dataset: mydataset # the name of the dataset where the table belongs
      table: mytable # the name of the table to load to

      # Optional parameters
      project: myproject # the GCP project where the dataset exists defaults to the system default
      truncate: True # whether to clear the table before loading, defaults to False
      post_generation_sql: "INSERT INTO xxx" # A query that will be run after the data has been inserted


### CloudStorage

Target that creates files in cloud storage.

Supports csv and parquet `filetype`s.

Usage:

    targets:
    - target: CloudStorage
      filetype: csv / parquet
      bucket: mybucket # the cloud storage bucket to save to
      prefix: my/prefix # the path prefix to give to all objects
      filename: myfile.csv # the name of the file

      # Optional params
      partition_cols: [col1, col2] # Optional. The columns within the dataset to partition on.


If partition_cols is specified then data will be split into separate files and loaded to cloud storage
with filepaths that follow the hive partitioning structure.
e.g. If a dataset has dt and currency columns and these are specified as partition_cols
then you might expect the following files to be created:
- gs://bucket/prefix/dt=2022-01-01/currency=USD/filename
- gs://bucket/prefix/dt=2022-01-01/currency=EUR/filename


### LocalFile

Target that creates files on the local file system

Supports csv and parquet `filetype`s.

Usage:

    targets:
    - target: LocalFile
      filetype: csv / parquet
      filepath: path/to/myfile # an absolute or relative base path
      filename: myfile.csv # the name of the file

      # Optional params
      partition_cols: [col1, col2] # Optional. The columns within the dataset to partition on.


If partition_cols is specified then data will be split into separate files and
separate files / directories will be created with filepaths that follow the hive partitioning structure.
e.g. If a dataset has dt and currency columns and these are specified as partition_cols
then you might expect the following files to be created:
- filepath/dt=2022-01-01/currency=USD/filename
- filepath/dt=2022-01-01/currency=EUR/filename


### Pubsub

Target that publishes data to Pubsub.

This target converts the data into json format and publishes each row as a separate pubsub message.
It expects the topic to already exist.

Usage:

    targets:
    - target: Pubsub
      topic: mytopic # the name of the topic

      # Optional parameters
      project: myproject # the GCP project where the topic exists defaults to the system default
      output_cols: [col1, col2] # the columns to convert to json and use for the message body
      attribute_cols: [col3, col4] # the columns to pass as pubsub message attributes, these columns will be removed from the message body unless they are also specified in the output_cols
      attributes: # additional attributes to add to the pbsub messages
        key1: value1
        key2: value2

      delay: 0.01 # the time in seconds to wait between each publish, default is 0.01
      date_format: iso # how timestamp fields should be formatted in the json eith iso or epoch
      time_unit: s # the resolution to use for timestamps, s, ms, us etc.



## Usage

The library can be used in various ways
- via the faux cli
- as a library by importing it into your python project, instantiating templates and calling the `.generate()` or `.run()` methods on them
- running the code in a cloud function, passing a template to the cloud function at call time, or using a template stored in cloud storage

### Using the CLI

#### Configuration
To use Google Cloud targets do *one* of the following:
- ensure that the `GOOGLE_CLOUD_PROJECT` environment variable is set 
- set the `FAUXDATA_GCP_PROJECT_ID` environment variable
- place a toml file at `~/.fauxdata/config.toml` with the following contents:

```
gcp_project_id = "myproject"
```

---

### Using the Python Library

---

### Deploying as a Cloud Function

To deploy a cloud function

```
gcloud functions deploy faux-data \
  --region europe-west2 \
  --project XXX \
  --runtime python310 \
  --trigger-http \
  --set-env-vars='FAUXDATA_DEPLOYMENT_MODE=cloud_function,FAUXDATA_TEMPLATE_BUCKET=df2test,FAUXDATA_TEMPLATE_LOCATION=templates' \
  --entry-point generate

```
---

## Concepts

### Variables

You can specify variables in a template to make parts of it modifyable at runtime. A common use case for this is to control the number of rows of data generated as follows:

```
variables:
  row_count: 100
tables:
  - name: mytable
    rows: {{ row_count }}
    columns:
      ...
```
By default the above will generate 100 rows, but when running the template you can specify row_count to override this number. For examples through the cli you might run `faux run mytemplate.yaml --row_count 40000`.

---

### Data Types and Output Types

---

### Using a CSV as the basis for a table

You may want to contain hardcoded data for some or all columns of a table. You can do this by specifying the path to the file as the `rows:` attribute. The path should be either a path relative to the template directory or an absolute or cloud storage path.

The following example will look for mytable.csv in the same directory as the template yaml file. This will work whether the template file is local or stored in cloud storage.

```
tables:
  - name: mytable
    rows: mytable.csv
    columns:
      ...
```

The following example, being an absolute pathm, will load the csv from cloud storage regardless of where the template yaml is loaded from.

```
tables:
  - name: mytable
    rows: gs://mybucket/templates/data/mytable.csv
    columns:
      ...
```
---