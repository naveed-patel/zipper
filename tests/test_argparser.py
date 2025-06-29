import pathlib
import runpy
import sys
import shlex
from unittest.mock import Mock
from types import SimpleNamespace, ModuleType
import pytest
import zipper


@pytest.fixture(autouse=True)
def reset_argv():
    original = sys.argv[:]
    yield
    sys.argv = original


@pytest.fixture
def main():
    from zipper.argparser import main

    return main


@pytest.fixture
def mock_run(monkeypatch):
    mock_zipper = Mock()
    mock_unzipper = Mock()

    # Create fake module zipper.zip - for __main__ tests
    zip_module = ModuleType("zipper.zip")
    zip_module.zipper = mock_zipper
    sys.modules["zipper.zip"] = zip_module

    # Create fake module zipper.unzip - for __main__ tests
    unzip_module = ModuleType("zipper.unzip")
    unzip_module.unzipper = mock_unzipper
    sys.modules["zipper.unzip"] = unzip_module

    # Patch where they're used — not where they're defined!
    monkeypatch.setattr("zipper.argparser.zipper", mock_zipper)
    monkeypatch.setattr("zipper.argparser.unzipper", mock_unzipper)

    # Only import run after monkeypatching
    # from zipper.argparser import main

    return SimpleNamespace(
        # main=main,
        zipper=mock_zipper,
        unzipper=mock_unzipper,
    )


def test_check_zip_single_input(main, mock_run):
    command = "zipper.py zip file1.txt"
    sys.argv = shlex.split(command)
    main()
    mock_run.zipper.assert_called_once_with(
        ["file1.txt"],
        exclude_patterns=[],
        output="",
        base=".",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_check_unzip_single_input(main, mock_run):
    sys.argv = ["zipper.py", "unzip", "file1.zip"]
    main()
    mock_run.unzipper.assert_called_once()
    mock_run.zipper.assert_not_called()


def test_check_zip_multiple_input(main, mock_run):
    command = "zipper.py zip 'file1.txt' file2.txt"
    sys.argv = shlex.split(command)
    main()
    mock_run.zipper.assert_called_once_with(
        ["file1.txt", "file2.txt"],
        exclude_patterns=[],
        output="",
        base=".",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_check_zip_with_excludes(main, mock_run):
    command = "zipper.py zip 'file 1.txt' file2.txt --exclude *2.txt"
    sys.argv = shlex.split(command)
    main()
    mock_run.zipper.assert_called_once_with(
        ["file 1.txt", "file2.txt"],
        exclude_patterns=["*2.txt"],
        output="",
        base=".",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_check_zip_with_multi_excludes(main, mock_run):
    command = "zipper.py zip 'file 1.txt' file2.txt --exclude *2.txt **/.git"
    sys.argv = shlex.split(command)
    main()
    mock_run.zipper.assert_called_once_with(
        ["file 1.txt", "file2.txt"],
        exclude_patterns=["*2.txt", "**/.git"],
        output="",
        base=".",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_check_zip_with_excludes_and_base(main, mock_run):
    command = "zipper.py zip file1.txt file2.txt --exclude **/__pycache__ --base /tmp"
    sys.argv = shlex.split(command)
    main()
    mock_run.zipper.assert_called_once_with(
        ["file1.txt", "file2.txt"],
        exclude_patterns=["**/__pycache__"],
        output="",
        base="/tmp",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_check_zip_with_compression_and_output(main, mock_run):
    command = (
        "zipper.py zip file1.txt file2.txt --compression lzma --output /tmp/temp.zip"
    )
    sys.argv = shlex.split(command)
    main()
    mock_run.zipper.assert_called_once_with(
        ["file1.txt", "file2.txt"],
        exclude_patterns=[],
        output="/tmp/temp.zip",
        base=".",
        prompt=False,
        compression="lzma",
    )
    mock_run.unzipper.assert_not_called()


def test_check_unzip_with_output(main, mock_run):
    command = "zipper.py unzip file1.zip file2.zip --output /tmp/temp"
    sys.argv = shlex.split(command)
    main()
    mock_run.unzipper.assert_called_once_with(
        ["file1.zip", "file2.zip"], output="/tmp/temp", base="."
    )
    mock_run.zipper.assert_not_called()


def test_main_guard(mock_run):
    command = "argparser.py unzip file1.zip file2.zip --output temp --base /tmp"
    sys.argv = shlex.split(command)
    main_path = pathlib.Path(zipper.__file__).parent / "argparser.py"
    runpy.run_path(str(main_path), run_name="__main__")
    mock_run.unzipper.assert_called_once_with(
        ["file1.zip", "file2.zip"], output="temp", base="/tmp"
    )
    mock_run.zipper.assert_not_called()


# TODO: Add support for argparse to take options alike typer
# def test_check_zip_with_multi_excludes_split(main, mock_run):
#     command = "zipper.py zip 'file 1.txt' file2.txt --exclude *2.txt --exclude **/.git"
#     sys.argv = shlex.split(command)
#     main()
#     mock_run.zipper.assert_called_once_with(
#         ["file 1.txt", "file2.txt"],
#         exclude_patterns=["*2.txt", "**/.git"],
#         output="",
#         base=".",
#         prompt=False,
#         compression="deflate",
#     )
#     mock_run.unzipper.assert_not_called()


# TODO: Add support for split out inputs
# def test_check_zip_with_distributed_input(main, mock_run):
#     command = (
#         "zipper.py zip 'file 1.txt' file2.txt --exclude *2.txt **/.git -- file3.txt"
#     )
#     sys.argv = shlex.split(command)
#     main()
#     mock_run.zipper.assert_called_once_with(
#         ["file 1.txt", "file2.txt", "file3.txt"],
#         exclude_patterns=["*2.txt", "**/.git"],
#         output="",
#         base=".",
#         prompt=False,
#         compression="deflate",
#     )
#     mock_run.unzipper.assert_not_called()
