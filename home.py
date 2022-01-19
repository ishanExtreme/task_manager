def render_home():
    return """
    <div style="width:100%;height:100%;display: flex; flex-flow: column wrap; justify-content: center; align-items: center;">
        <button style="padding: 10px;border-radius: 5px;background-color: steelblue;color: white; cursor: pointer;" onclick="window.location.href='./tasks';">Incompleted Tasks</button>
        <br/>
        <button style="padding: 10px;border-radius: 5px;background-color: green;color: white; cursor: pointer;" onclick="window.location.href='./completed';">Completed Tasks</button>
    </div>
    """