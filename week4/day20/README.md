# Started LangGraph and learned what is LangGraph, what are State, Nodes and Edges.

## It is an Orchestration and Management Service or Framework that converts agentic system in a graphical form and show structured management system to manage tools

## LangGraph is an open-source framework created by LangChain designed to build robust, stateful, and multi-agent artificial intelligence (AI) workflows using graph-based structures.

## Core Concepts
- State: A shared data structure that acts as persistent memory, letting the workflow store and update information across various steps.
- Nodes: Individual units of computation or tasks, such as calling a large language model (LLM), running a function, or executing an external tool.
- Edges: Connections that define the path and decision-making logic or transitions between different nodes.
- Conditional Routing: Functions that inspect the current state to dynamically choose which node should execute next.

## Key Features
- Cyclic Workflows: Unlike traditional linear chains that move strictly from input to output, LangGraph allows loops, making it easy for agents to retry tasks, self-correct, or run feedback loops.
- Durable Execution & Persistence: Includes built-in checkpointers that automatically save state after every step, allowing agents to pause, wait for user input, or recover safely after server restarts.
- Human-in-the-Loop: Makes it simple to pause execution to ask a human for approval or edits before continuing the process.