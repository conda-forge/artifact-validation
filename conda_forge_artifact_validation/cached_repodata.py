from collections import UserDict

import requests

SUBDIRS = [
    "linux-64", "osx-64", "noarch", "win-64",
    "linux-ppc64le", "linux-aarch64", "osx-arm64",
]
CHANNEL_URL = "https://conda.anaconda.org/conda-forge"


class RepodataCache(UserDict):
    """A cache of repodata.

    You can access the repodata via

    >>> repodata_cache["linux-64"]
    {"packages": {...}}

    """
    def __init__(self):
        super().__init__()

        for subdir in SUBDIRS:
            rd = requests.get(
                f"{CHANNEL_URL}/{subdir}/repodata.json"
            )
            rd.raise_for_status()
            self[subdir] = rd.json()
