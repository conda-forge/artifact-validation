import subprocess
import pytest


@pytest.mark.parametrize('md5sum,ok', [
    ("c792b85aebf54d48fb3d7597d6688ed6", True),
    ("d143", False),
])
def test_validate_url(md5sum, ok):
    r = subprocess.run(
        f"""\
conda-forge-validate-artifact -v \
  https://anaconda.org/conda-forge/numpy/1.19.4/download/osx-64/numpy-1.19.4-py36hcf5569d_1.tar.bz2 \
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
    ("c792b85aebf54d48fb3d7597d6688ed6", True),
    ("d143", False),
])
def test_validate_file(md5sum, ok):
    r = subprocess.run(
        f"""\
conda-forge-validate-artifact -v \
  numpy-1.19.4-py36hcf5569d_1.tar.bz2 \
  --md5sum=\"{md5sum}\"
""",  # noqa
        shell=True,
    )
    if ok:
        assert r.returncode == 0
    else:
        assert r.returncode != 0
