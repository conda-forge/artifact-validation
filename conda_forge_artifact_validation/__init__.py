try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("conda_forge_artifact_validation")
except PackageNotFoundError:
    # package is not installed
    pass
