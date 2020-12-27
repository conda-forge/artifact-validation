import os
import tempfile
import subprocess
import traceback
import glob
import logging
import shutil

import github
import conda_package_handling.api

from .utils import split_pkg, compute_md5sum

LOGGER = logging.getLogger(__name__)


def _validate_one(validate_yaml, pkg_dir):
    valid = True
    bad_paths = []
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
                valid = False
                bad_paths.append(file)
                break

    return valid, bad_paths


def validate_file(path, validate_yamls, tmpdir=None, lock=None):
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
    lock : threading.Lock or None, optional
        If not None, use this lock to protect calls to `conda_package_handling`.

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

    if lock is not None:
        with lock:
            conda_package_handling.api.extract(path)
    else:
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
                    "bad_paths": sorted(_bad_pths),
                }
        else:
            LOGGER.debug("skipping %s for %s", pkg_nm, validate_name)

    return valid, bad_pths


def download_and_validate(
    channel_url, subdir_pkg, validate_yamls, md5sum=None, lock=None,
):
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
    lock : threading.Lock or None, optional
        If not None, use this lock to protect calls to `conda_package_handling`.

    Returns
    -------
    valid : bool
        True if the package is valid, False otherwise.
    bad_paths : dict
        A dictionary mapping the validation YAML name information in the case
        that the package is not valid.
    """

    _, pkg = subdir_pkg.split(os.path.sep)

    with tempfile.TemporaryDirectory(
        dir=os.environ.get("GITHUB_WORKSPACE", None)
    ) as tmpdir:
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
                        return False, {"md5sum": {"valid": False}}
                    else:
                        LOGGER.info("md5 sum is valid")

                valid, bad_pths = validate_file(
                    f"{tmpdir}/{pkg}",
                    validate_yamls,
                    lock=lock,
                )
            else:
                valid = False
                bad_pths = {}

        except Exception:
            traceback.print_exc()
            valid = False
            bad_pths = {}

    return valid, bad_pths


def bump_team_with_error(
    *,
    feedstock, git_sha, errors, valid, copied,
    artifact_url, bad_pths, job_url
):
    """Make an issue or comment if the artifact validation failed.

    Parameters
    ----------
    feedstock : str
        The name of the feedstock.
    git_sha : str
        The git SHA of the commit.
    errors : list of str
        A list of errors, if any.
    valid : dict
        A dictionary mapping outputs to where or not they were valid for the
        feedstock.
    copied : dict
        A dictionary mapping outputs to whether or not they were copied.
    artifact_url : string
        The artifact being validated.
    bad_pths : dict
        A dictionary of any bad paths in the artifact.
    job_url : string
        A job url to reference.
    """
    if not feedstock.endswith("-feedstock"):
        return None

    gh = github.Github(os.environ['GH_TOKEN'])

    team_name = feedstock[:-len("-feedstock")]

    message = """\
Hi @conda-forge/%s! This is the friendly automated conda-forge-webservice!

It appears that one or more of your feedstock's outputs is either invalid or
did not copy from the staging channel (cf-staging) to the production channel (conda-forge). :(

This failure can happen for a lot of reasons, including an outdated feedstock
token, a feedstock output that is not allowed for that feedstock, or a feedstock output
with files that are not allowed for that output. Below we have put some information
about the failure to help you debug it.

**Rerendering the feedstock will usually fix these problems.**

If you have any issues or questions, you can find us on gitter in the
community [chat room](https://gitter.im/conda-forge/conda-forge.github.io) or you can bump us right here.
""" % team_name  # noqa

    if len(valid) > 0:
        valid_msg = "output validation (is this output allowed for your feedstock?):\n"
        for o, v in valid.items():
            valid_msg += " - **%s**: %s\n" % (o, v)

        message += "\n\n"
        message += valid_msg

    if len(copied) > 0:
        copied_msg = "copied (did this output get copied to the production channel?):\n"
        for o, v in copied.items():
            copied_msg += " - **%s**: %s\n" % (o, v)

        message += "\n\n"
        message += copied_msg

    if len(errors) > 0:
        error_msg = "error messages:\n"
        for err in errors:
            error_msg += " - %s" % err

        message += "\n\n"
        message += error_msg

    if len(bad_pths) > 0:
        bad_pths_msg = (
            "invalid paths in output (mapping of filter to file not allowed):\n"
        )
        for k, v in bad_pths:
            bad_pths_msg += " - **%s**: %s\n" % (k, v["bad_paths"])

        message += "\n\n"
        message += bad_pths_msg

    repo = gh.get_repo("conda-forge/%s" % feedstock)
    issue = None
    for _issue in repo.get_issues(state="all"):
        if (
            (git_sha is not None and git_sha in _issue.title)
            or ("[warning] failed package validation and/or copy" in _issue.title)
        ):
            issue = _issue
            break

    if issue is None:
        if git_sha is not None:
            issue = repo.create_issue(
                "[warning] failed package validation "
                "and/or copy for commit %s" % git_sha,
                body=message,
            )
        else:
            issue = repo.create_issue(
                "[warning] failed package validation and/or copy",
                body=message,
            )
    else:
        if issue.state == "closed":
            issue.edit(state="open")
        issue.create_comment(message)
