# Columns


- [MapValues](#mapvalues) - Maps the values in one column to values in another

- [Map](#map) - Map columns create a record style field from other fields

- [Selection](#selection) - Generates columns by selecting random values

- [Random](#random) - Generates columns of random data

- [Sequential](#sequential) - Generates a column by incrementing a field from a `start:` by a `step:` for each row.

- [Fixed](#fixed) - Generates a column with a single fixed value

- [Empty](#empty) - Generates and empty (null) column of data

- [Series](#series) - Repeats a series of values to fill a column




## MapValues

A MapValues column

### Examples


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
| EUR        | €        |
| GBP        | £        |
| EUR        | €        |
| GBP        | £        |

---




## Map

A Map column

### Examples


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
| {'id': 177, 'name': 'hv'}   |
| {'id': 281, 'name': 'Dy'}   |
| {'id': 164, 'name': 'QLcR'} |
| {'id': 197, 'name': 'HlP'}  |
| {'id': 201, 'name': 'jQY'}  |

---



If you want a valid json field specify `json: True`.

Template:
```
name: mytbl
rows: 5
columns:
  - col: mymap Map
    json: True
    columns:
      - col: id Random Int 100 300
      - col: name Random String 2 5
```

Result:
| mymap                     |
|---------------------------|
| {"id":225,"name":"axv"}   |
| {"id":143,"name":"uZ"}    |
| {"id":246,"name":"pDci"}  |
| {"id":227,"name":"DNt"}   |
| {"id":178,"name":"FNfPZ"} |

---



Similarly you can nest to any depth by adding Map columns within Map columns.

Template:
```
name: mytbl
rows: 5
columns:
  - col: mymap Map
    json: True
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
| {"id":233,"nestedmap":{"balance":5.4,"status":"inactive"}}  |
| {"id":233,"nestedmap":{"balance":6.55,"status":"active"}}   |
| {"id":234,"nestedmap":{"balance":7.7,"status":"inactive"}}  |
| {"id":235,"nestedmap":{"balance":8.85,"status":"active"}}   |
| {"id":278,"nestedmap":{"balance":10.0,"status":"inactive"}} |

---




## Selection

A selection column


### Examples


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
|  1 | second             |
|  2 | second             |
|  3 | first              |
|  4 | first              |

---



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
|  2 | USD                  |
|  3 | EUR                  |
|  4 | USD                  |

---




## Random

A Random column


### Examples


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
|  0 |                  52 |
|  1 |                  18 |
|  2 |                  68 |
|  3 |                 105 |
|  4 |                  41 |

---



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
|  0 | 2022-01-01 03:33:31.786000 |
|  1 | 2022-01-01 12:37:18.726000 |
|  2 | 2022-01-01 16:53:12.742000 |
|  3 | 2022-01-01 08:56:54.167000 |
|  4 | 2022-01-01 13:43:53.218000 |

---



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
|  0 | hDWJFiIny    |
|  1 | xigC         |
|  2 | sMTaNqPeXOQ  |
|  3 | pCYmyEnHXw   |
|  4 | AwJpd        |

---




## Sequential

A Sequential column

### Examples


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

---



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

---




## Fixed

A Fixed column

### Examples


None

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




## Series

A Series column

### Examples


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

---


