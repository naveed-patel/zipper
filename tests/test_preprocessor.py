import sys
import shlex
from zipper.preprocessor import (
    ESCAPE_MAP, escape_wildcards, unescape_wildcards, typer_preprocessor, argparse_preprocessor)

STAR = ESCAPE_MAP['*']

def test_escape_wildcards_str():
    ip = "input*.txt"
    result = escape_wildcards(ip)
    assert result == f"input{STAR}.txt"

def test_escape_wildcards_lst():
    ip = ["*.txt", "imp.*", "file*.zip"]
    result = escape_wildcards(ip)
    assert result == [f"{STAR}.txt", f"imp.{STAR}", f"file{STAR}.zip"]

def test_unescape_wildcards_str():
    ip = f"input{STAR}.txt"
    result = unescape_wildcards(ip)
    assert result == "input*.txt"

def test_unescape_wildcards_lst():
    ip = [f"{STAR}.txt", f"imp.{STAR}", f"file{STAR}.zip"]
    result =unescape_wildcards(ip)
    assert result == ["*.txt", "imp.*", "file*.zip"]

def test_typer_preprocessor():
    cmd = "zipper zip file1*.txt newfolder* --exclude **/__pycache__ **/.git --exclude .gitignore -- readme.md"
    sys.argv = shlex.split(cmd)
    typer_preprocessor()
    op = f"zipper zip file1*.txt newfolder* readme.md --exclude {STAR}{STAR}/__pycache__ --exclude {STAR}{STAR}/.git --exclude .gitignore"
    assert sys.argv == shlex.split(op)

def test_argparse_preprocessor():
    cmd = "zipper zip file1*.txt newfolder* --exclude **/__pycache__ **/.git --exclude .gitignore -- readme.md"
    sys.argv = shlex.split(cmd)
    argparse_preprocessor()
    op = f"zipper zip file1*.txt newfolder* readme.md --exclude **/__pycache__ **/.git .gitignore"
    assert sys.argv == shlex.split(op)