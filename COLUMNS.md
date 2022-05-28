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
  

- [Array](#array) - Builds an array from the specified `source_columns:`.
  -  [Simple Array with primitive types](#array1)
  -  [Use of `drop: False`](#array2)
  -  [With nulls in `source_columns:`](#array3)
  -  [Use of `drop_nulls: True`](#array4)
  

- [ExtractDate](#extractdate) - Extracts a date from a timestamp `source_column:`
  -  [Simple ExtractDate](#extractdate1)
  -  [ExtractDate with custom formatting](#extractdate2)
  -  [ExtractDate to an Int](#extractdate3)
  




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
|  0 |                 126 |
|  1 |                 172 |
|  2 |                  93 |
|  3 |                  95 |
|  4 |                 136 |

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
|  0 | 2022-01-02 09:29:39.611000 |
|  1 | 2022-01-01 20:00:46.763000 |
|  2 | 2022-01-02 01:15:53.421000 |
|  3 | 2022-01-02 03:04:37.731000 |
|  4 | 2022-01-02 03:21:22.376000 |

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
|  0 | KwfdIAuGA    |
|  1 | SoMigZAOk    |
|  2 | KaSyDuhXqkE  |
|  3 | LWafhzwoJlH  |
|  4 | RhWekoeG     |

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
|  2 | first              |
|  3 | second             |
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
|  1 | EUR                  |
|  2 | USD                  |
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
| EUR        | €        |
| USD        | $        |
| EUR        | €        |
| GBP        | £        |
| EUR        | €        |

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
| EUR        | €        |
| EUR        | €        |
| GBP        | n/a      |
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
| {'id': 259, 'name': 'PvO'}   |
| {'id': 171, 'name': 'bifmH'} |
| {'id': 278, 'name': 'Dxh'}   |
| {'id': 200, 'name': 'GMIU'}  |
| {'id': 182, 'name': 'MPn'}   |

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
| {"id":298,"name":"ExcE"}  |
| {"id":172,"name":"GeTYE"} |
| {"id":186,"name":"FuS"}   |
| {"id":262,"name":"hvQMd"} |
| {"id":234,"name":"fMaVq"} |

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
| {"id":167,"nestedmap":{"balance":5.4,"status":"inactive"}}  |
| {"id":144,"nestedmap":{"balance":6.55,"status":"active"}}   |
| {"id":196,"nestedmap":{"balance":7.7,"status":"inactive"}}  |
| {"id":159,"nestedmap":{"balance":8.85,"status":"active"}}   |
| {"id":205,"nestedmap":{"balance":10.0,"status":"inactive"}} |

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
| [29 70]     |
| [31 56]     |
| [39 65]     |
| [42 67]     |
| [32 78]     |

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
|     47 |     87 | [47 87]     |
|     24 |     53 | [24 53]     |
|     27 |     73 | [27 73]     |
|     49 |     88 | [49 88]     |
|     36 |     69 | [36 69]     |

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
|     47 | <NA>   | [47 <NA>]   |
|     24 | <NA>   | [24 <NA>]   |
|     40 | 56     | [40 56]     |
|     21 | <NA>   | [21 <NA>]   |
|     39 | <NA>   | [39 <NA>]   |

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
|     36 | 69     | [36 69]     |
|     37 | <NA>   | [37]        |
|     39 | <NA>   | [39]        |
|     37 | <NA>   | [37]        |
|     20 | <NA>   | [20]        |

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
| 2022-02-28 15:05:34.782000 | 2022-02-28 |
| 2022-03-16 23:38:57.914000 | 2022-03-16 |
| 2022-03-14 14:10:41.136000 | 2022-03-14 |
| 2022-02-05 18:15:05.382000 | 2022-02-05 |
| 2022-03-24 02:22:29.786000 | 2022-03-24 |

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
| event_time                 | day_of_month           |
|----------------------------|------------------------|
| 2022-03-30 08:57:45.677000 | A Wednesday in March   |
| 2022-03-20 05:59:27.461000 | A Sunday in March      |
| 2022-03-02 23:23:36.551000 | A Wednesday in March   |
| 2022-02-18 00:23:32.406000 | A Friday in February   |
| 2022-02-19 02:47:16.570000 | A Saturday in February |

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
| 2003-01-01 12:08:42.781000 |   2003 |
| 2004-11-27 03:59:38.491000 |   2004 |
| 2006-06-03 09:50:21.590000 |   2006 |
| 2010-05-26 04:58:22.983000 |   2010 |
| 2001-12-03 23:12:02.674000 |   2001 |

---


