class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, func):
        self.tools[func.__name__] = func

    def get_tool(self, name):
        return self.tools[name]

    def get_all_tools(self):
        return self.tools.values()
