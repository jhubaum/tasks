from argparse import ArgumentParser
import subprocess
from pathlib import Path

from .storage import Storage, Project

STORAGE_NAME = Path.home() / "notes/projects"


def add(args):
    s = Storage.pwd(STORAGE_NAME)
    s.add_project(Project.new(args.id, args.name, args.tags))
    s.save()


def show(args):
    s = Storage.pwd(STORAGE_NAME)
    if args.id is None:
        for proj in s.projects.values():
            proj.print_title()
        return

    if args.id not in s.projects:
        raise ValueError(f"Project '{args.id}' does not exist")

    s.projects[args.id].print_title()
    subprocess.run(["task", f"proj:{args.id}"]).check_returncode()


def create_parsers() -> ArgumentParser:
    parser = ArgumentParser("A file-based project manager")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("id", help="The project id")
    add_parser.add_argument("name", help="The project name")
    add_parser.add_argument("--tags", help="Tags for the project", nargs="*")
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
