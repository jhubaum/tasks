from argparse import ArgumentParser
from pathlib import Path
from .storage import Storage

STORAGE_NAME = Path.home() / "notes/projects"


def add(args):
    s = Storage.pwd(STORAGE_NAME)
    s.add_project(args.id, args.name)
    s.save()


def show(args):
    s = Storage.pwd(STORAGE_NAME)
    for proj in s.projects.values():
        print(f"{proj.name}: {len(proj.tasks)} task(s)")


def create_parsers() -> ArgumentParser:
    parser = ArgumentParser("A file-based project manager")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("id", help="The project id")
    add_parser.add_argument("name", help="The project name")
    add_parser.set_defaults(func=add)

    show_parser = subparsers.add_parser("show")
    show_parser.set_defaults(func=show)

    return parser


def main():
    args = create_parsers().parse_args()

    try:
        func = args.func
    except AttributeError:
        func = show

    func(args)
