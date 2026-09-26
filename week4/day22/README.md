# Restaurant LangGraph Agent

Run the agent from this directory:

```powershell
uv run python restuarant.py
```

The graph uses Mermaid, so no ASCII layout dependency is required. Open this file in VS Code and run **Markdown: Open Preview** to see the flow visually.

## LangGraph Flow

```mermaid
flowchart LR
  START((Start)):::terminal --> EXTRACT[Extract order with Groq]:::llm

  subgraph CHAT[Restaurant conversation]
    EXTRACT -->|question or unrelated| CHAT_REPLY[Answer in restaurant role]:::llm
    CHAT_REPLY --> FOLLOWUP[Ask for an order]:::llm
    FOLLOWUP --> EXTRACT
    REVIEW[Review complete cart]:::review
    RETRY_ORDER[Order retry available]:::retry
    ORDER_RETRY[Decrement order retry]:::retry
    NEW_ORDER[Collect new order]:::llm
  end

  subgraph ORDER[Order validation]
    CONFIRM[Check menu and inventory]:::process
    PARTIAL[Accept partial or reject]:::review
  end

  subgraph KITCHEN[Kitchen and delivery]
    COOK[Cook order]:::process
    COOK_RETRY[Consume cook retry]:::retry
    SERVE[Serve order]:::process
    SERVE_RETRY[Consume serve retry]:::retry
  end

  subgraph FINISH[Terminal states]
    COMPLETE((Order complete)):::success
    RECOVER[LLM explains failure]:::retry
    APOLOGY((Unable to complete)):::failure
    END((End)):::terminal
  end

  EXTRACT -->|valid order| REVIEW
  REVIEW -->|yes| CONFIRM
  REVIEW -->|no, retries left| ORDER_RETRY --> NEW_ORDER --> EXTRACT
  REVIEW -->|no retries left| APOLOGY
  CONFIRM -->|fully available| COOK
  CONFIRM -->|partial or unavailable| PARTIAL
  PARTIAL -->|accept partial| COOK
  PARTIAL -->|reject| ORDER_RETRY
  COOK -->|success| SERVE
  COOK -->|failure, retry left| COOK_RETRY --> COOK
  COOK -->|failure, no retries| RECOVER
  SERVE -->|success| COMPLETE --> END
  SERVE -->|failure, retries left| SERVE_RETRY --> COOK
  SERVE -->|failure, no retries| RECOVER
  RECOVER --> APOLOGY --> END

  classDef llm fill:#dbeafe,stroke:#2563eb,color:#172554,stroke-width:2px
  classDef review fill:#fef3c7,stroke:#d97706,color:#78350f,stroke-width:2px
  classDef process fill:#dcfce7,stroke:#16a34a,color:#14532d,stroke-width:2px
  classDef retry fill:#ffedd5,stroke:#ea580c,color:#7c2d12,stroke-width:2px
  classDef success fill:#bbf7d0,stroke:#15803d,color:#14532d,stroke-width:3px
  classDef failure fill:#fecaca,stroke:#dc2626,color:#7f1d1d,stroke-width:3px
  classDef terminal fill:#e5e7eb,stroke:#374151,color:#111827,stroke-width:2px
```

Diagram colors:

- Blue: Groq and restaurant conversation
- Yellow: order review and customer decisions
- Green: inventory, cooking, and serving
- Orange: retry paths
- Green endpoint: successful completion
- Red endpoint: failed order

The CLI also prints the same Mermaid source after each run. The execution log shows the node name, status, order details, and remaining retries.

## Testing

Run the deterministic automated tests from this directory:

```powershell
uv run python -m unittest discover -s tests -v
```

These tests mock Groq and verify:

- A successful order: `extract_order -> order_confirm -> cook -> serve -> END`
- Cook failure twice, followed by recovery and apology
- Serve failure twice, including cook retries, followed by recovery and apology

Run the real interactive workflow with the Groq API:

```powershell
uv run python restuarant.py
```

Try inputs such as:

```text
I am hungry, what is on the menu?
I want 2 chicken biryani
Can you debug my Python code?
```

The last request should be refused because the assistant is restricted to restaurant ordering. The `.env` file must contain a valid `GROQ_API_KEY` for this live test.

The automated tests use `cook_outcomes` and `serve_outcomes` so failures are reproducible. For example:

```python
initial_state(
  "I want 2 chicken biryani",
  cook_outcomes=["failure", "success"],
  serve_outcomes=["failure", "success"],
)
```

Use the printed `NODE`, `STATUS`, `cook_retries`, `serve_retries`, `cook_attempt`, and `serve_attempt` values to inspect each state transition.
