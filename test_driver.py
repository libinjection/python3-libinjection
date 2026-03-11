#!/usr/bin/env python
"""
Test driver
Runs off plain text files, similar to how PHP's test harness works
"""
import os
import glob
from libinjection import *
from words import *

# Test data is in upstream/tests/ relative to this script's directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_TESTS_DIR = os.path.join(_SCRIPT_DIR, 'upstream', 'tests')

print(version())

def print_token_string(tok):
    """
    returns the value of token, handling opening and closing quote characters
    """
    out = ''
    if tok.str_open != "\0":
        out += tok.str_open
    out += tok.val
    if tok.str_close != "\0":
        out += tok.str_close
    return out

def print_token(tok):
    """
    prints a token for use in unit testing
    """
    out = ''
    out += tok.type
    out += ' '
    if tok.type == 's':
        out += print_token_string(tok)
    elif tok.type == 'v':
        vc = tok.count;
        if vc == 1:
            out += '@'
        elif vc == 2:
            out += '@@'
        out += print_token_string(tok)
    else:
        out += tok.val
    return out.rstrip('\r\n')

def toascii(data):
    """
    Converts a utf-8 string to ascii.   needed since nosetests xunit is not UTF-8 safe
    https://github.com/nose-devs/nose/issues/649
    https://github.com/nose-devs/nose/issues/692
    """
    return data
    udata = data.decode('utf-8')
    return udata.encode('ascii', 'xmlcharrefreplace')

def readtestdata(filename):
    """
    Read a test file and split into components.
    Returns the input as bytes to preserve non-ASCII characters exactly
    (e.g. 0xA0 word separators) when passed to the C tokenizer.
    """

    state = None
    info = {
        b'--TEST--': b'',
        b'--INPUT--': b'',
        b'--EXPECTED--': b''
        }

    for line in open(filename, 'rb'):
        line = line.rstrip(b'\r\n')
        if line in info:
            state = line
        elif state:
            info[state] += line + b'\n'

    # remove last newline from input
    info[b'--INPUT--'] = info[b'--INPUT--'][:-1]

    return (
        info[b'--TEST--'].decode('utf-8', errors='replace'),
        info[b'--INPUT--'],   # kept as bytes for exact byte semantics
        info[b'--EXPECTED--'].decode('utf-8').strip()
    )

def runtest(testname, flag, sqli_flags):
    """
    runs a test, optionally with valgrind
    """
    data =  readtestdata(os.path.join(_TESTS_DIR, testname))

    sql_state = sqli_state()
    sqli_init(sql_state, data[1], sqli_flags)
    sqli_callback(sql_state, lookup)
    actual = ''

    if flag == 'tokens':
        while sqli_tokenize(sql_state):
            actual += print_token(sql_state.current) + '\n';
        actual = actual.strip()
    elif flag == 'folding':
        num_tokens = sqli_fold(sql_state)
        for i in range(num_tokens):
            actual += print_token(sqli_get_token(sql_state, i)) + '\n';
    elif flag == 'fingerprints':
        ok = is_sqli(sql_state)
        if ok:
            actual = sql_state.fingerprint
    else:
        raise RuntimeException("unknown flag")

    actual = actual.strip()

    if actual != data[2]:
        input_display = data[1].decode('latin-1') if isinstance(data[1], bytes) else data[1]
        print("INPUT: \n" + toascii(input_display))
        print()
        print("EXPECTED: \n" + toascii(data[2]))
        print()
        print("GOT: \n" + toascii(actual))
        assert actual == data[2]

def test_tokens():
    for testname in sorted(glob.glob(os.path.join(_TESTS_DIR, 'test-tokens-*.txt'))):
        testname = os.path.basename(testname)
        runtest(testname, 'tokens', libinjection.FLAG_QUOTE_NONE | libinjection.FLAG_SQL_ANSI)

def test_tokens_mysql():
    for testname in sorted(glob.glob(os.path.join(_TESTS_DIR, 'test-tokens_mysql-*.txt'))):
        testname = os.path.basename(testname)
        runtest(testname, 'tokens', libinjection.FLAG_QUOTE_NONE | libinjection.FLAG_SQL_MYSQL)

def test_folding():
    for testname in sorted(glob.glob(os.path.join(_TESTS_DIR, 'test-folding-*.txt'))):
        testname = os.path.basename(testname)
        runtest(testname, 'folding', libinjection.FLAG_QUOTE_NONE | libinjection.FLAG_SQL_ANSI)

def test_fingerprints():
    for testname in sorted(glob.glob(os.path.join(_TESTS_DIR, 'test-sqli-*.txt'))):
        testname = os.path.basename(testname)
        runtest(testname, 'fingerprints', 0)


if __name__ == '__main__':
    import sys
    sys.stderr.write("run using pytest\n")
    sys.exit(1)
