from setuptools import setup, find_packages

setup(
    name="conda-forge-artifact-validation",
    description="",
    author="conda-forge/core",
    author_email="",
    scripts=[
        "bin/conda-forge-validate-artifact",
        "bin/conda-forge-generate-validate-yamls",
        "bin/conda-forge-scan-artifacts",
        "bin/conda-forge-bump-on-fail",
        "bin/conda-forge-report-scan-results",
    ],
    url="https://github.com/conda-forge/artifact-validation",
    packages=find_packages(),
    use_scm_version=True,
    setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
)
