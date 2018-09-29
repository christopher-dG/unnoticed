import datetime

from .handlers import _stringify


def test_stringify():
    d = {"a": "foo", "b": 2, "c": 3.4, "d": datetime.datetime(2000, 1, 2, 3, 4, 5)}

    assert _stringify(d) == {
        "a": "foo",
        "b": "2",
        "c": "3.4",
        "d": "2000-01-02 03:04:05",
    }
