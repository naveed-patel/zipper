"""Utility file to allow running zipper without installing it as a module
"""
import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from zipper.main import run

if __name__ == "__main__":
    run()
