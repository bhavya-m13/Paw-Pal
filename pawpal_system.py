from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    id: str
    pet_id: str
    title: str
    description: str
    due_date: datetime
    category: str
    is_completed: bool
    priority: Priority
    completed_at: datetime | None = None


@dataclass
class Pet:
    id: str
    owner_id: str
    name: str
    species: str
    breed: str
    birth_date: datetime
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> bool:
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

    def remove_pet(self, pet_id: str) -> bool:
        pass

    def get_pets(self) -> list[Pet]:
        pass


class Scheduler:
    def __init__(self, owners: list[Owner]):
        self.owners = owners
        self._task_cache: list[Task] = []

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

    def _rebuild_cache(self) -> None:
        pass
