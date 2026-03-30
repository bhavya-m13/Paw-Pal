import unittest
from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, Priority


def make_task(task_id: str = "t1", pet_id: str = "p1") -> Task:
    return Task(
        id=task_id,
        pet_id=pet_id,
        title="Test Task",
        description="A test task",
        due_date=datetime(2026, 4, 1, 9, 0),
        category="Health",
        is_completed=False,
        priority=Priority.MEDIUM,
    )


def make_pet(pet_id: str = "p1") -> Pet:
    return Pet(
        id=pet_id,
        owner_id="o1",
        name="Buddy",
        species="Dog",
        breed="Labrador",
        birth_date=datetime(2020, 1, 1),
    )


class TestTaskCompletion(unittest.TestCase):
    def test_mark_complete_sets_is_completed(self):
        task = make_task()
        task.mark_complete()
        self.assertTrue(task.is_completed)

    def test_mark_complete_sets_completed_at(self):
        task = make_task()
        before = datetime.now()
        task.mark_complete()
        after = datetime.now()
        self.assertIsNotNone(task.completed_at)
        self.assertGreaterEqual(task.completed_at, before)
        self.assertLessEqual(task.completed_at, after)

    def test_incomplete_task_has_no_completed_at(self):
        task = make_task()
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.completed_at)


class TestTaskAddition(unittest.TestCase):
    def test_add_task_increases_count(self):
        pet = make_pet()
        self.assertEqual(len(pet.tasks), 0)
        pet.add_task(make_task("t1"))
        self.assertEqual(len(pet.tasks), 1)

    def test_add_multiple_tasks_increases_count(self):
        pet = make_pet()
        pet.add_task(make_task("t1"))
        pet.add_task(make_task("t2"))
        pet.add_task(make_task("t3"))
        self.assertEqual(len(pet.tasks), 3)

    def test_added_task_is_retrievable(self):
        pet = make_pet()
        task = make_task("t1")
        pet.add_task(task)
        self.assertIn(task, pet.get_tasks())


def make_scheduler_with_pet() -> tuple[Scheduler, Pet]:
    """Return a Scheduler and its single Pet, ready to receive tasks."""
    owner = Owner(id="o1", name="Jordan", email="j@example.com", phone="555-0100")
    pet = make_pet("p1")
    owner.add_pet(pet)
    scheduler = Scheduler(owners=[owner])
    return scheduler, pet


class TestSortByTime(unittest.TestCase):
    def test_tasks_sorted_earliest_first(self):
        scheduler, pet = make_scheduler_with_pet()
        for hour, task_id in [(14, "t3"), (8, "t1"), (22, "t4"), (12, "t2")]:
            t = make_task(task_id)
            t.due_date = datetime(2026, 4, 1, hour, 0)
            pet.add_task(t)
        scheduler._rebuild_cache()

        sorted_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())
        hours = [t.due_date.hour for t in sorted_tasks]
        self.assertEqual(hours, sorted(hours))

    def test_empty_list_returns_empty(self):
        scheduler, _ = make_scheduler_with_pet()
        self.assertEqual(scheduler.sort_by_time([]), [])

    def test_single_task_returns_single(self):
        scheduler, pet = make_scheduler_with_pet()
        task = make_task("t1")
        pet.add_task(task)
        scheduler._rebuild_cache()
        result = scheduler.sort_by_time(scheduler.get_all_tasks())
        self.assertEqual(len(result), 1)

    def test_tasks_same_time_sort_is_stable(self):
        """Tasks sharing the same HH:MM should preserve their original relative order."""
        scheduler, pet = make_scheduler_with_pet()
        t1 = make_task("t1")
        t2 = make_task("t2")
        t1.due_date = datetime(2026, 4, 1, 9, 0)
        t2.due_date = datetime(2026, 4, 2, 9, 0)  # different date, same time
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler._rebuild_cache()

        result = scheduler.sort_by_time(scheduler.get_all_tasks())
        # Both at "09:00" — original insertion order (t1, t2) must be preserved
        self.assertEqual([r.id for r in result], ["t1", "t2"])


