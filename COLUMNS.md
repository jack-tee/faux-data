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
|  0 |                  44 |
|  1 |                  63 |
|  2 |                  58 |
|  3 |                  18 |
|  4 |                 198 |

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
|  0 | 2022-01-01 15:30:52.994000 |
|  1 | 2022-01-02 01:02:42.844000 |
|  2 | 2022-01-02 02:03:50.694000 |
|  3 | 2022-01-02 06:30:00.987000 |
|  4 | 2022-01-02 06:17:48.799000 |

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
|  0 | mxEYhlHVC    |
|  1 | WQmpy        |
|  2 | OkSYo        |
|  3 | uPHjUizCRN   |
|  4 | plQDrw       |

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
|  1 | second             |
|  2 | second             |
|  3 | second             |
|  4 | first              |

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
|  4 | USD                  |

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
| USD        | $        |
| USD        | $        |
| GBP        | £        |
| USD        | $        |
| GBP        | £        |

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
| EUR        | €        |
| USD        | <NA>     |
| EUR        | €        |
| USD        | <NA>     |
| EUR        | €        |

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
| EUR        | €        |
| GBP        | n/a      |
| GBP        | n/a      |
| USD        | n/a      |
| GBP        | n/a      |

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
| mymap                        |
|------------------------------|
| {'id': 177, 'name': 'giGzX'} |
| {'id': 249, 'name': 'Ofc'}   |
| {'id': 159, 'name': 'IGwun'} |
| {'id': 180, 'name': 'ZN'}    |
| {'id': 128, 'name': 'vRf'}   |

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
| {"id":176,"name":"yQ"}    |
| {"id":252,"name":"jZSbP"} |
| {"id":279,"name":"QZ"}    |
| {"id":295,"name":"bZ"}    |
| {"id":280,"name":"pmx"}   |

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
| {"id":226,"nestedmap":{"balance":5.4,"status":"inactive"}}  |
| {"id":163,"nestedmap":{"balance":6.55,"status":"inactive"}} |
| {"id":154,"nestedmap":{"balance":7.7,"status":"active"}}    |
| {"id":121,"nestedmap":{"balance":8.85,"status":"active"}}   |
| {"id":118,"nestedmap":{"balance":10.0,"status":"active"}}   |

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
| mymap                                |
|--------------------------------------|
| {"id":240,"name":null,"status":null} |
| {"id":222,"name":null,"status":null} |
| {"id":166,"name":null,"status":null} |
| {"id":null,"name":null,"status":"Y"} |
| {"id":161,"name":null,"status":null} |

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
| [43 54]     |
| [34 87]     |
| [35 80]     |
| [21 51]     |
| [36 77]     |

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
|     29 |     72 | [29 72]     |
|     20 |     67 | [20 67]     |
|     37 |     52 | [37 52]     |
|     43 |     79 | [43 79]     |
|     30 |     50 | [30 50]     |

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
|     40 | 61     | [40 61]     |
|     48 | <NA>   | [48 <NA>]   |
|     45 | <NA>   | [45 <NA>]   |
|     27 | <NA>   | [27 <NA>]   |
|     33 | <NA>   | [33 <NA>]   |

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
|     26 | <NA>   | [26]        |
|     25 | <NA>   | [25]        |
|     40 | 82     | [40 82]     |
|     35 | <NA>   | [35]        |
|     48 | <NA>   | [48]        |

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
| [38, null, "foo"] |
| [42, null, "foo"] |
| [46, null, "foo"] |
| [36, null, "foo"] |

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
| 2022-02-10 18:46:29.275000 | 2022-02-10 |
| 2022-03-13 06:03:17.325000 | 2022-03-13 |
| 2022-03-16 01:36:36.748000 | 2022-03-16 |
| 2022-02-03 05:56:49.936000 | 2022-02-03 |
| 2022-03-23 06:34:26.570000 | 2022-03-23 |

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
| event_time                 | day_of_month         |
|----------------------------|----------------------|
| 2022-02-20 14:27:50.844000 | A Sunday in February |
| 2022-03-09 22:44:12.282000 | A Wednesday in March |
| 2022-03-29 19:02:53.447000 | A Tuesday in March   |
| 2022-02-21 21:21:58.462000 | A Monday in February |
| 2022-02-06 19:22:18.027000 | A Sunday in February |

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
| 2000-07-22 21:44:42.387000 |   2000 |
| 2000-03-23 20:56:56.326000 |   2000 |
| 2002-08-03 03:36:09.609000 |   2002 |
| 2010-04-15 04:13:06.934000 |   2010 |
| 2005-06-01 16:16:29.590000 |   2005 |

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
| 2006-12-09 08:03:18.205000 | 2006-12-09 |
| 2006-08-25 19:27:28.859000 | 2006-08-25 |
| 2007-06-01 10:51:22.237000 | 2007-06-01 |
| 2010-04-16 16:16:01.100000 | 2010-04-16 |
| 2006-10-03 12:32:23.677000 | 2006-10-03 |

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
|         4 | 2022-03-22 11:03:02.114000 | 2022-03-22 11:27:25.114000 |
|         6 | 2022-02-08 01:58:28.160000 | 2022-02-08 02:22:05.160000 |
|         3 | 2022-03-24 00:42:38.556000 | 2022-03-24 00:48:43.556000 |
|         2 | 2022-02-26 16:19:53.405000 | 2022-02-26 16:23:34.405000 |
|         4 | 2022-02-04 00:37:18.214000 | 2022-02-04 00:56:24.214000 |

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


