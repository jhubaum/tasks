from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import uuid

import json

DATABASE = "data.json"

# TODO: Use pydantic for storing jsons

@dataclass
class Task:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[str] = None


@dataclass
class Project:
    id: str
    tasks: List[str] # A list of uuids for tasks

@dataclass
class Storage:
    root: Path
    tasks: Dict[str, Task]
    projects: Dict[str, Project]


    @staticmethod
    def load(path: Path) -> "Storage":
        file = path / DATABASE

        if not file.exists():
            return Storage(root=path, tasks={}, projects={})

        with file.open('r') as f:
            data = json.load(f)

        tasks = {}
        projects = {}

        for proj in data['projects']:
            projects[proj['id']] = Project(id=proj['id'], tasks=proj['tasks'])

        for id, task in data['tasks'].items():
            tasks[id] = Task(id=id, title=task['title'], project_id=task.get('project_id'))


        return Storage(root=path, tasks=tasks, projects=projects)

    def save(self):
        file = self.root / DATABASE

        data = {}
        data["tasks"] = { id: dict(title=t.title, project_id=t.project_id) for id, t in self.tasks.items() }
        data["projects"] = [ dict(id=p.id, tasks=p.tasks) for p in self.projects.values() ]

        with file.open('w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


    @staticmethod
    def pwd(name: str):
        return Storage.load(Path.cwd() / name)

    def add_task(self, task: str, proj_id: Optional[str]):
        obj = Task(title=task, project_id=proj_id)

        if proj_id is not None:
            assert proj_id in self.projects
            self.projects[proj_id].tasks.append(obj.id)

        assert obj.id not in self.tasks
        self.tasks[obj.id] = obj

    def add_project(self, id: str):
        self.projects[id] = Project(id=id, tasks=[])
