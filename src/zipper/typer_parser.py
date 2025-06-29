import sys
from typing import List, Literal, Union

from zipper import logger
from zipper.unzip import unzipper
from zipper.zip import zipper

import typer

app = typer.Typer()

# Wildcard escape mappings
ESCAPE_MAP = {
    "*": "[star]",
    "?": "[mark]",
}


def escape_wildcards(val: Union[str, List[str]]) -> Union[str, List[str]]:
    def _escape(s: str) -> str:
        for k, v in ESCAPE_MAP.items():
            s = s.replace(k, v)
        return s

    if isinstance(val, list):
        return [_escape(s) for s in val]
    return _escape(val)


def unescape_wildcards(val: Union[str, List[str]]) -> Union[str, List[str]]:
    def _unescape(s: str) -> str:
        for k, v in ESCAPE_MAP.items():
            s = s.replace(v, k)
        return s

    if isinstance(val, list):
        return [_unescape(s) for s in val]
    return _unescape(val)


def preprocess_args() -> None:
    logger.debug("Sys.argv: %s", sys.argv)
    arguments = []  # Capture the main command
    options = []  # Capture the options
    option_name = ""  # Empty = Arguments and Non-Empty = Options

    for arg in sys.argv:
        logger.debug("Now read: %s", arg)
        # Empty the option_name to add next arg to arguments
        if arg == "--":
            option_name = ""
            continue
        # Option name was read
        if arg.startswith("--"):
            option_name = arg
            options.append(arg)
        # Option value was read
        elif option_name:
            # Don't add option name if it was added during previous iteratio
            if options[-1] != option_name:
                options.append(option_name)
            options.append(arg)
        # Argument was read
        else:
            arguments.append(arg)
        logger.debug("Arguments: %s", arguments)
        logger.debug("Options: %s", options)

    sys.argv = arguments + escape_wildcards(options)
    logger.debug("Processed argv: %s", sys.argv)


@app.command("zip")
def zip_it(
    inputs: List[str],
    exclude: List[str] = typer.Option([], "--exclude", "-e", help="Excludes"),
    base: str = ".",
    password: bool = False,
    output: str = "",
    compression: str = typer.Option(
        "deflate",
        "--compression",
        help="Compression algorithm",
        case_sensitive=False,
        show_choices=True,
        rich_help_panel="Options",
        prompt=False,
        callback=None,
        metavar=None,
        # Instead of Literal:
        show_default=True,
    ),
):
    exclude = unescape_wildcards(exclude)
    logger.debug("Inputs: %s", inputs)
    logger.debug("Excludes: %s", exclude)
    if compression not in ["deflate", "store", "lzma", "bzip2"]:
        raise typer.BadParameter(
            f"Unsupported compression type: {compression}"
        )
    zipper(
        inputs,
        exclude_patterns=exclude,
        output=output,
        base=base,
        prompt=password,
        compression=compression,
    )


@app.command("unzip")
def unzip_it(inputs: List[str], base: str = ".", output: str = ""):
    unzipper(inputs, base=base, output=output)


if __name__ == "__main__":
    preprocess_args()
    app()
