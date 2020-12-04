import subprocess
import pytest


@pytest.mark.parametrize('md5sum,ok', [
    ("96c4c98482a8783e209e064c715fd4e8", True),
    ("d143", False),
])
def test_validate_url_md5sum(md5sum, ok):
    r = subprocess.run(
        f"""\
conda-forge-validate-artifact -v \
  https://conda.anaconda.org/conda-forge/linux-64/cf-autotick-bot-test-package-0.10-py36h9f0ad1d_2.tar.bz2 \
  --md5sum=\"{md5sum}\" \
  --feedstock=cf-autotick-bot-test-package-feedstock
""",  # noqa
        shell=True,
    )
    if ok:
        assert r.returncode == 0
    else:
        assert r.returncode != 0


@pytest.mark.parametrize('url,md5sum,ok', [
    (
        (
            "https://conda.anaconda.org/conda-forge/linux-64/"
            "cf-autotick-bot-test-package-0.10-py36h9f0ad1d_2.tar.bz2"
        ),
        "96c4c98482a8783e209e064c715fd4e8",
        True,
    ),
    (
        (
            "https://conda.anaconda.org/conda-forge/"
            "numpy-1.19.4-py36hcf5569d_1.tar.bz2"
        ),
        "c792b85aebf54d48fb3d7597d6688ed6",
        False,
    ),
])
def test_validate_url_output(url, md5sum, ok):
    r = subprocess.run(
        f"""\
conda-forge-validate-artifact -v \
  {url} \
  --md5sum=\"{md5sum}\" \
  --feedstock=cf-autotick-bot-test-package-feedstock
""",  # noqa
        shell=True,
    )
    if ok:
        assert r.returncode == 0
    else:
        assert r.returncode != 0


@pytest.mark.parametrize('md5sum,ok', [
    ("96c4c98482a8783e209e064c715fd4e8", True),
    ("d143", False),
])
def test_validate_file_md5sum(md5sum, ok):
    r = subprocess.run(
        f"""\
conda-forge-validate-artifact -v \
  cf-autotick-bot-test-package-0.10-py36h9f0ad1d_2.tar.bz2 \
  --md5sum=\"{md5sum}\"
""",  # noqa
        shell=True,
    )
    if ok:
        assert r.returncode == 0
    else:
        assert r.returncode != 0


@pytest.mark.parametrize('pth,md5sum,ok', [
    (
        "cf-autotick-bot-test-package-0.10-py36h9f0ad1d_2.tar.bz2",
        "96c4c98482a8783e209e064c715fd4e8",
        True,
    ),
    (
        "numpy-1.19.4-py36hcf5569d_1.tar.bz2",
        "c792b85aebf54d48fb3d7597d6688ed6",
        False,
    ),
])
def test_validate_file_output(pth, md5sum, ok):
    r = subprocess.run(
        f"""\
conda-forge-validate-artifact -v \
  {pth} \
  --md5sum=\"{md5sum}\" \
  --feedstock=cf-autotick-bot-test-package-feedstock
""",  # noqa
        shell=True,
    )
    if ok:
        assert r.returncode == 0
    else:
        assert r.returncode != 0


@pytest.marl.parametrize('url_path', [
    "https://anaconda.org/conda-forge/linux-64/freud-0.11.0-py27h3e44d54_0.tar.bz2",
    "freud-0.11.0-py27h3e44d54_0.tar.bz2"
])
def test_validate_bad_paths(url_path):
    r = subprocess.run(
        f"conda-forge-validate-artifact -v {url_path}",
        shell=True,
    )
    assert r.returncode != 0
