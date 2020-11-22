"""
code to covert globs to regular expressions
lifted from https://stackoverflow.com/a/63212852/1745538
"""
# flake8: noqa
import re
from sys import hexversion, implementation

# Support for insertion-preserving/ordered dicts became language feature in Python 3.7, but works in CPython since 3.6.
if hexversion >= 0x03070000 or (implementation.name == 'cpython' and hexversion >= 0x03060000):
    ordered_dict = dict
else:
    from collections import OrderedDict as ordered_dict

escaped_glob_tokens_to_re = ordered_dict((
    # Order of ``**/`` and ``/**`` in RE tokenization pattern doesn't matter because ``**/`` will be caught first no matter what, making ``/**`` the only option later on.
    # W/o leading or trailing ``/`` two consecutive asterisks will be treated as literals.
    ('/\*\*', '(?:/.+?)*'), # Edge-case #1. Catches recursive globs in the middle of path. Requires edge case #2 handled after this case.
    ('\*\*/', '(?:^.+?/)*'), # Edge-case #2. Catches recursive globs at the start of path. Requires edge case #1 handled before this case. ``^`` is used to ensure proper location for ``**/``.
    ('\*', '[^/]*?'), # ``[^/]*?`` is used to ensure that ``*`` won't match subdirs, as with naive ``.*?`` solution.
    ('\?', '.'),
    ('\[\*\]', '\*'), # Escaped special glob character.
    ('\[\?\]', '\?'), # Escaped special glob character.
    ('\[!', '[^'), # Requires ordered dict, so that ``\[!`` preceded ``\[`` in RE pattern. Needed mostly to differentiate between ``!`` used within character class ``[]`` and outside of it, to avoid faulty conversion.
    ('\[', '['),
    ('\]', ']'),
))

escaped_glob_replacement = re.compile('(%s)' % '|'.join(escaped_glob_tokens_to_re).replace('\\', '\\\\\\'))

def glob_to_re(pattern):
    return escaped_glob_replacement.sub(lambda match: escaped_glob_tokens_to_re[match.group(0)], re.escape(pattern))
