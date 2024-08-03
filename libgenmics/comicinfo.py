import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


_MAP = {"languageiso": "LanguageISO", "scaninformation": "ScanInformation"}


def make(output_file: str, **data):
    """See https://anansi-project.github.io/docs/comicinfo/documentation
    for **data keys.

    Lowercase keys will be modified with `str.title()`.

    Note that no schema validation is made in this function.
    """
    root = ET.Element("ComicInfo")

    for key, val in data.items():
        mapped = _MAP.get(key)
        if mapped is not None:
            key = mapped
        else:
            key = key.title()

        subelement = ET.SubElement(root, key)
        logger.info("Setting text to %s: %s", subelement, str(val))
        subelement.text = val

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8")
    logger.info("Written: %s", output_file)
