from ..generate_validate_yamls import (
    generate_validate_yaml_for_python,
    generate_validate_yaml_from_libcfgraph,
)


def test_generate_validate_yaml_from_libcfgraph():
    validate_yaml = generate_validate_yaml_from_libcfgraph("numpy")

    assert validate_yaml["allowed"] == ["numpy"]
    for fname in [
        "bin/f2py",
        "bin/f2py2",
        "bin/f2py3",
        "bin/f2py3.8",
        "Scripts/f2py.exe",
        "lib/python2.7/site-packages/numpy/__init__.py",
        "Lib/site-packages/numpy/__init__.py",
    ]:
        assert fname in validate_yaml["files"]


def test_generate_validate_yaml_from_libcfgraph_exclude():
    validate_yaml = generate_validate_yaml_from_libcfgraph(
        "numpy", exclude_globs=["lib/python*/site-packages/numpy/**/*"]
    )

    assert validate_yaml["allowed"] == ["numpy"]
    for fname in [
        "bin/f2py",
        "bin/f2py2",
        "bin/f2py3",
        "bin/f2py3.8",
        "Scripts/f2py.exe",
        "Lib/site-packages/numpy/__init__.py",
    ]:
        assert fname in validate_yaml["files"]

    assert "lib/python2.7/site-packages/numpy/__init__.py" not in validate_yaml["files"]
    assert "lib/python*/site-packages/numpy/**/*" not in validate_yaml["files"]


def test_generate_validate_yaml_for_python():
    validate_yaml = generate_validate_yaml_for_python(
        "numpy",
        ["numpy", "blah"],
        allowed=["blah"],
    )

    assert validate_yaml["allowed"] == ["blah", "numpy"]
    for fname in [
        "bin/f2py",
        "bin/f2py2",
        "bin/f2py3",
        "bin/f2py3.8",
        "Scripts/f2py.exe",
    ]:
        assert fname in validate_yaml["files"]

    assert "lib/python2.7/site-packages/numpy/__init__.py" not in validate_yaml["files"]
    assert "lib/python*/site-packages/numpy/**/*" in validate_yaml["files"]
    assert "lib/python*/site-packages/blah/**/*" in validate_yaml["files"]
