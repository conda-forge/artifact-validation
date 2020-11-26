import os
import tempfile
import subprocess
import traceback
import glob
import logging
import shutil

import conda_package_handling.api

from .utils import split_pkg, compute_md5sum

LOGGER = logging.getLogger(__name__)


def _validate_one(validate_yaml, pkg_dir):
    for file in validate_yaml["files"]:
        pkg_dir_file = os.path.join(pkg_dir, file)
        LOGGER.debug("pkg_dir/file: %s", pkg_dir_file)

        if "*" in file:
            pths = glob.glob(pkg_dir_file, recursive=True)
        else:
            pths = [pkg_dir_file]

        LOGGER.debug("paths to be checked: %s", pths)

        for pth in pths:
            if os.path.exists(pth):
                return False, [pth.replace(pkg_dir, "$PREFIX")]

    return True, []


def validate_file(path, validate_yamls, tmpdir=None):
    """Validate a file on disk.

    Parameters
    ----------
    path : str
        The path to the file.
    validate_yamls : dict
        A dictionary mapping the filename of the validation yaml to its
        contents.
    tmpdir : str, optional
        If not None, copy the data to this location before unpacking it.

    Returns
    -------
    valid : bool
        True if the package is valid, False otherwise.
    bad_paths : dict
        A dictionary mapping the validation YAML name information in the case
        that the package is not valid.
    """
    valid = True
    bad_pths = {}

    if tmpdir is not None:
        shutil.copy2(path, tmpdir)
        path = os.path.join(tmpdir, path)

    pkg_dir, pkg = os.path.split(path)
    # hacking here to get the output name by adding a fake subdir
    _, output_name, _, _ = split_pkg(os.path.join("foo", pkg))

    if pkg.endswith(".tar.bz2"):
        pkg_nm = pkg[: -len(".tar.bz2")]
    else:
        pkg_nm = pkg[: -len(".conda")]

    conda_package_handling.api.extract(path)

    for validate_name, validate_yaml in validate_yamls.items():
        if output_name not in validate_yaml["allowed"]:
            _valid, _bad_pths = _validate_one(
                validate_yaml,
                f"{pkg_dir}/{pkg_nm}",
            )
            valid = valid and _valid
            if not _valid:
                bad_pths[validate_name] = {
                    "valid": _valid,
                    "bad_paths": sorted(_bad_pths),
                }
        else:
            LOGGER.debug("skipping %s for %s", pkg_nm, validate_name)

    return valid, bad_pths


def download_and_validate(channel_url, subdir_pkg, validate_yamls, md5sum=None):
    """Download and validate a package.

    Parameters
    ----------
    channel_url : str
        The URL for the conda channel.
    subdir_pkg : str
        The fully qualified path of the package (e.g. "linux-64/numpy-...").
    validate_yamls : dict
        A dictionary mapping the filename of the validation yaml to its
        contents.
    md5sum : str
        If not None, then checksum the downloaded file with md5 before we validate.

    Returns
    -------
    valid : bool
        True if the package is valid, False otherwise.
    bad_paths : dict
        A dictionary mapping the validation YAML name information in the case
        that the package is not valid.
    """

    _, pkg = subdir_pkg.split(os.path.sep)

    with tempfile.TemporaryDirectory(dir=os.environ.get("RUNNER_TEMP")) as tmpdir:
        try:
            # download
            subprocess.run(
                f"cd {tmpdir} && curl -s -L {channel_url}/{subdir_pkg} --output {pkg}",
                shell=True,
            )

            # unpack and validate
            if os.path.exists(f"{tmpdir}/{pkg}"):
                if md5sum is not None:
                    if md5sum != compute_md5sum(f"{tmpdir}/{pkg}"):
                        LOGGER.info("bad md5sum")
                        return False, {}
                    else:
                        LOGGER.info("md5 sum is valid")

                valid, bad_pths = validate_file(f"{tmpdir}/{pkg}", validate_yamls)
            else:
                valid = False
                bad_pths = {}

        except Exception:
            traceback.print_exc()
            valid = False
            bad_pths = {}

    return valid, bad_pths
