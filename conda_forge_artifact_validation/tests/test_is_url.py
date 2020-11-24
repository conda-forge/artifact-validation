import pytest

from ..utils import is_url


@pytest.mark.parametrize('pth,result', [
    ("blah", False),
    ("http://jkhfald", True),
    ("https://jkhfald", True),
    ("c:\\dskfjd;s", False),
    ("file://jkhfald", False),
])
def test_is_url(pth, result):
    assert is_url(pth) is result
