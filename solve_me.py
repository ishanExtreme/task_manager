from http.server import BaseHTTPRequestHandler, HTTPServer
from incomplete_task import render_route_tasks
from complete_task import render_route_completed

class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = [task[0:-1] for task in file.readlines()]
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        """
        Add task to list
    
        Task is added according to the priority and than it is saved in file
    
        Parameters:
        args: list of arguments
    
        """
        if(len(args) < 2):
            print("Error: Missing tasks string. Nothing added!")
        else:

            inc_priority = int(args[0])
            while(True):
                temp = None
                temp_arr = [key for key in self.current_items if key == inc_priority]
                for key in temp_arr:
                        self.current_items[inc_priority+1] = self.current_items[inc_priority]
                        inc_priority+=1
                if(temp == None):
                    break

            # self.current_items[int(item[0])] = " ".join(item[1:])
            self.current_items[int(args[0])] = args[1]
            self.write_current()
            print(f'Added task: "{args[1]}" with priority {args[0]}')


    def done(self, args):
        """
        Mark a task as complete
    
        Use the done command to mark an item as completed by its index.
    
        Parameters:
        args: list of arguments
    
        """

        if(len(args) < 1):
             print("Error: Missing NUMBER for marking tasks as done.")
        else:
            try:
                index = int(args[0])
                # delete from incomplete list
                task_name = self.current_items.pop(index)
                # reflect it to file
                self.write_current()
                # add name to complete list
                self.completed_items.append(task_name)
                # reflect to file
                self.write_completed()

                print("Marked item as done.")
        
            except:
                print(f"Error: no incomplete item with priority {index} exists.")

    def delete(self, args):
        """
        Delete a task
    
        Use the del command to remove an item by its index.
    
        Parameters:
        args: list of arguments

        """

        if(len(args) < 1):
             print("Error: Missing NUMBER for deleting tasks.")
        else:
            try:
                index = int(args[0])
                self.current_items.pop(index)
                self.write_current()
                print(f"Deleted item with priority {index}")
        
            except:
                print(f"Error: item with priority {index} does not exist. Nothing deleted.")

    def ls(self):
        """
        list tasks
    
        Use the ls command to see all the items that are not yet complete, in ascending order of priority.
    
        """

        # empty list
        if(len(self.current_items) == 0):
            print("There are no pending tasks!")
        count = 1
        for key in self.current_items:
            print(f"{count}. {self.current_items[key]} [{key}]")
            count+=1

    def report(self):
        """
        Generate report
    
        Show the number of complete and incomplete items in the list. and the complete and incomplete items grouped together.
    
        """

        # incomplete tasks
        print(f"Pending : {len(self.current_items)}")
        # print pending tasks
        count = 1
        for key in self.current_items:
            print(f"{count}. {self.current_items[key]} [{key}]")
            count+=1
        
        # complete tasks
        print(f"\nCompleted : {len(self.completed_items)}")
        # print completed tasks
        for index,task in enumerate(self.completed_items):
            print(f"{index+1}. {task}") 
            
    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks as HTML
        return render_route_tasks(self.current_items)

    def render_completed_tasks(self):
        
        # Complete this method to return all completed tasks as HTML
        return render_route_completed(self.completed_items)


class TasksServer(BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        task_command_object.read_current()
        task_command_object.read_completed()
        # if self.path == "/":
        #     content = render_home()
        if self.path == "/tasks":
            print(task_command_object.current_items)
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            print(task_command_object.completed_items)
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
