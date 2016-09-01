import pytest

from math_utils import rolling_average


def test_window_1_is_identity():
    lst = range(5)
    assert lst == list(rolling_average(lst, window=1))


def test_rolling_avg():
    lst = [1, 0, 1, 0, 1, 0]
    result = list(rolling_average(lst, window=2))
    assert result == [0.5] * (len(lst) - 1)


def test_avg_whole_list():
    lst = [0, 1, 2, 3]
    result = list(rolling_average(lst, len(lst)))
    assert result == [1.5]


def test_rolling_avg_too_small_list():
    lst = [0, 1, 2, 3]

    with pytest.raises(ValueError):
        rolling_average(lst, len(lst) + 1)
