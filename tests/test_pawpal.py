import unittest
from datetime import datetime
from pawpal_system import Task, Pet, Priority


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


if __name__ == "__main__":
    unittest.main()
