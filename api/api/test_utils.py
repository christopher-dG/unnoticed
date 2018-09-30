import datetime

from .utils import has_mod, accuracy, grade


def test_from_winticks():
    pass


def test_has_mod():
    assert has_mods({}, "NF") is None

    score = {"enabled_mods": 1}
    assert has_mods(score, "NF") is True
    assert has_mods(score, "HD") is False


def test_osu_id():
    pass


def test_get_int():
    pass


def test_stringify():
    d = {"a": "foo", "b": 2, "c": 3.4, "d": datetime.datetime(2000, 1, 2, 3, 4, 5)}

    assert _stringify(d) == {
        "a": "foo",
        "b": "2",
        "c": "3.4",
        "d": "2000-01-02 03:04:05",
    }


def test_response():
    pass


def test_accuracy():
    assert accuracy({}) is None


def test_grade():
    assert grade({}) is None
