from typing import TypedDict
from langgraph.graph import END, StateGraph

class State(TypedDict):
    raw_text: str
    cleaned_text: str
    word_count: int

def clean_text(state: State) -> dict:
    print("in clean_text")
    cleaned = state["raw_text"].strip().lower()
    return {"cleaned_text": cleaned}

def count_words(state: State) -> dict:
    print("in count_words")
    words = state["cleaned_text"].split()
    return {"word_count": len(words)}

builder = StateGraph(State)
builder.add_node("clean_text", clean_text)
builder.add_node("count_words", count_words)

# Entry point
builder.set_entry_point("clean_text")

# Linear edge from clean_text -> count_words -> END
builder.add_edge("clean_text", "count_words")
builder.add_edge("count_words", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({
        "raw_text": "   Hello LangGraph World!   ",
        "cleaned_text": "",
        "word_count": 0
    })
    print("Final Result:", result)
    
    
# Print an ASCII diagram directly in your console
graph.get_graph().print_ascii()
