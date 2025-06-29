import argparse
from zipper.preprocessor import argpass_preprocessor
from zipper.unzip import unzipper
from zipper.zip import zipper


def main():
    argpass_preprocessor()
    parser = argparse.ArgumentParser(
        description="(Un)zip files/folders with optional AES encryption"
    )
    subparsers = parser.add_subparsers(dest="mode", required=False)

    # --- ZIP MODE ---
    zip_parser = subparsers.add_parser("zip", help="Zip files and folders")
    zip_parser.add_argument(
        "inputs", nargs="*", default=["*"], help="File(s) to zip"
    )
    zip_parser.add_argument(
        "--exclude", nargs="*", default=[], help="Exclude patterns"
    )
    zip_parser.add_argument("--output", "-o", help="File(s) to zip")
    zip_parser.add_argument(
        "--password", action="store_true", help="Prompt for password"
    )
    zip_parser.add_argument(
        "--base", default=".", help="Base input path for files to zip"
    )
    zip_parser.add_argument(
        "--compression",
        choices=["deflate", "store", "bzip2", "lzma"],
        default="deflate",
        help="Compression algorithm",
    )

    # --- UNZIP MODE ---
    unzip_parser = subparsers.add_parser("unzip", help="Unzip file(s)")
    unzip_parser.add_argument(
        "inputs", nargs="*", default=["*"], help="Zip file(s) to extract"
    )
    unzip_parser.add_argument("--output", "-o", help="Folder to extract to")
    unzip_parser.add_argument(
        "--base", default=".", help="Base input path for files to unzip"
    )

    args = parser.parse_args()

    if args.mode == "unzip":
        unzipper(args.inputs, output=args.output, base=args.base)
    else:
        zipper(
            args.inputs,
            exclude_patterns=args.exclude,
            output=args.output or "",
            base=args.base or ".",
            prompt=args.password or False,
            compression=args.compression or "deflate",
        )


if __name__ == "__main__":
    main()
