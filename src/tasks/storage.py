from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import subprocess
import json
import logging

# TODO: Since I'm currently only storing projects, and they already have files associated with them
# the database isn't necessary
DATABASE = "data.json"

# TODO: Use pydantic for storing jsons


@dataclass
class Task:
    id: int
    title: str
    description: Optional[str]
    status: str
    project: Optional[str] = None


def context_filter(context):
    match context:
        case "work":
            return lambda tags: "sh" in tags or "nvim" in tags or "dotfile" in tags
        case "private":
            return lambda tags: "sh" not in tags
        case _:
            raise ValueError(f"Unsupported context '{context}'")


def iter_tasks() -> List[Task]:
    tasks = subprocess.run(["task", "export"], stdout=subprocess.PIPE)
    tasks.check_returncode()

    context_res = subprocess.run(["task", "_get", "rc.context"], stdout=subprocess.PIPE)
    context_res.check_returncode()
    is_in_context = context_filter(context_res.stdout.decode("utf8").strip())
    for task in json.loads(tasks.stdout):
        if task["status"] == "deleted" or task["status"] == "completed":
            continue
        if not is_in_context(task.get("tags", {})):
            continue
        title = task["description"].strip()
        description = None
        if "\n" in title:
            title, description = title.split("\n", maxsplit=1)
        yield Task(
            id=task["id"],
            title=title,
            description=description,
            status=task["status"],
            project=task.get("project"),
        )


@dataclass
class Project:
    id: str
    name: str
    tasks: List[Task]
    tags: List[str]

    def print_title(self):
        tags = ""
        if len(self.tags) > 0:
            tags = " +" + " +".join(self.tags)
        print(f"{self.name} ({self.id}){tags}: {len(self.tasks)} task(s)")


@dataclass
class Storage:
    root: Path
    tasks: List[Task]
    projects: Dict[str, Project]

    @staticmethod
    def load(path: Path) -> "Storage":
        file = path / DATABASE

        if not file.exists():
            return Storage(root=path, tasks=[], projects={})

        with file.open("r") as f:
            data = json.load(f)

        projects = {}

        for proj in data["projects"]:
            projects[proj["id"]] = Project(
                id=proj["id"], name=proj["name"], tasks=[], tags=proj["tags"]
            )

        tasks = []
        for task in iter_tasks():
            if task.project is None:
                tasks.append(task)
                continue

            if task.project not in projects:
                logging.warning(
                    f"Project '{task.project}' does not exist. Task is ignored"
                )
                continue

            projects[task.project].tasks.append(task)

        return Storage(root=path, tasks=tasks, projects=projects)

    def save(self):
        file = self.root / DATABASE

        data = {}
        data["projects"] = [
            dict(id=p.id, name=p.name, tags=p.tags) for p in self.projects.values()
        ]

        with file.open("w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def pwd(name: str):
        return Storage.load(Path.cwd() / name)

    def add_project(self, id: str, name: Optional[str], tags: List[str]):
        if name is None:
            name = id
        assert id not in self.projects
        self.projects[id] = Project(id=id, name=name, tasks=[], tags=tags)

        self.root.mkdir(exist_ok=True)
        (self.root / f"{id}.md").touch()
        (self.root / f"{id}").mkdir()

    def delete_project(self, id: str):
        assert id in self.projects
        (self.root / f"{id}.md").unlink(missing_ok=True)
        if (self.root / f"{id}").is_dir():
            (self.root / f"{id}").rmdir()

        for task in self.projects[id]:
            subprocess.run(["task", "delete", str(task.id)]).check_returncode()
        del self.projects[id]
        self.save()
