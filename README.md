# python3-libinjection
libInjection Python3 bindings

## Overview

Python3 bindings for [libinjection](https://github.com/libinjection/libinjection) - a SQL/SQLI tokenizer, parser and analyzer.

## Requirements

- Python 3.x
- SWIG 4.x
- GCC or compatible C compiler

## Building

### 1. Clone the repository and get upstream libinjection

```bash
git clone https://github.com/libinjection/python3-libinjection.git
cd python3-libinjection
make upstream
```

### 2. Copy upstream C source files

```bash
make libinjection/libinjection.h libinjection/libinjection_sqli.h libinjection/libinjection_error.h
```

### 3. Generate the SWIG wrapper

```bash
swig -python -builtin -Wall -Wextra libinjection/libinjection.i
```

### 4. Build the Python extension

```bash
python3 setup.py build_ext --inplace
```

Or using the Makefile:

```bash
make build
```

### 5. Generate the word lookup table (needed for tests)

```bash
python3 json2python.py < upstream/src/sqlparse_data.json > words.py
```

## Usage

### SQLi Detection

```python
import libinjection

# Simple API - detect SQLi in a string
result, fingerprint = libinjection.sqli("1 UNION SELECT * FROM users")
if result:
    print(f"SQLi detected! Fingerprint: {fingerprint}")

# Advanced API with state object
state = libinjection.sqli_state()
libinjection.sqli_init(state, "1 UNION SELECT * FROM users",
                       libinjection.FLAG_QUOTE_NONE | libinjection.FLAG_SQL_ANSI)
libinjection.sqli_callback(state, None)
if libinjection.is_sqli(state):
    print(f"SQLi detected! Fingerprint: {state.fingerprint}")
```

### XSS Detection

```python
import libinjection

# Detect XSS in a string
result = libinjection.xss("<script>alert(1)</script>")
if result:
    print("XSS detected!")
```

## Testing

Run the test suite using pytest:

```bash
cd /tmp  # run from outside the repo directory to avoid pytest.py conflict
python3 -m pytest /path/to/python3-libinjection/test_driver.py -v
```
