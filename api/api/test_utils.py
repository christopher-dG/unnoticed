from .utils import has_mod, accuracy, grade

def test_has_mod():
    assert has_mods({}, "NF") is None

    score = {"enabled_mods": 1}
    assert has_mods(score, "NF") is True
    assert has_mods(score, "HD") is False


def test_accuracy():
    assert accuracy({}) is None


def test_grade():
    assert grade({}) is None
