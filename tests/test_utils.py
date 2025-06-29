import os
import zipfile
from datetime import datetime
from zipper.utils import (
    check_new_archive_exists,
    get_absolute_path,
    get_base_path,
    get_extraction_path,
    get_output_name,
    get_password,
    is_valid_zip,
    navigate,
)


def test_check_new_archive_exists_file_exists(tmp_path):
    file = tmp_path / "dummy.zip"
    file.write_text("data")

    result = check_new_archive_exists(str(file))

    assert result is True


def test_check_new_archive_exists_file_missing(tmp_path):
    missing_file = tmp_path / "missing.zip"
    result = check_new_archive_exists(str(missing_file))
    assert result is False


def test_relative_path_with_base(tmp_path):
    base = tmp_path
    relative = "data/file.txt"
    expected = os.path.abspath(base / relative)

    result = get_absolute_path(relative, str(base))
    assert result == expected


def test_absolute_path_with_base(tmp_path):
    absolute_path = os.path.abspath(tmp_path / "file.txt")
    result = get_absolute_path(absolute_path, "/some/ignored/base")
    assert result == absolute_path  # base should be ignored


def test_relative_path_without_base(tmp_path, monkeypatch):
    # simulate cwd
    monkeypatch.chdir(tmp_path)
    relative = "file.txt"
    expected = os.path.abspath(relative)

    result = get_absolute_path(relative, "")
    assert result == expected


def test_absolute_path_without_base(tmp_path):
    abs_path = os.path.abspath(tmp_path / "abc.txt")
    result = get_absolute_path(abs_path, "")
    assert result == abs_path


def test_get_base_path_with_path(tmp_path):
    result = get_base_path(str(tmp_path))
    assert result == str(tmp_path)


def test_get_base_path_without_path(tmp_path):
    result = get_base_path()
    assert result == "."


def test_get_extraction_path_without_output(monkeypatch):
    zip_path = "archive.test.zip"
    expected = os.path.abspath("archive.test")
    result = get_extraction_path(zip_path, "")
    assert result == expected


def test_get_extraction_path_with_output(tmp_path):
    zip_path = "any.zip"
    output_path = tmp_path / "out_dir"
    expected = os.path.abspath(output_path)
    result = get_extraction_path(zip_path, str(output_path))
    assert result == expected


def test_get_output_name_without_timestamp():
    result = get_output_name("example.zip", timestamp=False)
    expected = os.path.abspath("example.zip")
    assert result == expected


def test_get_output_name_without_extension():
    result = get_output_name("example", timestamp=False)
    expected = os.path.abspath("example.zip")
    assert result == expected


def test_get_output_name_with_timestamp(monkeypatch):
    fixed_time = datetime(2023, 1, 1, 12, 30, 45)

    # Patch only datetime.now within the zipper.utils module
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_time

    monkeypatch.setattr("zipper.utils.datetime", FixedDateTime)

    result = get_output_name("example.zip", timestamp=True)
    expected = os.path.abspath("example_20230101123045.zip")
    assert result == expected


def test_get_password_without_prompt():
    assert get_password(prompt=False) == ""


def test_get_password_with_prompt(monkeypatch):
    # Simulate user typing "secret123" at the prompt
    monkeypatch.setattr("zipper.utils.getpass", lambda prompt: "secret123")
    result = get_password(prompt=True)
    assert result == "secret123"


def test_zip_file_does_not_exist(tmp_path, caplog):
    missing_file = tmp_path / "nonexistent.zip"
    with caplog.at_level("ERROR"):
        result = is_valid_zip(str(missing_file))
    assert result is False
    assert f"Zip file not found: {missing_file}" in caplog.text


def test_not_a_zip_file(tmp_path, caplog):
    fake_zip = tmp_path / "fake.zip"
    fake_zip.write_text("not a real zip")

    with caplog.at_level("WARNING"):
        result = is_valid_zip(str(fake_zip))
    assert result is False
    assert f"Not a valid zip file: {fake_zip}" in caplog.text


def test_valid_zip_file(tmp_path):
    valid_zip = tmp_path / "valid.zip"
    with zipfile.ZipFile(valid_zip, "w") as zf:
        zf.writestr("file.txt", "hello world")

    result = is_valid_zip(str(valid_zip))
    assert result is True


def test_navigate_single_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")

    result = list(navigate(str(file_path), exclude_patterns=[]))
    assert result == [str(file_path.resolve())]


def test_navigate_directory_without_exclusions(tmp_path):
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "file1.txt").write_text("data1")
    (tmp_path / "dir" / "file2.txt").write_text("data2")

    result = list(navigate(str(tmp_path / "dir"), exclude_patterns=[]))
    expected = {
        str(tmp_path / "dir" / "file1.txt"),
        str(tmp_path / "dir" / "file2.txt"),
    }
    assert set(result) == expected


def test_navigate_exclude_file(tmp_path):
    (tmp_path / "a").mkdir()
    f1 = tmp_path / "a" / "include.txt"
    f2 = tmp_path / "a" / "exclude.txt"
    f1.write_text("keep")
    f2.write_text("skip")

    result = list(navigate(str(tmp_path), exclude_patterns=["**/exclude.txt"]))
    assert str(f2) not in result
    assert str(f1) in result


def test_navigate_exclude_directory(tmp_path):
    keep_dir = tmp_path / "keep"
    skip_dir = tmp_path / "skip"
    keep_dir.mkdir()
    skip_dir.mkdir()
    (keep_dir / "a.txt").write_text("data")
    (skip_dir / "b.txt").write_text("data")

    result = list(navigate(str(tmp_path), exclude_patterns=[str(skip_dir)]))
    assert any("keep" in p for p in result)
    assert all("skip" not in p for p in result)
