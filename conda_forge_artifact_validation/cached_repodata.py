import functools
from collections import UserDict

import requests

SUBDIRS = [
    "linux-64", "osx-64", "noarch", "win-64",
    "linux-ppc64le", "linux-aarch64", "osx-arm64",
]
CHANNEL_URL = "https://conda.anaconda.org/conda-forge"


@functools.lru_cache(maxsize=16)
def _load_repodata(subdir):
    for i in range(10):
        try:
            rd = requests.get(
                f"{CHANNEL_URL}/{subdir}/repodata.json"
            )
            rd.raise_for_status()
            break
        except Exception:
            if i == 9:
                raise
            else:
                pass
    return rd.json()


class RepodataCache(UserDict):
    """A cache of repodata.

    You can access the repodata via

    >>> repodata_cache["linux-64"]
    {"packages": {...}}

    """
    def __init__(self):
        super().__init__()

    def __getitem__(self, index):
        if index not in self.data:
            self[index] = _load_repodata(index)

        return self.data[index]


REPODATA_CACHE = RepodataCache()
