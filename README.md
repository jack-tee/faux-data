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
  - [Random](#random), [Selection](#selection), [Sequential](#sequential), [MapValues](#mapvalues), [Series](#series), [Fixed](#fixed), [Empty](#empty), [Map](#map), [Array](#array), [ExtractDate](#extractdate), [TimestampOffset](#timestampoffset), [Eval](#eval)
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
- [Eval](#eval)



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

See [COLUMNS.md](COLUMNS.md#random) for more info and usage examples.

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

See [COLUMNS.md](COLUMNS.md#selection) for more info and usage examples.

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

See [COLUMNS.md](COLUMNS.md#sequential) for more info and usage examples.

### MapValues

A map column.

See [COLUMNS.md](COLUMNS.md#mapvalues) for more info and usage examples.

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

See [COLUMNS.md](COLUMNS.md#series) for more info and usage examples.

### Fixed

A column with a single fixed `value:`.

See [COLUMNS.md](COLUMNS.md#fixed) for more info and usage examples.

### Empty

An empty column.

See [COLUMNS.md](COLUMNS.md#empty) for more info and usage examples.

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

See [COLUMNS.md](COLUMNS.md#map) for more info and usage examples.

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

See [COLUMNS.md](COLUMNS.md#array) for more info and usage examples.

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

See [COLUMNS.md](COLUMNS.md#extractdate) for more info and usage examples.

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

See [COLUMNS.md](COLUMNS.md#timestampoffset) for more info and usage examples.

### Eval

An eval column

See [COLUMNS.md](COLUMNS.md#eval) for more info and usage examples.


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