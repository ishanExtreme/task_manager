import sys
from solve_me import TasksCommand


try:
    # Extract Arguments from Command Line
    cli_args = sys.argv[1:]
    command = None
    arguments = None
    if len(cli_args) == 0:
        raise Exception("Arguments not supplied")
    elif len(cli_args) == 1:
        command = cli_args[0]
    if len(cli_args) > 1:
        command = cli_args[0]
        arguments = cli_args[1:]
    # Run the Task Command Class with the arguments supplied
    obj1 = TasksCommand()
    obj1.run(command, arguments)
    # obj2 = TasksCommand()
    # print("For obj1=>")
    # print("Icompeted Items:")
    # print(obj1.current_items)
    # print("Completed Items:")
    # print(obj1.completed_items)
    # print("For obj2=>")
    # print("Icompeted Items:")
    # print(obj2.current_items)
    # print("Completed Items:")
    # print(obj2.completed_items)
except Exception as e:
    print(str(e))
