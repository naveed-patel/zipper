import pathlib
import runpy
import sys
import types
import zipper
from zipper.main import run


def test_typer_preferred_parser(monkeypatch):
    zipper.CONFIG["preferred_parser"] = "typer"  # mutate in-place!

    # Fake typer_parser module
    mock_typer_parser = types.SimpleNamespace(
        preprocess_args=lambda: None, app=lambda: "TYPER"
    )
    monkeypatch.setitem(sys.modules, "zipper.typer_parser", mock_typer_parser)
    result = run()
    assert result == "TYPER"


def test_fallback_to_argparse_on_module_not_found(monkeypatch):
    # Patch __import__ to simulate ModuleNotFoundError when importing zipper.typer_parser
    original_import = __import__

    def import_mock(name, *args, **kwargs):
        if name == "zipper.typer_parser":
            raise ModuleNotFoundError("Simulated missing module")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", import_mock)

    monkeypatch.setitem(
        sys.modules,
        "zipper.argparser",
        types.SimpleNamespace(main=lambda: "ARGPARSE_FALLBACK"),
    )
    result = zipper.main.run()

    assert result == "ARGPARSE_FALLBACK"


def test_argparse_selected(monkeypatch):
    monkeypatch.setitem(
        sys.modules, "zipper.argparser", types.SimpleNamespace(main=lambda: "ARGPARSE")
    )
    zipper.CONFIG["preferred_parser"] = "argparse"  # mutate in-place!
    result = zipper.main.run()
    assert result == "ARGPARSE"


def test_main_guard(monkeypatch):
    called = {}  # Track if `run()` gets called

    # Patch zipper.run() to capture call
    monkeypatch.setitem(
        sys.modules,
        "zipper.argparser",
        types.SimpleNamespace(main=lambda: called.setdefault("ran", True)),
    )

    monkeypatch.setitem(
        sys.modules,
        "zipper.typer_parser",
        types.SimpleNamespace(
            preprocess_args=lambda: None, app=lambda: called.setdefault("ran", True)
        ),
    )

    # Actually execute main.py in "__main__" context
    main_path = pathlib.Path(zipper.__file__).parent / "main.py"
    runpy.run_path(str(main_path), run_name="__main__")

    assert called.get("ran") is True
