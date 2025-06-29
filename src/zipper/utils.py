import fnmatch
import os
import zipfile

from datetime import datetime
from getpass import getpass
from typing import Generator, List
from zipper import logger


def check_new_archive_exists(archive: str) -> bool:
    if os.path.exists(archive):
        return True
    return False


def get_absolute_path(path: str, base: str) -> str:
    if base and not os.path.isabs(path):
        return os.path.abspath(os.path.join(base, path))
    return os.path.abspath(path)


def get_base_path(path: str = "") -> str:
    if path:
        base = os.path.abspath(path)
        logger.debug("Base path: %s", base)
        return base
    return "."


def get_extraction_path(zip_path: str, output: str) -> str:
    if not output:
        extract_to = os.path.abspath(".".join(zip_path.split(".")[:-1]))
    else:
        extract_to = os.path.abspath(output)
    logger.info("Extracting %s to %s", zip_path, extract_to)
    return os.path.abspath(extract_to)


def get_output_name(item_name: str, timestamp: bool = False) -> str:
    item_name = item_name.replace(".zip", "")
    if timestamp:
        stamp = f"_{datetime.now().strftime("%Y%m%d%H%M%S")}"
    else:
        stamp = ""
    return os.path.abspath(f"{item_name}{stamp}.zip")


def get_password(prompt: bool = False) -> str:
    if prompt:
        return getpass("Enter password: ")
    return ""


def is_valid_zip(zip_path: str) -> bool:
    if not os.path.exists(zip_path):
        logger.error(f"Zip file not found: {zip_path}")
        return False
    if not zipfile.is_zipfile(zip_path):
        logger.warning(f"Not a valid zip file: {zip_path}")
        return False
    return True


def navigate(
    root_path: str, exclude_patterns: List[str]
) -> Generator[str, None, None]:
    if os.path.isfile(root_path):
        yield os.path.abspath(root_path)
    elif os.path.isdir(root_path):
        for root, dirs, files in os.walk(root_path):
            # Don't walk into excluded subdirectories
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    fnmatch.fnmatch(os.path.join(root, d), pattern)
                    for pattern in exclude_patterns
                )
            ]
            for name in files:
                full_path = os.path.join(root, name)
                if not any(
                    fnmatch.fnmatch(full_path, pattern)
                    for pattern in exclude_patterns
                ):
                    yield os.path.join(root, name)
