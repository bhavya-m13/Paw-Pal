from collections import defaultdict
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
    frequency: str | None = None  # "daily", "weekly", or None for one-time tasks

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

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by their time-of-day in ascending order.

        Extracts the "HH:MM" portion of each task's due_date and uses it as
        the sort key. Because the time is zero-padded 24-hour format, plain
        string comparison produces the correct chronological order without
        needing to parse the datetime again.

        Args:
            tasks: The list of Task objects to sort. The original list is not
                modified; a new sorted list is returned.

        Returns:
            A new list of Task objects ordered from the earliest time-of-day
            (e.g. "08:00") to the latest (e.g. "23:30"). Tasks on different
            dates but with the same time of day will be treated as equal by
            this sort; use sort_by_due_date for full date+time ordering.

        Example:
            >>> sorted_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())
        """
        return sorted(tasks, key=lambda t: t.due_date.strftime("%H:%M"))

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted descending by priority (HIGH first)."""
        return sorted(tasks, key=lambda t: t.priority.value, reverse=True)

    def filter_by_category(self, tasks: list[Task], category: str) -> list[Task]:
        """Return only tasks whose category matches the given string."""
        return [task for task in tasks if task.category == category]

    def filter_by_completion(self, tasks: list[Task], is_completed: bool) -> list[Task]:
        """Return only tasks matching the given completion status."""
        return [task for task in tasks if task.is_completed == is_completed]

    def filter_by_pet_name(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Filter tasks to only those belonging to a pet with the given name.

        Performs a case-insensitive name match across every pet registered
        under any owner in the scheduler. The match is resolved to a set of
        pet IDs first, so the final task filter is an O(1) membership test
        per task rather than a string comparison.

        Args:
            tasks: The pool of Task objects to filter.
            pet_name: The pet name to match (e.g. "Buddy"). Comparison is
                case-insensitive, so "buddy", "BUDDY", and "Buddy" all match.

        Returns:
            A new list containing only the tasks whose pet_id belongs to a
            pet whose name matches pet_name. Returns an empty list if no pet
            with that name is found.

        Example:
            >>> buddy_tasks = scheduler.filter_by_pet_name(all_tasks, "Buddy")
        """
        matching_ids = {
            pet.id
            for owner in self.owners
            for pet in owner.pets
            if pet.name.lower() == pet_name.lower()
        }
        return [task for task in tasks if task.pet_id in matching_ids]

    def mark_task_complete(self, task_id: str) -> Task | None:
        """Mark a task as complete and auto-schedule the next occurrence if recurring.

        Searches the owner→pet→task hierarchy for the given task ID using a
        short-circuiting generator (next()), so iteration stops the moment the
        task is found. After marking the task complete, the method checks its
        frequency field:

        - "daily"  → clones the task with due_date + 1 day via timedelta(days=1)
        - "weekly" → clones the task with due_date + 7 days via timedelta(weeks=1)
        - None     → no new task is created; the task is simply completed

        The cloned task inherits all attributes (title, description, category,
        priority, frequency) from the original and receives a unique ID in the
        form "{original_id}_next_{YYYYMMDD}". The internal task cache is
        rebuilt after every call so callers see the updated state immediately.

        Args:
            task_id: The unique string ID of the task to complete.

        Returns:
            The newly created Task for the next occurrence if the completed
            task was recurring, or None if the task was one-time or if no
            task with the given ID was found.

        Example:
            >>> next_task = scheduler.mark_task_complete("t1")
            >>> if next_task:
            ...     print(next_task.due_date)  # tomorrow at the same time
        """
        # Locate the task and its owning pet — next() short-circuits on first match
        match = next(
            ((pet, task) for owner in self.owners
                         for pet in owner.pets
                         for task in pet.tasks
                         if task.id == task_id),
            None,
        )
        if match is None:
            return None

        owning_pet, target_task = match
        target_task.mark_complete()

        # Auto-schedule next occurrence for recurring tasks
        if target_task.frequency == "daily":
            delta = timedelta(days=1)
        elif target_task.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            self._rebuild_cache()
            return None

        next_due = target_task.due_date + delta
        next_task = Task(
            id=f"{target_task.id}_next_{next_due.strftime('%Y%m%d')}",
            pet_id=target_task.pet_id,
            title=target_task.title,
            description=target_task.description,
            due_date=next_due,
            category=target_task.category,
            is_completed=False,
            priority=target_task.priority,
            frequency=target_task.frequency,
        )
        owning_pet.add_task(next_task)
        self._rebuild_cache()
        return next_task

    def get_conflicts(self, tasks: list[Task]) -> list[str]:
        """Detect scheduling conflicts and return human-readable warning messages.

        Groups tasks into buckets keyed by "YYYY-MM-DD HH:MM". Any bucket
        that contains two or more tasks is a conflict, regardless of whether
        the clashing tasks belong to the same pet or different pets. This is a
        lightweight, non-crashing strategy: it never raises an exception and
        never modifies any task — it only reports.

        Args:
            tasks: The list of Task objects to inspect for conflicts. Typically
                the full result of get_all_tasks(), but can be any subset.

        Returns:
            A list of warning strings, one per conflicting time slot, in the
            format:
                "[CONFLICT] YYYY-MM-DD HH:MM — 'Task A' (Pet1) vs 'Task B' (Pet2)"
            Returns an empty list when no conflicts are found.

        Example:
            >>> warnings = scheduler.get_conflicts(scheduler.get_all_tasks())
            >>> for w in warnings:
            ...     print(w)
            [CONFLICT] 2026-03-30 08:00 — 'Morning Walk' (Buddy) vs 'Morning Feeding' (Luna)
        """
        warnings: list[str] = []
        pet_lookup = {
            pet.id: pet.name
            for owner in self.owners
            for pet in owner.pets
        }
        # Group tasks by their "YYYY-MM-DD HH:MM" bucket
        buckets: dict[str, list[Task]] = defaultdict(list)
        for task in tasks:
            key = task.due_date.strftime("%Y-%m-%d %H:%M")
            buckets[key].append(task)

        for time_key, grouped in buckets.items():
            if len(grouped) < 2:
                continue
            names = [
                f"'{t.title}' ({pet_lookup.get(t.pet_id, 'Unknown')})"
                for t in grouped
            ]
            warnings.append(
                f"[CONFLICT] {time_key} — {' vs '.join(names)}"
            )
        return warnings

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
