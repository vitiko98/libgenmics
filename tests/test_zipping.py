import os
import zipfile

import pytest

from libgenmics import zipping


@pytest.mark.parametrize("path", ["tests/data/dummy.cbz"])
def test_extract(tmp_path, path):
    zipping.extract(path, tmp_path)
    assert os.listdir(tmp_path)


def test_extract_inexistent_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        zipping.extract(tmp_path / "dummy.cbz", tmp_path)


def test_extract_no_rar_zip_file(tmp_path):
    with pytest.raises(zipfile.BadZipFile):
        zipping.extract(__file__, tmp_path)


@pytest.mark.parametrize("path", ["tests/data/dummy.cbz"])
def test_extract_and_write(tmp_path, path):
    zipping.extract(path, tmp_path)

    new = tmp_path / "dummy.cbz"
    zipping.make_cbz(tmp_path, new)

    new_dir = tmp_path / "new_dir"

    os.makedirs(new_dir, exist_ok=True)

    zipping.extract(new, new_dir)

    assert os.listdir(new_dir)