class TestRecurrenceLogic(unittest.TestCase):
    def test_daily_task_creates_next_task_one_day_later(self):
        scheduler, pet = make_scheduler_with_pet()
        task = make_task("t1")
        task.frequency = "daily"
        task.due_date = datetime(2026, 4, 1, 9, 0)
        pet.add_task(task)
        scheduler._rebuild_cache()

        next_task = scheduler.mark_task_complete("t1")

        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.due_date, datetime(2026, 4, 2, 9, 0))

    def test_weekly_task_creates_next_task_seven_days_later(self):
        scheduler, pet = make_scheduler_with_pet()
        task = make_task("t1")
        task.frequency = "weekly"
        task.due_date = datetime(2026, 4, 1, 9, 0)
        pet.add_task(task)
        scheduler._rebuild_cache()

        next_task = scheduler.mark_task_complete("t1")

        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.due_date, datetime(2026, 4, 8, 9, 0))

    def test_one_time_task_returns_none(self):
        scheduler, pet = make_scheduler_with_pet()
        task = make_task("t1")
        task.frequency = None
        pet.add_task(task)
        scheduler._rebuild_cache()

        result = scheduler.mark_task_complete("t1")
        self.assertIsNone(result)

    def test_original_task_is_marked_complete_after_recurrence(self):
        scheduler, pet = make_scheduler_with_pet()
        task = make_task("t1")
        task.frequency = "daily"
        pet.add_task(task)
        scheduler._rebuild_cache()

        scheduler.mark_task_complete("t1")
        self.assertTrue(task.is_completed)

    def test_next_task_inherits_frequency(self):
        """The cloned task must itself be recurring, not a one-time task."""
        scheduler, pet = make_scheduler_with_pet()
        task = make_task("t1")
        task.frequency = "daily"
        pet.add_task(task)
        scheduler._rebuild_cache()

        next_task = scheduler.mark_task_complete("t1")
        self.assertEqual(next_task.frequency, "daily")

    def test_chained_recurrence_creates_third_task(self):
        """Completing the generated next task must produce a further next task."""
        scheduler, pet = make_scheduler_with_pet()
        task = make_task("t1")
        task.frequency = "daily"
        task.due_date = datetime(2026, 4, 1, 9, 0)
        pet.add_task(task)
        scheduler._rebuild_cache()

        next1 = scheduler.mark_task_complete("t1")
        next2 = scheduler.mark_task_complete(next1.id)

        self.assertIsNotNone(next2)
        self.assertEqual(next2.due_date, datetime(2026, 4, 3, 9, 0))

    def test_nonexistent_task_id_returns_none(self):
        scheduler, _ = make_scheduler_with_pet()
        self.assertIsNone(scheduler.mark_task_complete("does-not-exist"))


class TestConflictDetection(unittest.TestCase):
    def test_two_tasks_at_same_time_flagged_as_conflict(self):
        scheduler, pet = make_scheduler_with_pet()
        t1, t2 = make_task("t1"), make_task("t2")
        t1.title, t2.title = "Morning Walk", "Morning Feed"
        t1.due_date = t2.due_date = datetime(2026, 4, 1, 8, 0)
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler._rebuild_cache()

        conflicts = scheduler.get_conflicts(scheduler.get_all_tasks())
        self.assertEqual(len(conflicts), 1)

    def test_conflict_message_contains_both_task_titles(self):
        scheduler, pet = make_scheduler_with_pet()
        t1, t2 = make_task("t1"), make_task("t2")
        t1.title, t2.title = "Walk", "Feed"
        t1.due_date = t2.due_date = datetime(2026, 4, 1, 8, 0)
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler._rebuild_cache()

        conflict_msg = scheduler.get_conflicts(scheduler.get_all_tasks())[0]
        self.assertIn("Walk", conflict_msg)
        self.assertIn("Feed", conflict_msg)

    def test_tasks_at_different_times_produce_no_conflict(self):
        scheduler, pet = make_scheduler_with_pet()
        t1, t2 = make_task("t1"), make_task("t2")
        t1.due_date = datetime(2026, 4, 1, 8, 0)
        t2.due_date = datetime(2026, 4, 1, 9, 0)
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler._rebuild_cache()

        self.assertEqual(scheduler.get_conflicts(scheduler.get_all_tasks()), [])

    def test_three_tasks_at_same_time_all_appear_in_conflict(self):
        scheduler, pet = make_scheduler_with_pet()
        tasks = [make_task(f"t{i}") for i in range(1, 4)]
        for i, t in enumerate(tasks):
            t.title = f"Task{i+1}"
            t.due_date = datetime(2026, 4, 1, 8, 0)
            pet.add_task(t)
        scheduler._rebuild_cache()

        conflicts = scheduler.get_conflicts(scheduler.get_all_tasks())
        self.assertEqual(len(conflicts), 1)
        for i in range(1, 4):
            self.assertIn(f"Task{i}", conflicts[0])

    def test_empty_task_list_returns_no_conflicts(self):
        scheduler, _ = make_scheduler_with_pet()
        self.assertEqual(scheduler.get_conflicts([]), [])

    def test_conflict_timestamp_appears_in_message(self):
        scheduler, pet = make_scheduler_with_pet()
        t1, t2 = make_task("t1"), make_task("t2")
        t1.due_date = t2.due_date = datetime(2026, 4, 1, 8, 0)
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler._rebuild_cache()

        conflict_msg = scheduler.get_conflicts(scheduler.get_all_tasks())[0]
        self.assertIn("2026-04-01 08:00", conflict_msg)


if __name__ == "__main__":
    unittest.main()
