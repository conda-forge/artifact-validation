from ..generate_validate_yamls import (
    generate_validate_yaml_for_python,
    generate_validate_yaml_from_libcfgraph,
    _get_subdir_pkg_from_libcfgraph_artifact,
)


def test_get_subdir_pkg_from_libcfgraph_artifact():
    subdir, pkg = _get_subdir_pkg_from_libcfgraph_artifact(
        "artifacts/foo/conda-forge/osx-64/foo.json"
    )
    assert subdir == "osx-64"
    assert pkg == "foo.tar.bz2"


def test_generate_validate_yaml_from_libcfgraph():
    validate_yaml = generate_validate_yaml_from_libcfgraph(
        "des-desmeds",
        verbose=100,
    )

    assert validate_yaml["allowed"] == ["des-desmeds"]
    for fname in [
        "bin/desmeds-prep-tile",
        "bin/desmeds-rsync-meds-srcs",
        "lib/python3.9/site-packages/desmeds-0.9.9.dist-info/INSTALLER",
    ]:
        assert fname in validate_yaml["files"]


def test_generate_validate_yaml_from_libcfgraph_exclude():
    validate_yaml = generate_validate_yaml_from_libcfgraph(
        "des-desmeds",
        verbose=100,
        exclude_globs=["lib/python3.9/site-packages/**/*"],
    )

    assert validate_yaml["allowed"] == ["des-desmeds"]
    for fname in [
        "lib/python3.9/site-packages/desmeds-0.9.9.dist-info/INSTALLER",
        "lib/python3.9/site-packages/**/*",
    ]:
        assert fname not in validate_yaml["files"]

    for fname in [
        "bin/desmeds-prep-tile",
        "bin/desmeds-rsync-meds-srcs",
    ]:
        assert fname in validate_yaml["files"]


def test_generate_validate_yaml_for_python():
    validate_yaml = generate_validate_yaml_for_python(
        "des-desmeds",
        ["desmeds", "blah"],
        allowed=["blah"],
        verbose=100,
    )

    assert validate_yaml["allowed"] == ["blah", "des-desmeds"]
    for fname in [
        "bin/desmeds-prep-tile",
        "bin/desmeds-rsync-meds-srcs",
    ]:
        assert fname in validate_yaml["files"]

    assert (
        "lib/python2.7/site-packages/desmeds/__init__.py"
        not in validate_yaml["files"]
    )
    assert "lib/python*/site-packages/desmeds/**/*" in validate_yaml["files"]
    assert "lib/python*/site-packages/blah/**/*" in validate_yaml["files"]
