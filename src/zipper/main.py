"""Utility to un(zip) files and folders
Prefers to use typer to provide cli functionality and fallbacks to argparse
"""

import os
import sys

sys.path.insert(0, os.path.abspath("src"))
# Import after sys.path.insert to allow running this as a script
from zipper import CONFIG


def run():
    if CONFIG.get("preferred_parser", "typer") == "typer":
        try:
            from zipper.typer_parser import app, preprocess_args

            preprocess_args()
            return app()
        except ModuleNotFoundError:
            from zipper.argparser import main

            return main()
    else:
        from zipper.argparser import main

        return main()


if __name__ == "__main__":
    run()
