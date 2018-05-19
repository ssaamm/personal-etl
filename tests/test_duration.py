import pytest

from utils.duration import Duration


@pytest.mark.parametrize('a,b,expected', [
    [Duration(1, 1, 1), Duration(3, 3, 3), Duration(4, 4, 4)],
    [Duration(0, 0, 1), Duration(0, 0, 59), Duration(0, 1, 0)],
    [Duration(0, 1, 0), Duration(0, 59, 0), Duration(1, 0, 0)],
    [Duration(0, 1, 1), Duration(0, 59, 59), Duration(1, 1, 0)],
    [Duration(0, 120, 0), Duration(0, 0, 120), Duration(2, 2, 0)],
    [Duration(0, 120, 0), Duration(0, 0, 123), Duration(2, 2, 3)],
])
def test_addition(a, b, expected):
    result = a + b
    assert result == expected


@pytest.mark.parametrize('d,r', [
    [Duration(0, 0, 410), '0:06:50'],
    [Duration(1, 1, 1), '1:01:01'],
])
def test_repr(d, r):
    assert repr(d) == r
