import glob
from typing import List

import pyzipper

from zipper import logger
from zipper.utils import (
    get_absolute_path,
    get_base_path,
    get_extraction_path,
    get_password,
    is_valid_zip,
)


def unzipper(
    include_patterns: List[str], *, output: str = "", base: str = "."
) -> None:
    base = get_base_path(base)
    for file_input in include_patterns:
        for zipped_file in glob.glob(file_input, recursive=False):
            zip_path = get_absolute_path(zipped_file, base)
            if not is_valid_zip(zip_path):
                continue
            extract_to = get_extraction_path(zip_path, output)
            unzip_file(zip_path, extract_to)
        else:
            logger.error(f"Zip file not found: {file_input}")


def unzip_file(zip_path: str, extract_to: str) -> None:
    with pyzipper.AESZipFile(zip_path, "r") as zf:
        try:
            # Try without password
            zf.extractall(path=extract_to)
            logger.info(f"Extracted to: {extract_to}")
            return
        except RuntimeError as e:
            if "encrypted" not in str(e).lower():
                raise

        # Prompt for password as protected zip
        for _ in range(3):
            password = get_password(True)
            try:
                zf.setpassword(password.encode())
                zf.extractall(path=extract_to)
                logger.info(f"Extracted to: {extract_to}")
                continue
            except RuntimeError:
                logger.warning("Incorrect password. Try again.")
        logger.error(f"Failed to extract {zip_path} after 3 attempts")
