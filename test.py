import io
import os
import unittest
import unittest.mock

from solve_me import TasksCommand


def reset_files():
    try:
        os.remove(TasksCommand.TASKS_FILE)
    except OSError:
        pass
    try:
        os.remove(TasksCommand.COMPLETED_TASKS_FILE)
    except OSError:
        pass


def load_tasks_file():
    current_items = {}
    try:
        file = open(TasksCommand.TASKS_FILE, "r")
        for line in file.readlines():
            item = line[:-1].split(" ")
            current_items[int(item[0])] = " ".join(item[1:])
        file.close()
    except Exception:
        pass
    return current_items


def load_completed_file():
    tasks = []
    try:
        file = open(TasksCommand.COMPLETED_TASKS_FILE, "r")
        tasks = [i[:-1] for i in file.readlines()]
        file.close()
    except Exception:
        pass
    return tasks


class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.command_object = TasksCommand()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def assert_stdout(self, command, args, expected_output, mock_stdout):
        if command == "add":
            self.command_object.add(args)
        elif command == "done":
            self.command_object.done(args)
        elif command == "delete":
            self.command_object.delete(args)
        elif command == "ls":
            self.command_object.ls()
        elif command == "report":
            self.command_object.report()
        elif command == "help":
            self.command_object.help()
        self.assertIn(expected_output, mock_stdout.getvalue())

    def test_add_tasks(self):
        self.assert_stdout("add",["5", "Test Task 5"], "Added task: \"Test Task 5\" with priority 5")
        tasks = load_tasks_file()
        self.assertEqual(tasks[5], "Test Task 5")

    def test_add_same_tasks(self):
        self.assert_stdout("add",["2", "Task 3"], "Added task: \"Task 3\" with priority 2")
        self.assert_stdout("add", ["2", "Task 2"], "Added task: \"Task 2\" with priority 2")
        tasks = load_tasks_file()
        self.assertEqual(tasks[3], "Task 3")

    def test_add_complete_tasks(self):
        self.assert_stdout("add", ["10", "Task 10"], "Added task: \"Task 10\" with priority 10")
        self.assert_stdout("done", ["10"], "Marked item as done.")
        tasks = load_tasks_file()
        self.assertFalse("10" in tasks)
        completed = load_completed_file()
        self.assertTrue("Task 10" in completed)

    def test_complete_nonexisting_tasks(self):
        self.assert_stdout("done", ["1500"], "Error: no incomplete item with priority 1500 exists.")

    def test_delete_tasks(self):
        self.assert_stdout("add", ["15", "Task 15"], "Added task: \"Task 15\" with priority 15")
        self.assert_stdout("delete", ["15"], "Deleted item with priority 15")
        tasks = load_tasks_file()
        self.assertFalse("15" in tasks)
        completed = load_completed_file()
        self.assertFalse("Task 15" in completed)

    def test_delete_nonexisting_tasks(self):
        self.assert_stdout("delete", ["1500"], "Error: item with priority 1500 does not exist. Nothing deleted.")

    def test_ls_tasks(self):
        self.assert_stdout("ls", [], '1. Task 2 [2]\n2. Task 3 [3]\n3. Test Task 5 [5]')

    def test_report(self):
        self.assert_stdout("report", [], "Pending : 3\n1. Task 2 [2]\n2. Task 3 [3]\n3. Test Task 5 [5]\n\nCompleted : 1\n1. Task 10")

reset_files()
unittest.main()
