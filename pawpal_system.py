from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    id: str
    title: str
    description: str
    due_date: datetime
    category: str
    is_completed: bool
    priority: str


@dataclass
class Pet:
    id: str
    name: str
    species: str
    breed: str
    birth_date: datetime
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    id: str
    name: str
    email: str
    phone: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_id: str) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass

    def sort_by_due_date(self, tasks: list[Task]) -> list[Task]:
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def filter_by_category(self, tasks: list[Task], category: str) -> list[Task]:
        pass

    def filter_by_completion(self, tasks: list[Task], is_completed: bool) -> list[Task]:
        pass

    def get_upcoming_tasks(self, days: int) -> list[Task]:
        pass
