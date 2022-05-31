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
- [Deploying](#deploying)
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

- [Random](#random)
- [Selection](#selection)
- [Sequential](#sequential)
- [MapValues](#mapvalues)
- [Series](#series)
- [Fixed](#fixed)
- [Empty](#empty)
- [Map](#map)
- [Array](#array)
- [ExtractDate](#extractdate)
- [TimestampOffset](#timestampoffset)



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
|  0 |                 111 |
|  1 |                 157 |
|  2 |                 136 |
|  3 |                 189 |
|  4 |                   5 |

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
|  0 | 2022-01-01 20:29:42.748000 |
|  1 | 2022-01-01 15:44:03.227000 |
|  2 | 2022-01-01 00:40:29.741000 |
|  3 | 2022-01-01 01:27:45.743000 |
|  4 | 2022-01-01 08:55:26.323000 |

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
|  0 | pLyebCp      |
|  1 | lBoi         |
|  2 | nXbHn        |
|  3 | kqGMSTeF     |
|  4 | AjyeWTCpVD   |

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
|  0 | first              |
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
|  1 | USD                  |
|  2 | EUR                  |
|  3 | USD                  |
|  4 | EUR                  |

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

A map column.


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
| GBP        | £        |
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
| GBP        | <NA>     |
| USD        | <NA>     |
| EUR        | €        |
| GBP        | <NA>     |
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
| USD        | n/a      |
| GBP        | n/a      |
| EUR        | €        |
| GBP        | n/a      |
| EUR        | €        |

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

A column with a single fixed `value:`.


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
  | mymap                        |
|------------------------------|
| {'id': 271, 'name': 'SAvF'}  |
| {'id': 133, 'name': 'xmnPe'} |
| {'id': 223, 'name': 'GoByr'} |
| {'id': 179, 'name': 'dVH'}   |
| {'id': 276, 'name': 'osMqD'} |

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
| {"id":137,"name":"fdlN"} |
| {"id":120,"name":"gWp"}  |
| {"id":194,"name":"cK"}   |
| {"id":149,"name":"MXap"} |
| {"id":249,"name":"OvX"}  |

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
| {"id":227,"nestedmap":{"balance":5.4,"status":"active"}}    |
| {"id":128,"nestedmap":{"balance":6.55,"status":"inactive"}} |
| {"id":219,"nestedmap":{"balance":7.7,"status":"active"}}    |
| {"id":154,"nestedmap":{"balance":8.85,"status":"active"}}   |
| {"id":100,"nestedmap":{"balance":10.0,"status":"inactive"}} |

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
  | mymap                                   |
|-----------------------------------------|
| {"id":null,"name":"pjx","status":null}  |
| {"id":null,"name":"nFiD","status":null} |
| {"id":null,"name":null,"status":"N"}    |
| {"id":299,"name":null,"status":null}    |
| {"id":265,"name":null,"status":null}    |

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
| [23 66]     |
| [47 68]     |
| [36 61]     |
| [36 82]     |
| [20 81]     |

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
|     33 |     83 | [33 83]     |
|     25 |     52 | [25 52]     |
|     50 |     78 | [50 78]     |
|     36 |     86 | [36 86]     |
|     49 |     76 | [49 76]     |

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
|     28 | 86     | [28 86]     |
|     32 | <NA>   | [32 <NA>]   |
|     36 | <NA>   | [36 <NA>]   |
|     47 | <NA>   | [47 <NA>]   |
|     30 | <NA>   | [30 <NA>]   |

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
|     35 | <NA>   | [35]        |
|     43 | <NA>   | [43]        |
|     48 | <NA>   | [48]        |
|     44 | <NA>   | [44]        |
|     43 | 62     | [43 62]     |

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
| [39, null, "foo"] |
| [36, null, "foo"] |
| [44, null, "foo"] |
| [22, null, "foo"] |
| [27, null, "foo"] |

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
| 2022-02-18 02:02:01.249000 | 2022-02-18 |
| 2022-02-12 05:04:42.474000 | 2022-02-12 |
| 2022-03-31 10:29:57.298000 | 2022-03-31 |
| 2022-03-14 04:10:10.772000 | 2022-03-14 |
| 2022-03-17 14:58:44.102000 | 2022-03-17 |

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
  | event_time                 | day_of_month          |
|----------------------------|-----------------------|
| 2022-02-08 17:46:24.557000 | A Tuesday in February |
| 2022-02-06 23:42:46.797000 | A Sunday in February  |
| 2022-03-12 14:32:58.039000 | A Saturday in March   |
| 2022-02-21 02:45:47.976000 | A Monday in February  |
| 2022-02-22 23:25:03.592000 | A Tuesday in February |

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
| 2005-10-14 09:18:33.871000 |   2005 |
| 2004-09-02 03:21:56.718000 |   2004 |
| 2009-01-06 01:25:13.708000 |   2009 |
| 2006-04-13 20:25:11.452000 |   2006 |
| 2009-09-09 10:07:26.787000 |   2009 |

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
| 2008-10-21 00:35:01.304000 | 2008-10-21 |
| 2003-11-06 15:35:28.125000 | 2003-11-06 |
| 2008-07-01 02:11:28.173000 | 2008-07-01 |
| 2009-11-10 05:27:00.117000 | 2009-11-10 |
| 2008-08-22 06:41:25.136000 | 2008-08-22 |

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
|         4 | 2022-02-13 03:21:52.691000 | 2022-02-13 03:36:08.691000 |
|         6 | 2022-03-16 02:07:55.619000 | 2022-03-16 02:11:32.619000 |
|         7 | 2022-03-19 12:37:54.808000 | 2022-03-19 12:50:53.808000 |
|         6 | 2022-03-30 09:09:39.320000 | 2022-03-30 09:32:57.320000 |
|         3 | 2022-03-23 08:33:07.965000 | 2022-03-23 08:53:08.965000 |

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



## Deploying

The library can be used in various ways
- via the faux cli
- as a library by importing it into your python project, instantiating templates and calling the `.generate()` or `.run()` methods on them
- running the code in a cloud function, passing a template to the cloud function at call time, or using a template stored in cloud storage


### Deploying as a Cloud Function

To deploy a cloud function

```
gcloud functions deploy faux-data \
  --region europe-west2 \
  --project XXX \
  --runtime python310 \
  --trigger-http \
  --set-env-vars='FAUX_DATA_DEPLOYMENT_MODE=cloud_function,FAUX_DATA_TEMPLATE_BUCKET=df2test,FAUX_DATA_TEMPLATE_LOCATION=templates' \
  --entry-point generate

```

## Concepts

### Variables

### Data Types and Output Types