from typing import List, Literal, Union

from zipper import logger
from zipper.preprocessor import unescape_wildcards, typer_preprocessor
from zipper.unzip import unzipper
from zipper.zip import zipper

import typer

app = typer.Typer()

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
    typer_preprocessor()
    app()
