# Columns


- [Random](#random) - Generates columns of random data
  -  [Random Ints](#random1)
  -  [Random Timestamps](#random2)
  -  [Random Strings](#random3)
  

- [Selection](#selection) - Generates columns by selecting random values
  -  [Simple Selection](#selection1)
  -  [Selection with Weighting](#selection2)
  

- [Sequential](#sequential) - Generates a column by incrementing a field from a `start:` by a `step:` for each row.
  -  [Sequential Ints](#sequential1)
  -  [Sequential Timestamps](#sequential2)
  

- [MapValues](#mapvalues) - Maps the values in one column to values in another
  -  [A Simple MapValues](#mapvalues1)
  -  [Mapping a subset of values](#mapvalues2)
  -  [MapValues with Default](#mapvalues3)
  

- [Series](#series) - Repeats a series of values to fill a column
  -  [Simple Series](#series1)
  

- [Fixed](#fixed) - Generates a column with a single fixed value
  -  [A Fixed String](#fixed1)
  

- [Empty](#empty) - Generates and empty (null) column of data
  -  [An Empty Float](#empty1)
  

- [Map](#map) - Map columns create a record style field from other fields
  -  [A Simple Map](#map1)
  -  [Map with Json Output](#map2)
  -  [Nested Map](#map3)
  -  [Usage of `select_one:`](#map4)
  

- [Array](#array) - Builds an array from the specified `source_columns:`.
  -  [Simple Array with primitive types](#array1)
  -  [Use of `drop: False`](#array2)
  -  [With nulls in `source_columns:`](#array3)
  -  [Use of `drop_nulls: True`](#array4)
  -  [Outputting a Json array](#array5)
  

- [ExtractDate](#extractdate) - Extracts a date from a timestamp `source_column:`
  -  [Simple ExtractDate](#extractdate1)
  -  [ExtractDate with custom formatting](#extractdate2)
  -  [ExtractDate to an Int](#extractdate3)
  -  [ExtractDate concise syntax](#extractdate4)
  

- [TimestampOffset](#timestampoffset) - TimestampOffset produces a Timestamp column by adding some timedelta onto an existing timestamp column.
  -  [Simple TimestampOffset](#timestampoffset1)
  -  [Fixed TimestampOffset](#timestampoffset2)
  




## Random

A Random column


### Examples


A Random column generates random values between `min:` and `max:`.

<a id="random1"></a>
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

---



You can generate random timestamps as well.

<a id="random2"></a>
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

---



Or random strings, where min and max are the length of the string.

<a id="random3"></a>
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
|  0 | xkILAtrLnwT  |
|  1 | zNXDYHa      |
|  2 | CAgzOIL      |
|  3 | viNLM        |
|  4 | yEhi         |

---




## Selection

A selection column


### Examples


A simple Selection column fills a column with a random selection from the provided `values`.

<a id="selection1"></a>
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

---



You can apply weighting to the provided `values` to make some more likely to be selected. In this example USD is 10 times more likely than GBP and EUR is 3 times more likely than GBP. A specific weighting is not needed for GBP since it defaults to 1.

<a id="selection2"></a>
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

---




## Sequential

A Sequential column

### Examples


A simple Sequential column can be used for generating incrementing Ids.

<a id="sequential1"></a>
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

---



They can also be used for timestamps and can be written in the following concise syntax.

<a id="sequential2"></a>
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

---




## MapValues

A MapValues column

### Examples


A simple mapping

<a id="mapvalues1"></a>
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

---



Any values not specified in the mapping are left empty / null

<a id="mapvalues2"></a>
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

---



You can provide a default value to fill any gaps

<a id="mapvalues3"></a>
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

---




## Series

A Series column

### Examples


A simple series

<a id="series1"></a>
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

---




## Fixed

A Fixed column

### Examples


A fixed string

<a id="fixed1"></a>
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

---




## Empty

A Empty column

### Examples


A simple empty column

<a id="empty1"></a>
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

---




## Map

A Map column

### Examples


You can create a Map field by specifing sub `columns:`. Note that the intermediate format here is a python dict and so it renders with single quotes.

<a id="map1"></a>
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
| {'id': 271, 'name': 'nztQ'} |
| {'id': 133, 'name': 'cQ'}   |
| {'id': 223, 'name': 'MrI'}  |
| {'id': 179, 'name': 'iQa'}  |
| {'id': 276, 'name': 'mQ'}   |

---



If you want a valid json field specify `data_type: String`.

<a id="map2"></a>
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
| mymap                     |
|---------------------------|
| {"id":137,"name":"Ft"}    |
| {"id":120,"name":"wsCO"}  |
| {"id":194,"name":"MDoXK"} |
| {"id":149,"name":"ksVm"}  |
| {"id":249,"name":"srleM"} |

---



Similarly you can nest to any depth by adding Map columns within Map columns.

<a id="map3"></a>
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

---



Specifying `select_one: True`, picks one field and masks all the others.

<a id="map4"></a>
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
| mymap                                     |
|-------------------------------------------|
| {"id":null,"name":"oCJLJi","status":null} |
| {"id":null,"name":"aQYrAU","status":null} |
| {"id":null,"name":null,"status":"N"}      |
| {"id":299,"name":null,"status":null}      |
| {"id":265,"name":null,"status":null}      |

---




## Array

A Array column

### Examples


A simple array of primitive types

<a id="array1"></a>
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

---



The source columns are removed by default but you can leave them with `drop: False`

<a id="array2"></a>
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

---



Nulls in the source_columns are included in the array by default

<a id="array3"></a>
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

---



Add `drop_nulls: True` to remove them from the array

<a id="array4"></a>
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

---



You can get a Json formatted string using data_type: String

<a id="array5"></a>
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

---




## ExtractDate

A ExtractDate column

### Examples


You may want to use a timestamp column to populate another column. For example populating a `dt` column with the date. The ExtractDate column provides an easy way to do this.

<a id="extractdate1"></a>
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

---



You can also extract the date as a string and control the formatting

<a id="extractdate2"></a>
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

---



Or extract part of the date as an integer

<a id="extractdate3"></a>
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

---



The concise format for an ExtractDate column

<a id="extractdate4"></a>
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

---




## TimestampOffset

A TimestampOffset column

### Examples


This example shows adding a random timedelta onto a timestamp field

<a id="timestampoffset1"></a>
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

---



If you want a fixed offset from the source timestamp you can set min and max to the same value

<a id="timestampoffset2"></a>
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

---


