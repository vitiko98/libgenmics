import logging
import os
import zipfile

import rarfile

logger = logging.getLogger(__name__)


def extract(path, output):
    "raises FileNotFoundError, zipfile.BadZipFile"
    handler = rarfile.RarFile if rarfile.is_rarfile(path) else zipfile.ZipFile
    handler(path).extractall(output)


def make_cbz(source_dir, output_path):
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file)

    logger.info("OK: %s", output_path)
