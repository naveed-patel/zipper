import fnmatch
import glob
import os

from typing import List
from zipper import logger
from zipper.utils import (
    check_new_archive_exists,
    get_absolute_path,
    get_base_path,
    get_output_name,
    get_password,
    navigate,
)
import pyzipper


def zipper(
    include_patterns: List[str],
    *,
    exclude_patterns: List[str],
    output: str,
    base: str,
    prompt: bool,
    compression: str,
) -> None:
    logger.debug("Include Patterns: %s", include_patterns)
    logger.debug("Exclude patterns: %s", exclude_patterns)
    base = get_base_path(base)
    password = get_password(prompt)
    collected_files = set()
    for pattern in include_patterns:
        pattern_path = get_absolute_path(pattern, base)
        logger.debug("Checking pattern: %s", pattern_path)
        for match in glob.glob(pattern_path, recursive=True):
            full_path = os.path.abspath(match)
            if any(
                fnmatch.fnmatch(full_path, pattern)
                for pattern in exclude_patterns
            ):
                logger.debug("Skipping %s", full_path)
                continue
            for item in navigate(full_path, exclude_patterns):
                collected_files.add(os.path.abspath(item))
            if (not output) and (not collected_files):
                logger.warning(f"No files matched for {pattern_path}")
            elif not output:
                output_zip = get_output_name(match, False)
                zip_files(list(collected_files), output_zip, password, base)
                collected_files = set()
    if output:
        output_zip = get_output_name(output, False)
        zip_files(
            list(collected_files), output_zip, password, base, compression
        )


def zip_files(
    files: List[str],
    output_zip: str,
    password: str | None = None,
    base: str = os.getcwd(),
    compression: str = "deflate",
):
    if check_new_archive_exists(output_zip):
        logger.warning(f"Archive {output_zip} already exists. Skipping...")
        return
    compression_map = {
        "deflate": pyzipper.ZIP_DEFLATED,
        "store": pyzipper.ZIP_STORED,
        "bzip2": pyzipper.ZIP_BZIP2,
        "lzma": pyzipper.ZIP_LZMA,
    }
    compression_method = compression_map.get(
        compression, pyzipper.ZIP_DEFLATED
    )
    with pyzipper.AESZipFile(
        output_zip, "w", compression=compression_method
    ) as zf:
        if password:
            message = "AES encrypted zip"
            zf.setpassword(password.encode())
            zf.setencryption(pyzipper.WZ_AES, nbits=256)
        else:
            message = "zip"
        for file in files:
            arcname = os.path.relpath(file, start=base)
            logger.info(f"[+] Adding: {arcname} ({file})")
            zf.write(file, arcname)
    logger.info("Created %s: %s", message, output_zip)
