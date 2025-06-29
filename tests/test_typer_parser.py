import pathlib
import runpy
import sys
import shlex
from unittest.mock import Mock
from types import SimpleNamespace, ModuleType
import pytest
import zipper
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture(autouse=True)
def reset_argv():
    original = sys.argv[:]
    yield
    sys.argv = original


@pytest.fixture
def app():
    from zipper.typer_parser import app

    return app


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
    monkeypatch.setattr("zipper.typer_parser.zipper", mock_zipper)
    monkeypatch.setattr("zipper.typer_parser.unzipper", mock_unzipper)

    # Only import run after monkeypatching
    # from zipper.typer_parser import app

    return SimpleNamespace(
        # app=app,
        zipper=mock_zipper,
        unzipper=mock_unzipper,
    )


def test_check_zip_single_input(app, mock_run):
    command = "zip file1.txt"
    runner.invoke(app, shlex.split(command))
    mock_run.zipper.assert_called_once_with(
        ["file1.txt"],
        exclude_patterns=[],
        output="",
        base=".",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_check_zip_with_multi_excludes_split(app, mock_run):
    command = "zip 'file 1.txt' file2.txt --exclude *2.txt --exclude **/.git"
    runner.invoke(app, shlex.split(command))
    mock_run.zipper.assert_called_once_with(
        ["file 1.txt", "file2.txt"],
        exclude_patterns=["*2.txt", "**/.git"],
        output="",
        base=".",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_check_zip_with_distributed_input(app, mock_run):
    command = "zip file1.txt file2.txt --exclude *2.txt --exclude **/.git -- file3.txt"
    runner.invoke(app, shlex.split(command))
    mock_run.zipper.assert_called_once_with(
        ["file1.txt", "file2.txt", "file3.txt"],
        exclude_patterns=["*2.txt", "**/.git"],
        output="",
        base=".",
        prompt=False,
        compression="deflate",
    )
    mock_run.unzipper.assert_not_called()


def test_invalid_compression_raises_error(app):
    result = runner.invoke(app, shlex.split("zip file1.txt --compression invalidalgo"))
    assert result.exit_code != 0
    assert "Unsupported compression type: invalidalgo" in result.output


def test_main_guard_zip(mock_run):
    sys.argv = shlex.split(
        "typer_parser.py unzip file1.zip file2.zip --output temp --base /tmp"
    )
    main_path = pathlib.Path(zipper.__file__).parent / "typer_parser.py"

    # Catch SystemExit(0) from Typer
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(main_path), run_name="__main__")

    assert excinfo.value.code == 0
    mock_run.unzipper.assert_called_once_with(
        ["file1.zip", "file2.zip"], output="temp", base="/tmp"
    )
    mock_run.zipper.assert_not_called()


def test_main_guard_unzip(mock_run):
    sys.argv = shlex.split(
        "typer_parser.py zip file* new_folder --exclude file2*.zip **/.git --base /tmp --compression=lzma -- extra_folder"
    )
    main_path = pathlib.Path(zipper.__file__).parent / "typer_parser.py"

    # Catch SystemExit(0) from Typer
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(main_path), run_name="__main__")

    assert excinfo.value.code == 0
    mock_run.zipper.assert_called_once_with(
        ["file*", "new_folder", "extra_folder"],
        exclude_patterns=["file2*.zip", "**/.git"],
        output="",
        base="/tmp",
        prompt=False,
        compression="lzma",
    )
    mock_run.unzipper.assert_not_called()
