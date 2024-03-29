import os
import urllib
import hashlib
import shutil
import tempfile
import json

import conda_package_handling.api


def split_pkg(pkg):
    """Split a subdir + conda package into parts.

    From @isuruf and @CJ-Wright originally.

    Parameters
    ----------
    pkg : str
        The conda package (e.g. `linux-64/python-3.7.6-py37djfa_0.tar.bz2`)

    Returns
    -------
    plat : str
        The platform (e.g., `linux-64`).
    name : str
        The package name (e.g., `python`).
    ver : str
        The version (e.g., `3.7.6`).
    build : str
        The build string (e.g., `py37djfa_0`)
    """
    if pkg.endswith(".tar.bz2"):
        pkg = pkg[:-len(".tar.bz2")]
    elif pkg.endswith(".conda"):
        pkg = pkg[:-len(".conda")]
    else:
        raise RuntimeError("Can only process packages that end in .tar.bz2 or .conda!")
    plat, pkg_name = pkg.split(os.path.sep)
    name_ver, build = pkg_name.rsplit("-", 1)
    name, ver = name_ver.rsplit("-", 1)
    return plat, name, ver, build


def is_url(url):
    """Test if something is a url.

    See https://stackoverflow.com/questions/7849818/argument-is-url-or-path
    """
    return urllib.parse.urlparse(url).scheme in ["http", "https"]


def compute_md5sum(path):
    """Compute the MD5 checksum of a path.

    See https://stackoverflow.com/a/59056837/1745538.
    """

    with open(path, "rb") as fp:
        hash = hashlib.md5()
        chunk = fp.read(8192)
        while chunk:
            hash.update(chunk)
            chunk = fp.read(8192)

    return hash.hexdigest()


def chunk_iterable(iterable, chunk_size):
    """Generate sequences of `chunk_size` elements from `iterable`.
    https://stackoverflow.com/a/12797249/1745538
    """
    chunk_size = max(chunk_size, 1)

    iterable = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(next(iterable))
            yield chunk
        except StopIteration:
            if chunk:
                yield chunk
            break


def extract_subdir(path):
    """Extract the subdir from an artifact."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = str(tmpdir)

        shutil.copy2(path, tmpdir)
        path = os.path.join(tmpdir, path)

        pkg_dir, pkg = os.path.split(path)

        if pkg.endswith(".tar.bz2"):
            pkg_nm = pkg[:-len(".tar.bz2")]
        elif pkg.endswith(".conda"):
            pkg_nm = pkg[:-len(".conda")]
        else:
            raise RuntimeError(
                "Can only process packages that end in .tar.bz2 or .conda!"
            )

        conda_package_handling.api.extract(path)

        try:
            with open(f"{pkg_dir}/{pkg_nm}/info/index.json", "r") as fp:
                subdir = json.load(fp)["subdir"]
        except Exception:
            subdir = None

    return subdir
