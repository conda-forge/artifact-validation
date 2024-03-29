import os
import requests
import re
import logging

import joblib

from .glob_to_re import glob_to_re
from .cached_repodata import REPODATA_CACHE

LOGGER = logging.getLogger(__name__)

# holds the libcfgraph file index - used for finding out which possible
# files there are to download
LIBCFGRAPH_INDEX = None

# this is a default exclude set for a python package
DEFAULT_PYTHON_GLOBS = [
    "Lib/site-packages/{import_name}/**/*",
    "Lib/site-packages/{import_name}-*.dist-info/**/*",
    "Lib/site-packages/{import_name}-*.egg",
    "Lib/site-packages/{import_name}-*.egg-info",
    "Lib/site-packages/{import_name}-*.egg-info/**/*",
    "site-packages/{import_name}-*.dist-info/**/*",
    "site-packages/{import_name}-*.egg-info/**/*",
    "site-packages/{import_name}/**/*",
    "lib/python*/site-packages/{import_name}/**/*",
    "lib/python*/site-packages/{import_name}-*.dist-info/**/*",
    "lib/python*/site-packages/{import_name}-*.egg",
    "lib/python*/site-packages/{import_name}-*.egg-info",
    "lib/python*/site-packages/{import_name}-*.egg-info/**/*",
]

DEFAULT_PYTHON_EXCLUDES = [
    # these files appear to be made when 2to3 was used on windows
    # any package can write them
    "Lib/lib2to3/**/*",
    # this file is made by cross-python on some cross-compile builds
    "bin/python.bak",
]


def _get_subdir_pkg_from_libcfgraph_artifact(artifact_pth, tail):
    subdir_pkg = "/".join(artifact_pth.split('/')[-2:])
    if subdir_pkg.endswith(".json"):
        subdir_pkg = subdir_pkg[:-len(".json")] + tail

    subdir, pkg = os.path.split(subdir_pkg)
    return subdir, pkg


def _download_libcfgraph_index():
    global LIBCFGRAPH_INDEX
    r = requests.get(
        "https://raw.githubusercontent.com/regro/libcfgraph"
        "/master/.file_listing_meta.json",
    )
    r.raise_for_status()
    n_files = r.json()["n_files"]
    LIBCFGRAPH_INDEX = []
    for i in range(n_files):
        r = requests.get(
            "https://raw.githubusercontent.com/regro/libcfgraph"
            "/master/.file_listing_%d.json" % i,
        )
        r.raise_for_status()
        LIBCFGRAPH_INDEX += r.json()


