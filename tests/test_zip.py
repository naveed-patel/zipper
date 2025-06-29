import os
import zipfile
import pyzipper
from pathlib import Path
from zipper.zip import zipper, zip_files  # adjust as per actual location


def test_zip_files_creates_zip(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_text("hello")
    file2.write_text("world")

    output_zip = tmp_path / "test.zip"

    zip_files(
        files=[str(file1), str(file2)],
        output_zip=str(output_zip),
        password=None,
        base=str(tmp_path),
        compression="deflate",
    )

    assert output_zip.exists()

    with zipfile.ZipFile(output_zip, "r") as zf:
        names = zf.namelist()
        assert "file1.txt" in names
        assert "file2.txt" in names


def test_zip_files_skips_existing(monkeypatch, tmp_path, caplog):
    zip_path = tmp_path / "existing.zip"
    zip_path.write_text("already exists")

    monkeypatch.setattr("zipper.zip.check_new_archive_exists", lambda path: True)

    zip_files(
        files=["fakefile.txt"],
        output_zip=str(zip_path),
        password=None,
        base=str(tmp_path),
    )

    assert "already exists" in zip_path.read_text()  # unchanged
    assert "already exists" in caplog.text


def test_zipper_creates_zip(monkeypatch, tmp_path):
    include_file = tmp_path / "keep.txt"
    exclude_file = tmp_path / "ignore.txt"
    include_file.write_text("keep me")
    exclude_file.write_text("ignore me")

    output = tmp_path / "out.zip"

    monkeypatch.setattr("zipper.zip.get_password", lambda prompt: None)
    monkeypatch.setattr("zipper.zip.get_base_path", lambda base: str(tmp_path))
    monkeypatch.setattr("zipper.zip.get_absolute_path", lambda p, b: os.path.join(b, p))
    monkeypatch.setattr(
        "zipper.zip.navigate", lambda p, ex: [p] if "ignore" not in p else []
    )
    monkeypatch.setattr("zipper.zip.check_new_archive_exists", lambda path: False)

    zipper(
        include_patterns=[str(include_file.name), str(exclude_file.name)],
        exclude_patterns=["*ignore.txt"],
        output=str(output),
        base=str(tmp_path),
        prompt=False,
        compression="deflate",
    )

    assert output.exists()
    with pyzipper.AESZipFile(output, "r") as zf:
        assert "keep.txt" in zf.namelist()
        assert "ignore.txt" not in zf.namelist()


def test_zip_files_with_password(tmp_path):
    file_path = tmp_path / "secret.txt"
    file_path.write_text("confidential")
    output_zip = tmp_path / "secret.zip"

    zip_files(
        files=[str(file_path)],
        output_zip=str(output_zip),
        password="s3cr3t",
        base=str(tmp_path),
    )

    assert output_zip.exists()

    with pyzipper.AESZipFile(output_zip, "r") as zf:
        zf.setpassword(b"s3cr3t")
        data = zf.read("secret.txt")
        assert data == b"confidential"


def test_zipper_creates_individual_archives_when_output_missing(monkeypatch, tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("alpha")
    file2.write_text("beta")

    created_zips = []

    monkeypatch.setattr("zipper.zip.get_password", lambda prompt: None)
    monkeypatch.setattr("zipper.zip.get_base_path", lambda base: str(tmp_path))
    monkeypatch.setattr("zipper.zip.get_absolute_path", lambda p, b: os.path.join(b, p))
    monkeypatch.setattr("zipper.zip.check_new_archive_exists", lambda path: False)
    monkeypatch.setattr("zipper.zip.navigate", lambda p, ex: [p])

    # Track output zips via monkeypatched get_output_name
    def mock_get_output_name(path, timestamp=False):
        output = tmp_path / (Path(path).stem + ".zip")
        created_zips.append(output)
        return str(output)

    monkeypatch.setattr("zipper.zip.get_output_name", mock_get_output_name)

    zipper(
        include_patterns=["a.txt", "b.txt"],
        exclude_patterns=[],
        output="",  # triggers per-file zip creation
        base=str(tmp_path),
        prompt=False,
        compression="store",
    )

    assert all(zip_path.exists() for zip_path in created_zips)
    assert len(created_zips) == 2


def test_zipper_logs_warning_when_no_files(monkeypatch, tmp_path, caplog):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    monkeypatch.setattr("zipper.zip.get_password", lambda prompt: None)
    monkeypatch.setattr("zipper.zip.get_base_path", lambda base: str(tmp_path))
    monkeypatch.setattr("zipper.zip.get_absolute_path", lambda p, b: os.path.join(b, p))
    monkeypatch.setattr("zipper.zip.check_new_archive_exists", lambda path: False)
    monkeypatch.setattr("zipper.zip.navigate", lambda p, ex: [])  # No files matched

    zipper(
        include_patterns=[str(empty_dir)],
        exclude_patterns=[],
        output="",
        base=str(tmp_path),
        prompt=False,
        compression="deflate",
    )

    assert "No files matched for" in caplog.text
