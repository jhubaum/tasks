from argparse import ArgumentParser

from .storage import Storage

STORAGE_NAME = "storage"

def add(args):
    s = Storage.pwd(STORAGE_NAME)
    if args.project is not None and args.project not in s.projects:
        print(f"Created new project '{args.project}'")
        s.add_project(args.project)
    s.add_task(args.name, args.project)
    s.save()


def show(args):
    s = Storage.pwd(STORAGE_NAME)
    for index, task in enumerate(s.tasks.values()):
        print(f"{index} | {task.title} | {task.project_id}")


def show_projects(args):
    s = Storage.pwd(STORAGE_NAME)
    for proj in s.projects.values():
        print(f"Proj '{proj.id}' ({len(proj.tasks)} task(s))")


def delete_project(args):
    s = Storage.pwd(STORAGE_NAME)
    s.delete_project(args.project)
    s.save()


def create_parsers() -> ArgumentParser:
    parser = ArgumentParser("A file-based task manager")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("name", help="The name of the task")
    add_parser.add_argument("--project", "-p", help="The project id")
    add_parser.set_defaults(func=add)


    show_parser = subparsers.add_parser("show")
    show_parser.set_defaults(func=show)

    projects_parser = subparsers.add_parser("projects")
    projects_subparsers = projects_parser.add_subparsers()
    projects_show_parser = projects_subparsers.add_parser("show")
    projects_show_parser.set_defaults(func=show_projects)

    projects_delete_parser = projects_subparsers.add_parser("delete")
    projects_delete_parser.add_argument("project", help="The project id")
    projects_delete_parser.set_defaults(func=delete_project)



    return parser


def main():
    args = create_parsers().parse_args()

    try:
        func = args.func
    except AttributeError:
        func = show

    func(args)
