from argparse import ArgumentParser
import subprocess
from pathlib import Path
from typing import List

from .storage import Storage, Project

STORAGE_NAME = Path.home() / "notes/projects"

def week_review() -> List[str]:
    return [
        "Skim Bujo and Calendar from last week",
        "Move open tasks back to monthly log",
        "Think about what went well, and where to go next",
        "Write a short summary in monthly log",
    ]

    return []

def monthly_review() -> List[str]:
    return week_review() + [
        "Review all open tasks and past weeks",
        "Look at quarterly plan and pick projects",
    ]

TEMPLATES = {
    "review_w": week_review,
    "review_m": monthly_review
}

def apply_template(proj: Project , template_id: str):
    tasks = TEMPLATES[template_id]()
    for task in tasks:
        subprocess.run(["task", "add", f"proj:{proj.id}", "due:today", f'"{task}"']).check_returncode()


def add(args):
    if " " in args.id:
        raise ValueError("Invalid project id: It contains spaces")
    s = Storage.pwd(STORAGE_NAME)
    proj = Project.new(args.id, args.name, args.tags)
    if args.template is not None:
        apply_template(proj, args.template)

    s.add_project(proj)


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


def delete(args):
    s = Storage.pwd(STORAGE_NAME)
    s.delete_project(args.id)


def create_parsers() -> ArgumentParser:
    parser = ArgumentParser("A file-based project manager")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("id", help="The project id")
    add_parser.add_argument("name", help="The project name", nargs="?")
    add_parser.add_argument("--tags", help="Tags for the project", nargs="*")
    add_parser.add_argument("--template", help="The template id to use for project creation", choices=TEMPLATES.keys())
    add_parser.set_defaults(func=add)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("id", help="The project id", nargs="?")
    show_parser.set_defaults(func=show)

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("id", help="The project id")
    delete_parser.set_defaults(func=delete)

    return parser


def main():
    args = create_parsers().parse_args()

    func = None
    try:
        func = args.func
    except AttributeError:
        create_parsers().print_usage()
        exit(1)
    func(args)
