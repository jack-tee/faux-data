# Columns


- [Selection](#selection) - Generates columns by selecting random values


- [Random](#random) - Generates columns of random data


- [Sequential](#sequential) - Generates a column by incrementing a field from a `start:` by a `step:` for each row.


- [Fixed](#fixed) - Generates a column with a single fixed value


- [Empty](#empty) - Generates and empty (null) column of data





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
|  0 | second             |
|  1 | first              |
|  2 | second             |
|  3 | second             |
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
|  0 | EUR                  |
|  1 | USD                  |
|  2 | EUR                  |
|  3 | USD                  |
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
|  0 |                 125 |
|  1 |                 118 |
|  2 |                   9 |
|  3 |                  38 |
|  4 |                 191 |

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
|  0 | 2022-01-01 10:38:31.781000 |
|  1 | 2022-01-01 11:39:06.962000 |
|  2 | 2022-01-01 18:19:04.943000 |
|  3 | 2022-01-01 06:43:15.580000 |
|  4 | 2022-01-02 00:13:44.657000 |

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
|  0 | HaJrstsAM    |
|  1 | PmLh         |
|  2 | TguhPNvxz    |
|  3 | wOSvEUr      |
|  4 | AyFQI        |

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



They can also be used for timestamps

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