def _get_all_json_blobs_for_artifact(artifact_name, verbose=0):
    """Given the name of a conda package, download all libcfgraph entries for it."""
    global LIBCFGRAPH_INDEX
    if LIBCFGRAPH_INDEX is None:
        _download_libcfgraph_index()

    sentinel = os.path.join("artifacts", artifact_name) + "/"
    artifact_pths = [pth for pth in LIBCFGRAPH_INDEX if pth.startswith(sentinel)]

    def _download_jsob_blob(artifact_pth, tail):
        # ignore things not on the main channel
        subdir, pkg = _get_subdir_pkg_from_libcfgraph_artifact(artifact_pth, tail)
        if pkg not in REPODATA_CACHE[subdir]["packages"]:
            return None

        try:
            r = requests.get(
                "https://raw.githubusercontent.com/regro/libcfgraph/master/"
                f"{artifact_pth}"
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    jobs = []
    for artifact_pth in artifact_pths:
        for tail in [".tar.bz2", ".conda"]:
            jobs.append(joblib.delayed(_download_jsob_blob)(artifact_pth, tail))

    artifacts = joblib.Parallel(n_jobs=5, backend="threading", verbose=verbose)(jobs)

    return [a for a in artifacts if a is not None]


def generate_validate_yaml_from_libcfgraph(
    artifact_name, exclude_globs=None, verbose=0
):
    """Generate a validation YAML file from an artifact using libcfgraph.

    This function uses libcfgraph (https://raw.githubusercontent.com/regro/libcfgraph)
    to collect all files provided by any version of a given artifact. It then figures
    out which ones would be caught by the `exclude_globs`, if any. It then returns
    a validation YAML file with the file paths not caught. Note that if libcfgraph is
    missing artifacts, then paths from those artifacts will not appear.

    Parameters
    ----------
    artifact_name : str
        The name of the artifact (e.g., `numpy`).
    exclude_globs : list of str, optional
        If given, any file in artifact that would be matched by any of the glob
        patterns will be excluded.
    verbose : int, optional
        Integer between 0 and 100. Passed to joblib. Zero produces no output (default)
        and 100 produces the maximum amount of output.

    Returns
    -------
    validate_yaml : dict
        A dictionary with the contents of the validate YAML file.
    """
    exclude_globs = exclude_globs or []

    # turn the globs into regular expressions
    re_patts = [glob_to_re(patt) for patt in exclude_globs]
    re_patt_comps = [re.compile(re_patt) for re_patt in re_patts]
    LOGGER.debug("using %s regexes for %s", re_patt_comps, artifact_name)

    # get all json blobs for artifact
    blobs = _get_all_json_blobs_for_artifact(artifact_name, verbose=verbose)
    LOGGER.debug("found %s json blobs for %s", len(blobs), artifact_name)

    # now find any files not matched by the excluide_globs, if any
    files_to_add = set()
    for a in blobs:
        for f in a.get("files", []):
            if re_patt_comps:
                if all(
                    re_patt_comp.fullmatch(f) is None for re_patt_comp in re_patt_comps
                ):
                    files_to_add.add(f)
            else:
                files_to_add.add(f)

    return {"files": sorted(list(files_to_add)), "allowed": [artifact_name]}


def generate_validate_yaml_for_python(
    artifact_name,
    top_level_imports,
    allowed=None,
    exclude_files=None,
    verbose=0,
):
    """Generate a validation YAML file from an artifact that is a python package.

    This function works in two stages.

    1. It uses a default set of globs for python installations.
    2. It calls `generate_validate_yaml_from_artifact` to get any other possible files
       to include.

    Parameters
    ----------
    artifact_name : str
        The name of the artifact (e.g., `numpy`).
    top_level_imports : list of str
        A list of top-level imports (e.g., `[numpy,]` for numpy).
    allowed : list of str
        If not None, this set of artifacts will also be allowed to output files
        to the paths from `artifact_name` in addition to `artifact_name`. If not set,
        then only `artifact_name` will be allowed.
    exclude_files : list of str
        Any files matching these glob patterns will not be added to the list of
        files in the outputs.
    verbose : int, optional
        Integer between 0 and 100. Passed to joblib. Zero produces no output (default)
        and 100 produces the maximum amount of output.

    Returns
    -------
    validate_yaml : dict
        A dictionary with the contents of the validate YAML file.
    """
    allowed = allowed or []
    exclude_files = exclude_files or []

    # add in the defaults that any python package is allowed to write
    exclude_files += DEFAULT_PYTHON_EXCLUDES

    # first make the default globs
    default_globs = []
    for import_name in top_level_imports:
        for tmp_str in DEFAULT_PYTHON_GLOBS:
            default_globs.append(tmp_str.format(import_name=import_name))

    validate_yaml = generate_validate_yaml_from_libcfgraph(
        artifact_name,
        exclude_globs=default_globs + exclude_files,
        verbose=verbose,
    )

    validate_yaml["files"].extend(default_globs)
    for allow in allowed + [artifact_name]:
        validate_yaml["allowed"].append(allow)

    for key in ["files", "allowed"]:
        validate_yaml[key] = sorted(list(set(validate_yaml[key])))

    return validate_yaml
