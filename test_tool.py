from google.adk.tools import ToolContext
from agents.greeting_agent import request_verification_tool

class MockContext:
    def __init__(self):
        self.state = {"temp:pending_user_name": "Narci"}

ctx = MockContext()
result = request_verification_tool(ctx, "haerinarges@gmail.com")
print(result)