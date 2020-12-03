import os
import subprocess
import tempfile

import pytest

from ..validate import download_and_validate, validate_file


def test_validate_skip():
    validate_yamls = {
        "numpy": {
            "allowed": ["numpy"],
            "files": [
                "lib/python*/site-packages/numpy",
                "lib/python*/site-packages/numpy-*.dist-info",
            ],
        },
    }

    channel_url = "https://conda.anaconda.org/conda-forge"
    subdir_pkg = "osx-64/numpy-1.19.4-py36hcf5569d_1.tar.bz2"
    valid, bad_pths = download_and_validate(
        channel_url,
        subdir_pkg,
        validate_yamls,
        md5sum="c792b85aebf54d48fb3d7597d6688ed6",
    )
    assert valid
    assert bad_pths == {}

    valid, bad_pths = download_and_validate(
        channel_url,
        subdir_pkg,
        validate_yamls,
    )
    assert valid
    assert bad_pths == {}


def test_validate_bad_md5sum():
    validate_yamls = {
        "numpy": {
            "allowed": ["numpy"],
            "files": [
                "lib/python*/site-packages/numpy",
                "lib/python*/site-packages/numpy-*.dist-info",
            ],
        },
    }

    channel_url = "https://conda.anaconda.org/conda-forge"
    subdir_pkg = "osx-64/numpy-1.19.4-py36hcf5569d_1.tar.bz2"
    valid, bad_pths = download_and_validate(
        channel_url,
        subdir_pkg,
        validate_yamls,
        md5sum="c7",
    )
    assert not valid
    assert bad_pths == {'md5sum': {'valid': False}}


@pytest.mark.parametrize(
    "globstr",
    [
        "lib/python*/site-packages/numpy/**/*",
        "lib/python*/site-packages/numpy/**",
        "lib/python*/site-packages/numpy",
        "lib/python*/site-packages/numpy/",
        "lib/python*/site-packages/numpy-*.dist-info/**/*",
        "lib/python2.7/site-packages/numpy",
        "lib/python2.7/site-packages/numpy/polynomial/tests/__init__.pyc",
    ],
)
@pytest.mark.parametrize(
    "subdir_pkg,ok",
    [
        ("linux-aarch64/iminuit-1.5.4-py36h47e6fc7_0.tar.bz2", True),
        # this one is invalid and known to be so
        ("linux-64/freud-0.11.0-py27h3e44d54_0.tar.bz2", False),
    ],
)
def test_validate_glob_dir_file(subdir_pkg, ok, globstr):

    validate_yamls = {
        "numpy": {
            "allowed": ["numpy"],
            "files": [globstr],
        },
    }

    channel_url = "https://conda.anaconda.org/conda-forge"
    valid, bad_pths = download_and_validate(
        channel_url,
        subdir_pkg,
        validate_yamls,
    )
    assert valid is ok
    if ok:
        assert bad_pths == {}
    else:
        assert bad_pths != {}
        assert "numpy" in bad_pths
        print(bad_pths)


@pytest.mark.parametrize(
    "subdir_pkg,ok",
    [
        ("linux-aarch64/iminuit-1.5.4-py36h47e6fc7_0.tar.bz2", True),
        # this one is invalid and known to be so
        ("linux-64/freud-0.11.0-py27h3e44d54_0.tar.bz2", False),
    ],
)
def test_validate_file(subdir_pkg, ok):
    channel_url = "https://conda.anaconda.org/conda-forge"
    validate_yamls = {
        "numpy": {
            "allowed": ["numpy"],
            "files": [
                "lib/python*/site-packages/numpy",
                "lib/python*/site-packages/numpy-*.dist-info",
            ],
        },
    }
    subdir, pkg = os.path.split(subdir_pkg)

    with tempfile.TemporaryDirectory() as dwndir:
        # download
        subprocess.run(
            f"cd {dwndir} && curl -s -L {channel_url}/{subdir_pkg} --output {pkg}",
            shell=True,
        )
        with tempfile.TemporaryDirectory() as updir:
            valid, bad_pths = validate_file(
                os.path.join(dwndir, pkg),
                validate_yamls,
                tmpdir=updir,
            )

    if ok:
        assert valid
        assert bad_pths == {}
    else:
        assert not valid
        assert bad_pths != {}
