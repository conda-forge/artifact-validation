import os
import subprocess
import tempfile

from ..utils import extract_subdir


def test_extract_subdir():
    url = (
        "https://conda.anaconda.org/conda-forge/"
        "osx-64/numpy-1.19.4-py36hcf5569d_1.tar.bz2"
    )
    pkg = "numpy-1.19.4-py36hcf5569d_1.tar.bz2"
    subdir = "osx-64"
    with tempfile.TemporaryDirectory() as tmpdir:
        # download
        subprocess.run(
            f"cd {tmpdir} && curl -s -L {url} --output {pkg}",
            shell=True,
        )

        assert extract_subdir(os.path.join(tmpdir, pkg)) == subdir
