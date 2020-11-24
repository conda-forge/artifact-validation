"""
tests for converting globs to regular expressions
lifted from https://stackoverflow.com/a/63212852/1745538
"""
import re

import pytest

from ..glob_to_re import glob_to_re


@pytest.mark.parametrize('valid,path,glob_pat', [
    (True, 'foo.py', 'foo.py'),
    (True, 'foo.py', 'fo[o].py'),
    (True, 'fob.py', 'fo[!o].py'),
    (True, '*foo.py', '[*]foo.py'),
    (True, 'foo.py', '**/foo.py'),
    (True, 'baz/duck/bar/bam/quack/foo.py', '**/bar/**/foo.py'),
    (True, 'bar/foo.py', '**/foo.py'),
    (True, 'bar/baz/foo.py', 'bar/**'),
    (False, 'bar/baz/foo.py', 'bar/*'),
    (False, 'bar/baz/foo.py', 'bar**/foo.py'),
    (True, 'bar/baz/foo.py', 'bar/**/foo.py'),
    (True, 'bar/baz/wut/foo.py', 'bar/**/foo.py'),
])
def test_glob_to_re(valid, path, glob_pat):
    re_pat = glob_to_re(glob_pat)
    match = re.fullmatch(re_pat, path)
    if valid:
        assert match is not None
    else:
        assert match is None
