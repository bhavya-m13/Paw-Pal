from dataclasses import dataclass, field
from datetime import datetime, timedelta
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

    def mark_complete(self) -> None:
        """Mark the task as completed and record the completion timestamp."""
        self.is_completed = True
        self.completed_at = datetime.now()


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
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID; returns True if found and removed, False otherwise."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    id: str
    name: str
    email: str
    phone: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Append a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by ID; returns True if found and removed, False otherwise."""
        for i, pet in enumerate(self.pets):
            if pet.id == pet_id:
                self.pets.pop(i)
                return True
        return False

    def get_pets(self) -> list[Pet]:
        """Return a shallow copy of this owner's pet list."""
        return list(self.pets)


class Scheduler:
    def __init__(self, owners: list[Owner]):
        """Initialize the scheduler with a list of owners and build the task cache."""
        self.owners = owners
        self._task_cache: list[Task] = []
        self._rebuild_cache()

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        """Return all cached tasks belonging to the given pet ID."""
        return [task for task in self._task_cache if task.pet_id == pet_id]

    def get_all_tasks(self) -> list[Task]:
        """Return a shallow copy of all cached tasks across every owner and pet."""
        return list(self._task_cache)

    def sort_by_due_date(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted ascending by due date."""
        return sorted(tasks, key=lambda t: t.due_date)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted descending by priority (HIGH first)."""
        return sorted(tasks, key=lambda t: t.priority.value, reverse=True)

    def filter_by_category(self, tasks: list[Task], category: str) -> list[Task]:
        """Return only tasks whose category matches the given string."""
        return [task for task in tasks if task.category == category]

    def filter_by_completion(self, tasks: list[Task], is_completed: bool) -> list[Task]:
        """Return only tasks matching the given completion status."""
        return [task for task in tasks if task.is_completed == is_completed]

    def get_upcoming_tasks(self, days: int) -> list[Task]:
        """Return incomplete tasks due within the next N days from now."""
        cutoff = datetime.now() + timedelta(days=days)
        return [
            task for task in self._task_cache
            if not task.is_completed and task.due_date <= cutoff
        ]

    def _rebuild_cache(self) -> None:
        """Flatten all tasks from every owner's pets into the internal cache."""
        self._task_cache = [
            task
            for owner in self.owners
            for pet in owner.pets
            for task in pet.tasks
        ]
