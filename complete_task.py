def render_route_completed(taskList):
    content = """
    <h1 style="text-align: center;">Completed Tasks</h1>
    <br/>
    <div style="display: flex; flex-flow: column wrap; justify-content: center; align-items: center;">

    """
    for task in taskList:
        newTask = f"""
        <h3 style="color: green;">
            {task}
        </h3>
        """
        content+=newTask

    # print(content)

    return content+"</div>"