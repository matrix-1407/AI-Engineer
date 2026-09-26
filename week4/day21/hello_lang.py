from typing import TypedDict
from langgraph.graph import END, StateGraph

class State(TypedDict):
    name: str
    message: str

def greet(state: State) -> dict:
    print("in greet")
    user_name = state["name"]
    return {"message": f"Hello, {user_name}!"}

builder = StateGraph(State)
builder.add_node("greet", greet)

# Entry point and termination
builder.set_entry_point("greet")
builder.add_edge("greet", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"name": "Alice", "message": ""})
    print("Final result:", result)
    
    
# Print an ASCII diagram directly in your console
graph.get_graph().print_ascii()
