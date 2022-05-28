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
|  0 |                  43 |
|  1 |                 194 |
|  2 |                 129 |
|  3 |                  41 |
|  4 |                  62 |

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
|  0 | 2022-01-02 07:23:00.680000 |
|  1 | 2022-01-02 01:58:51.558000 |
|  2 | 2022-01-01 02:48:55.726000 |
|  3 | 2022-01-01 18:43:30.256000 |
|  4 | 2022-01-02 10:31:23.253000 |

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
|  0 | PDDoBqm      |
|  1 | xaJAunkMD    |
|  2 | qwpZ         |
|  3 | iVUbtCq      |
|  4 | eUZmVyeAZrD  |

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
|  0 | second             |
|  1 | first              |
|  2 | first              |
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
| GBP        | £        |
| EUR        | €        |
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
| USD        | <NA>     |
| USD        | <NA>     |
| EUR        | €        |
| USD        | <NA>     |
| GBP        | <NA>     |

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
| USD        | n/a      |
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
| mymap                       |
|-----------------------------|
| {'id': 233, 'name': 'fA'}   |
| {'id': 117, 'name': 'KTqc'} |
| {'id': 115, 'name': 'wcoM'} |
| {'id': 296, 'name': 'IIEJ'} |
| {'id': 296, 'name': 'Oh'}   |

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
| mymap                    |
|--------------------------|
| {"id":275,"name":"aCy"}  |
| {"id":105,"name":"lUDo"} |
| {"id":209,"name":"oPGv"} |
| {"id":108,"name":"ag"}   |
| {"id":142,"name":"kxsf"} |

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
| {"id":206,"nestedmap":{"balance":5.4,"status":"inactive"}}  |
| {"id":249,"nestedmap":{"balance":6.55,"status":"inactive"}} |
| {"id":236,"nestedmap":{"balance":7.7,"status":"inactive"}}  |
| {"id":138,"nestedmap":{"balance":8.85,"status":"inactive"}} |
| {"id":254,"nestedmap":{"balance":10.0,"status":"inactive"}} |

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
| [45 63]     |
| [43 65]     |
| [37 68]     |
| [31 73]     |
| [33 60]     |

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
|     33 |     58 | [33 58]     |
|     29 |     78 | [29 78]     |
|     35 |     71 | [35 71]     |
|     32 |     62 | [32 62]     |
|     42 |     54 | [42 54]     |

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
|     32 | <NA>   | [32 <NA>]   |
|     49 | 86     | [49 86]     |
|     22 | <NA>   | [22 <NA>]   |
|     34 | <NA>   | [34 <NA>]   |
|     37 | <NA>   | [37 <NA>]   |

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
|     47 | <NA>   | [47]        |
|     34 | <NA>   | [34]        |
|     34 | <NA>   | [34]        |
|     31 | 74     | [31 74]     |
|     48 | <NA>   | [48]        |

---


