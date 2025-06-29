import pathlib
import runpy
import sys
import types
import zipper
from unittest.mock import patch, Mock

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
    main_path = pathlib.Path(zipper.__file__).parent.parent / "zipper.py"
    runpy.run_path(str(main_path), run_name="__main__")

    assert called.get("ran") is True