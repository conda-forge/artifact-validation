import functools
from collections import UserDict

import tenacity
import requests

SUBDIRS = [
    "linux-64", "osx-64", "noarch", "win-64",
    "linux-ppc64le", "linux-aarch64", "osx-arm64",
]
CHANNEL_URL = "https://conda.anaconda.org/conda-forge"


@tenacity.retry(
    wait=tenacity.wait_random_exponential(multiplier=1, max=10),
    stop=tenacity.stop_after_attempt(5),
    reraise=True,
)
def _load_repodata_retry(subdir):
    rd = requests.get(
        f"{CHANNEL_URL}/{subdir}/repodata.json"
    )
    rd.raise_for_status()
    return rd.json()


@functools.lru_cache(maxsize=16)
def _load_repodata(subdir):
    return _load_repodata_retry(subdir)


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
