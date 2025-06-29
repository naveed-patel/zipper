import pytest
import pyzipper
from pathlib import Path
from zipper.unzip import unzipper


def create_test_zip(zip_path: Path, contents: dict, password: str = None):
    """Create a test zip file with or without encryption"""
    with pyzipper.AESZipFile(zip_path, "w", compression=pyzipper.ZIP_DEFLATED) as zf:
        if password:
            zf.setpassword(password.encode())
            zf.setencryption(pyzipper.WZ_AES)
        for name, data in contents.items():
            zf.writestr(name, data)


def test_unzipper_extracts_zip(tmp_path):
    zip_file = tmp_path / "test.zip"
    contents = {"file1.txt": "hello", "file2.txt": "world"}
    create_test_zip(zip_file, contents)
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    unzipper([str(zip_file)], output=str(output_dir))

    extracted = list(output_dir.glob("**/*"))
    extracted_files = [f.name for f in extracted if f.is_file()]
    assert "file1.txt" in extracted_files
    assert "file2.txt" in extracted_files


def test_unzipper_encrypted_success(monkeypatch, tmp_path):
    zip_file = tmp_path / "protected.zip"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    contents = {"secret.txt": "top secret"}
    password = "test123"

    create_test_zip(zip_file, contents, password=password)

    attempts = iter([password])  # simulate entering correct password on 1st try

    monkeypatch.setattr("zipper.unzip.get_password", lambda prompt: password)

    unzipper([str(zip_file)], output=str(output_dir))

    extracted = list(output_dir.glob("**/*"))
    extracted_files = [f.name for f in extracted if f.is_file()]
    assert "secret.txt" in extracted_files


def test_unzipper_encrypted_fail(monkeypatch, tmp_path, caplog):
    zip_file = tmp_path / "protected_fail.zip"
    output_dir = tmp_path / "fail_out"
    output_dir.mkdir()
    contents = {"fail.txt": "bad password test"}
    correct_password = "secret"

    create_test_zip(zip_file, contents, password=correct_password)

    attempts = iter(["wrong1", "wrong2", "wrong3"])

    monkeypatch.setattr("zipper.unzip.get_password", lambda prompt: next(attempts))

    unzipper([str(zip_file)], output=str(output_dir))

    assert "Failed to extract" in caplog.text
    assert not any((output_dir / "fail.txt").exists() for _ in range(1))


def test_unzipper_skips_invalid_zip(tmp_path, caplog):
    invalid_zip = tmp_path / "not_a_zip.zip"
    invalid_zip.write_text("this is not a zip file")
    unzipper([str(invalid_zip)], output=str(tmp_path))

    assert f"Not a valid zip file: {invalid_zip}" in caplog.text


def test_unzipper_missing_zip(tmp_path, caplog):
    missing_zip = tmp_path / "missing.zip"
    unzipper([str(missing_zip)], output=str(tmp_path))
    assert f"Zip file not found: {missing_zip}" in caplog.text


def test_unzipper_other_runtime_error(monkeypatch, tmp_path):
    zip_path = tmp_path / "corrupted.zip"
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    # Create a dummy valid zip so pyzipper opens it, but force extractall to break
    create_test_zip(zip_path, {"file.txt": "data"})

    # monkeypatch extractall to raise non-password-related RuntimeError
    def bad_extractall(self, path=None):
        raise RuntimeError("disk full or some other error")

    monkeypatch.setattr("pyzipper.AESZipFile.extractall", bad_extractall)

    with pytest.raises(RuntimeError, match="disk full"):
        unzipper([str(zip_path)], output=str(output_dir))
