from ..utils import split_pkg


def test_split_pkg():
    pkg = "linux-64/python-3.7.6-py37djfa_0.tar.bz2"
    res = split_pkg(pkg)

    assert res == (
        "linux-64",
        "python",
        "3.7.6",
        "py37djfa_0",
    )
