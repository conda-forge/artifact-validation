from ..utils import chunk_iterable


def test_chunk_iterable():
    lst = []
    chunks = list(chunk_iterable(lst, 0))
    assert sum(len(c) for c in chunks) == 0
    chunks = list(chunk_iterable(lst, 1))
    assert sum(len(c) for c in chunks) == 0
    chunks = list(chunk_iterable(lst, 100))
    assert sum(len(c) for c in chunks) == 0

    lst = list(range(119))
    chunks = list(chunk_iterable(lst, 0))
    assert sum(len(c) for c in chunks) == 119
    assert sum(chunks, []) == list(range(119))
    chunks = list(chunk_iterable(lst, 1))
    assert sum(len(c) for c in chunks) == 119
    assert sum(chunks, []) == list(range(119))
    chunks = list(chunk_iterable(lst, 13))
    assert sum(len(c) for c in chunks) == 119
    assert sum(chunks, []) == list(range(119))

    lst = list(range(101))
    chunks = list(chunk_iterable(lst, 0))
    assert sum(len(c) for c in chunks) == 101
    assert sum(chunks, []) == list(range(101))
    chunks = list(chunk_iterable(lst, 1))
    assert sum(len(c) for c in chunks) == 101
    assert sum(chunks, []) == list(range(101))
    chunks = list(chunk_iterable(lst, 10))
    assert sum(len(c) for c in chunks) == 101
    assert sum(chunks, []) == list(range(101))

    lst = list(range(100))
    chunks = list(chunk_iterable(lst, 0))
    assert sum(len(c) for c in chunks) == 100
    assert sum(chunks, []) == list(range(100))
    chunks = list(chunk_iterable(lst, 1))
    assert sum(len(c) for c in chunks) == 100
    assert sum(chunks, []) == list(range(100))
    chunks = list(chunk_iterable(lst, 10))
    assert sum(len(c) for c in chunks) == 100
    assert sum(chunks, []) == list(range(100))
