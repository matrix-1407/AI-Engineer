from typing import TypedDict
from langgraph.graph import END, StateGraph

class State(TypedDict):
    number: int

def add_ten(state: State) -> dict:
    current = state["number"]
    new_num = current + 10
    print(f"in add_ten: {current} + 10 = {new_num}")
    return {"number": new_num}

def multiply_two(state: State) -> dict:
    current = state["number"]
    new_num = current * 2
    print(f"in multiply_two: {current} * 2 = {new_num}")
    return {"number": new_num}

builder = StateGraph(State)
builder.add_node("add_ten", add_ten)
builder.add_node("multiply_two", multiply_two)

# Flow: START -> add_ten -> multiply_two -> END
builder.set_entry_point("add_ten")
builder.add_edge("add_ten", "multiply_two")
builder.add_edge("multiply_two", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"number": 5})
    print("Final result:", result)
    
    
# Print an ASCII diagram directly in your console
graph.get_graph().print_ascii()