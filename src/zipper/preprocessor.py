import sys
from zipper import logger
from typing import List, Union

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


def typer_preprocessor() -> None:
    logger.debug("Sys.argv: %s", sys.argv)
    arguments = []  # Capture the main command
    options = []  # Capture the options
    option_name = ""  # Empty = Arguments and Non-Empty = Options

    for arg in sys.argv:
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
            # Don't add option name if it was added during previous iteration
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

def argparse_preprocessor() -> None:
    logger.debug("Sys.argv: %s", sys.argv)
    arguments = []  # Capture the main command
    options = {}  # Capture the options
    option_name = ""  # Empty = Arguments and Non-Empty = Options

    for arg in sys.argv:
        # Empty the option_name to add next arg to arguments
        if arg == "--":
            option_name = ""
            continue
        # Option name was read
        if arg.startswith("--"):
            option_name = arg
            if option_name not in options:
                options[option_name] = []
            # options.setdefault(arg, [])
        # Option value was read
        elif option_name:
            options[option_name].append(arg)
        # Argument was read
        else:
            arguments.append(arg)
        logger.debug("Arguments: %s", arguments)
        logger.debug("Options: %s", options)

    flattened_options = [item for k, v in options.items() for item in [k] + v]
    sys.argv = arguments + flattened_options
    logger.debug("Processed argv: %s", sys.argv)