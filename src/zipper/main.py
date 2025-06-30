"""Utility to un(zip) files and folders
Prefers to use typer to provide cli functionality and fallbacks to argparse
"""
from zipper import CONFIG
import os
import sys

sys.path.insert(0, os.path.abspath("src"))

def run():
    if CONFIG.get("preferred_parser", "typer") == "typer":
        try:
            from zipper.preprocessor import typer_preprocessor
            from zipper.typer_parser import app

            typer_preprocessor()
            return app()
        except ModuleNotFoundError:
            from zipper.argparser import main
            return main()
    else:
        from zipper.argparser import main
        return main()


if __name__ == "__main__":
    run()
