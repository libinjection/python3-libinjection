#!/usr/bin/env python
"""
API tests for libinjection Python bindings.
Covers the simple sqli() and xss() APIs as well as the stateful sqli API.
"""
import libinjection


def test_sqli_returns_tuple():
    """sqli() should return a (result, fingerprint) sequence."""
    result = libinjection.sqli("1 UNION SELECT * FROM users")
    assert len(result) == 2, "sqli() must return a 2-element sequence (result, fingerprint)"


def test_sqli_detects_injection():
    """sqli() must detect a known SQLi payload."""
    is_sqli, fingerprint = libinjection.sqli("1 UNION SELECT * FROM users")
    assert is_sqli == 1, "Expected SQLi to be detected"
    assert fingerprint != "", "Expected non-empty fingerprint for SQLi input"


def test_sqli_benign_input():
    """sqli() must not flag benign input."""
    is_sqli, fingerprint = libinjection.sqli("hello world")
    assert is_sqli == 0, "Benign input should not be flagged as SQLi"
    assert fingerprint == "", "Benign input should produce an empty fingerprint"


def test_sqli_fingerprint_content():
    """sqli() fingerprint should be a non-empty string for detected SQLi."""
    is_sqli, fingerprint = libinjection.sqli("1 UNION ALL SELECT * FROM foo")
    assert is_sqli == 1
    assert isinstance(fingerprint, str)
    assert len(fingerprint) > 0


def test_is_sqli_stateful_api():
    """Advanced stateful API using sqli_state / sqli_init / sqli_callback / is_sqli."""
    state = libinjection.sqli_state()
    libinjection.sqli_init(
        state,
        "1 UNION SELECT * FROM users",
        libinjection.FLAG_QUOTE_NONE | libinjection.FLAG_SQL_ANSI,
    )
    libinjection.sqli_callback(state, None)
    assert libinjection.is_sqli(state) == 1, "Expected SQLi detection via stateful API"
    assert state.fingerprint != "", "Expected fingerprint set in state"


def test_is_sqli_stateful_benign():
    """Stateful API should not flag benign input."""
    state = libinjection.sqli_state()
    libinjection.sqli_init(
        state,
        "hello world",
        libinjection.FLAG_QUOTE_NONE | libinjection.FLAG_SQL_ANSI,
    )
    libinjection.sqli_callback(state, None)
    assert libinjection.is_sqli(state) == 0, "Benign input should not be SQLi"


def test_xss_detects_script_tag():
    """xss() must detect a basic XSS payload."""
    result = libinjection.xss("<script>alert(1)</script>")
    assert result == 1, "Expected XSS detection for <script> tag"


def test_xss_benign_input():
    """xss() must not flag benign HTML-free input."""
    result = libinjection.xss("hello world")
    assert result == 0, "Benign input should not be flagged as XSS"


def test_xss_detects_event_handler():
    """xss() must detect XSS via event handler attribute."""
    result = libinjection.xss('<img src=x onerror=alert(1)>')
    assert result == 1, "Expected XSS detection for onerror event handler"


def test_version_returns_string():
    """version() must return a non-empty string."""
    v = libinjection.version()
    assert isinstance(v, str), "version() must return a string"
    assert len(v) > 0, "version() must return a non-empty string"
