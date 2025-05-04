from argparse import ArgumentParser
from pathlib import Path
from .storage import Storage

STORAGE_NAME = Path.home() / "notes/projects"

import subprocess

def add(args):
    s = Storage.pwd(STORAGE_NAME)
    s.add_project(args.id, args.name)
    s.save()


def show(args):
    s = Storage.pwd(STORAGE_NAME)
    if args.id is None:
        for proj in s.projects.values():
            print(f"{proj.name} ({proj.id}): {len(proj.tasks)} task(s)")

        return

    if args.id not in s.projects:
        raise ValueError(f"Project '{args.id}' does not exist")

    subprocess.run(["task", f"proj:{args.id}"]).check_returncode()


def create_parsers() -> ArgumentParser:
    parser = ArgumentParser("A file-based project manager")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("id", help="The project id")
    add_parser.add_argument("name", help="The project name")
    add_parser.set_defaults(func=add)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("id", help="The project id", nargs="?")
    show_parser.set_defaults(func=show)

    return parser


def main():
    args = create_parsers().parse_args()

    try:
        args.func(args)
    except AttributeError:
        create_parsers().print_usage()
        exit(1)
