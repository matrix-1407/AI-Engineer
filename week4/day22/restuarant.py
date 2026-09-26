import json
import os
import random
from pathlib import Path
from typing import Annotated, NotRequired, TypedDict

from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from menu import MENU, MENU_ITEMS


load_dotenv(Path(__file__).with_name(".env"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = "openai/gpt-oss-20b"
RESTAURANT_SYSTEM_PROMPT = f"""
You are the conversational assistant for one restaurant ordering system.

Your responsibilities are limited to this restaurant:
- Explain the menu, categories, prices, and availability.
- Help the user choose a dish.
- Ask for a dish name and a positive quantity when the user wants to order.
- Be concise, polite, and clear.

The current menu is:
{json.dumps(MENU, indent=2)}

You must not answer questions about Python, programming, debugging, mathematics,
general knowledge, medical topics, or any other unrelated subject. For unrelated
requests, say exactly that you are a restaurant food-ordering agent and redirect
the user to the menu or placing an order. Never pretend to be a general-purpose
assistant and never invent dishes, prices, or inventory.
"""


class State(TypedDict):
	messages: Annotated[list, add_messages]
	user_input: str
	dish_name: str
	required_quantity: int
	available_quantity: str
	status: str
	order_retry_attempts: int
	cook_retry_attempts: int
	serve_retry_attempts: int
	final_result: str
	order_items: NotRequired[list[dict[str, int | str]]]
	available_items: NotRequired[list[dict[str, int | str]]]
	order_confirmed: NotRequired[bool]
	# Optional outcome lists make later simulations deterministic.
	cook_outcomes: NotRequired[list[str]]
	serve_outcomes: NotRequired[list[str]]
	cook_attempts: NotRequired[int]
	serve_attempts: NotRequired[int]


def add_message(state: State, message: str) -> dict:
	return {"messages": [{"role": "assistant", "content": message}]}


def order_text(items: list[dict[str, int | str]]) -> str:
	return ", ".join(
		f"{item['quantity']} x {item['dish_name']}"
		for item in items
	)


def extract_order(state: State) -> dict:
	"""Use Groq to classify the request and extract one or more line items."""
	response = groq_client.chat.completions.create(
		model=GROQ_MODEL,
		temperature=0,
		response_format={"type": "json_object"},
		messages=[
			{
				"role": "system",
				"content": (
					"You extract restaurant orders. The only valid dishes are: "
					f"{MENU_ITEMS}. Return JSON only with keys "
					"is_food_order (boolean) and items (array). Each item must have "
					"dish_name (string) and quantity (positive integer). "
					"Extract every dish mentioned, including multiple dishes in one request. "
					"Correct obvious spelling mistakes to the closest menu dish, for example "
					"'chciken burger' means 'chicken burger'. Never silently drop a requested "
					"dish. Use an empty items array when the request is unrelated or contains "
					"no clear dish and quantity."
				),
			},
			{"role": "user", "content": state["user_input"]},
		],
	)
	order = json.loads(response.choices[0].message.content or "{}")
	items = []
	for item in order.get("items", []):
		dish = str(item.get("dish_name", "")).lower().strip()
		quantity = item.get("quantity", 0)
		if dish in MENU and isinstance(quantity, int) and quantity > 0:
			items.append({"dish_name": dish, "quantity": quantity})

	# Keep compatibility with the original single-item JSON contract.
	if not items and order.get("dish_name"):
		dish = str(order["dish_name"]).lower().strip()
		quantity = order.get("quantity", 0)
		if dish in MENU and isinstance(quantity, int) and quantity > 0:
			items.append({"dish_name": dish, "quantity": quantity})

	valid_order = order.get("is_food_order") is True and bool(items)

	if not valid_order:
		return {
			"dish_name": "",
			"required_quantity": 0,
			"status": "unrelated",
		}

	first_item = items[0]
	return {
		"dish_name": first_item["dish_name"],
		"required_quantity": int(first_item["quantity"]),
		"order_items": items,
		"order_confirmed": False,
		"status": "order_received",
		**add_message(state, f"I received: {order_text(items)}."),
	}


def order_review(state: State) -> dict:
	"""Show the complete cart and obtain an explicit customer confirmation."""
	items = state.get("order_items", [])
	print("\nOrder review")
	for item in items:
		menu_item = MENU[item["dish_name"]]
		price = int(menu_item["price"])
		print(
			f"  {item['quantity']} x {item['dish_name']} "
			f"(Rs. {price} each, Rs. {price * int(item['quantity'])} total)"
		)
	answer = input("Confirm this order? (yes/no)\n> ").strip().lower()
	if answer in {"yes", "y", "confirm", "confirmed"}:
		return {"order_confirmed": True, "status": "order_confirmed"}
	return {
		"order_confirmed": False,
		"status": "new_order",
		**add_message(state, "Order cancelled. Please enter a different order."),
	}


def order_confirm(state: State) -> dict:
	items = state.get("order_items", [])
	available_items = []
	for item in items:
		menu_item = MENU[item["dish_name"]]
		available = int(menu_item["quantity"])
		available_items.append({**item, "available_quantity": available})

	if any(int(item["available_quantity"]) == 0 for item in available_items):
		status = "unavailable"
	elif any(int(item["available_quantity"]) < int(item["quantity"])
			 for item in available_items):
		status = "partial"
	else:
		status = "confirmed"

	availability = ", ".join(
		f"{item['dish_name']}: {item['available_quantity']} available"
		for item in available_items
	)

	return {
		"available_items": available_items,
		"available_quantity": availability,
		"status": status,
		**add_message(state, f"Availability: {availability}. Order status: {status}."),
	}


def partial_order_decision(state: State) -> dict:
	if state["status"] == "partial":
		message = (
			f"The requested quantities are partially available: {state['available_quantity']}. "
			"Type 'yes' to accept the partial order or 'no' to order again."
		)
		answer = input(f"{message}\n> ").strip().lower()
		if answer in {"yes", "y"}:
			available_items = [
				{
					"dish_name": item["dish_name"],
					"quantity": min(int(item["quantity"]), int(item["available_quantity"])),
				}
				for item in state.get("available_items", [])
				if int(item["available_quantity"]) > 0
			]
			return {
				"order_items": available_items,
				"dish_name": available_items[0]["dish_name"] if available_items else "",
				"required_quantity": available_items[0]["quantity"] if available_items else 0,
				"status": "confirmed" if available_items else "unavailable",
			}

	return {
		"status": "new_order",
		**add_message(state, "Please enter a new food order."),
	}


def get_new_order(state: State) -> dict:
	return {"user_input": input("New order\n> ").strip()}


def respond_to_user(state: State) -> dict:
	"""Answer restaurant questions and refuse unrelated requests in-role."""
	response = groq_client.chat.completions.create(
		model=GROQ_MODEL,
		temperature=0.2,
		messages=[
			{"role": "system", "content": RESTAURANT_SYSTEM_PROMPT},
			{"role": "user", "content": state["user_input"]},
		],
	)
	answer = response.choices[0].message.content or "Please ask about our menu or place an order."
	print(f"Assistant: {answer}")
	return {"status": "conversation", **add_message(state, answer)}


def get_followup(state: State) -> dict:
	return {"user_input": input("What would you like to order?\n> ").strip()}


def cook(state: State) -> dict:
	outcomes = list(state.get("cook_outcomes", []))
	attempt = state.get("cook_attempts", 0) + 1
	outcome = outcomes.pop(0) if outcomes else ("success" if random.random() >= 0.4 else "failure")
	if outcome == "success":
		return {
			"status": "ready",
			"cook_attempts": attempt,
			"cook_outcomes": outcomes,
			**add_message(state, "Your order is cooked and ready to serve."),
		}

	remaining = max(0, state["cook_retry_attempts"] - 1)
	return {
		"status": "cook_failed",
		"cook_attempts": attempt,
		"cook_retry_attempts": remaining,
		"cook_outcomes": outcomes,
		**add_message(state, f"Cooking failed. Cook retries remaining: {remaining}."),
	}


def serve(state: State) -> dict:
	outcomes = list(state.get("serve_outcomes", []))
	attempt = state.get("serve_attempts", 0) + 1
	outcome = outcomes.pop(0) if outcomes else ("success" if random.random() >= 0.4 else "failure")
	if outcome == "success":
		return {
			"status": "complete",
			"final_result": "success",
			"serve_attempts": attempt,
			"serve_outcomes": outcomes,
			**add_message(state, "Your order is complete. Enjoy your meal!"),
		}

	remaining = max(0, state["serve_retry_attempts"] - 1)
	return {
		"status": "serve_failed",
		"serve_attempts": attempt,
		"serve_retry_attempts": remaining,
		"serve_outcomes": outcomes,
		**add_message(state, f"Serving failed. Serve retries remaining: {remaining}."),
	}


def apology(state: State) -> dict:
	message = (
		"We are sorry, but we were unable to complete your order within the "
		"allowed attempts. Please try again later."
	)
	return {
		"status": "failed",
		"final_result": "failure",
		**add_message(state, message),
	}


def retry_order_after_failure(state: State) -> dict:
	"""Let the restaurant assistant ask for a different order after exhaustion."""
	response = groq_client.chat.completions.create(
		model=GROQ_MODEL,
		temperature=0.2,
		messages=[
			{"role": "system", "content": RESTAURANT_SYSTEM_PROMPT},
			{
				"role": "user",
				"content": (
					"The restaurant could not complete the current order within its "
					"allowed attempts. Ask the customer whether they want to try a different order."
				),
			},
		],
	)
	answer = response.choices[0].message.content or (
		"I am sorry, but I could not complete that order. "
		"Would you like to try something different?"
	)
	print(f"LLM: {answer}")
	return {"status": "retry_requested", **add_message(state, answer)}


def route_after_extraction(state: State) -> str:
	return "order_review" if state["status"] == "order_received" else "respond_to_user"


def route_after_review(state: State) -> str:
	if state.get("order_confirmed"):
		return "order_confirm"
	if state["order_retry_attempts"] > 0:
		return "decrement_order_retry"
	return "apology"


def route_after_confirmation(state: State) -> str:
	return "cook" if state["status"] == "confirmed" else "partial_order_decision"


def route_after_decision(state: State) -> str:
	return "cook" if state["status"] == "confirmed" else "new_order"


def route_after_cook(state: State) -> str:
	if state["status"] == "ready":
		return "serve"
	return "cook" if state.get("cook_attempts", 0) < 2 else "retry_order_after_failure"


def route_after_serve(state: State) -> str:
	if state["status"] == "complete":
		return "end"
	if state.get("serve_attempts", 0) >= 2 or state.get("cook_attempts", 0) >= 2:
		return "retry_order_after_failure"
	return "prepare_cook_retry"


def prepare_cook_retry(state: State) -> dict:
	remaining = max(0, state["cook_retry_attempts"] - 1)
	return {
		"cook_retry_attempts": remaining,
		"status": "cook_retry_requested",
		**add_message(state, f"Serve failed. Returning to cook; cook retries remaining: {remaining}."),
	}


def route_after_new_order(state: State) -> str:
	return "extract_order" if state["order_retry_attempts"] > 0 else "apology"


def decrement_order_retry(state: State) -> dict:
	return {"order_retry_attempts": max(0, state["order_retry_attempts"] - 1)}


builder = StateGraph(State)
builder.add_node("extract_order", extract_order)
builder.add_node("order_review", order_review)
builder.add_node("order_confirm", order_confirm)
builder.add_node("partial_order_decision", partial_order_decision)
builder.add_node("new_order", get_new_order)
builder.add_node("respond_to_user", respond_to_user)
builder.add_node("get_followup", get_followup)
builder.add_node("decrement_order_retry", decrement_order_retry)
builder.add_node("cook", cook)
builder.add_node("serve", serve)
builder.add_node("apology", apology)
builder.add_node("retry_order_after_failure", retry_order_after_failure)
builder.add_node("prepare_cook_retry", prepare_cook_retry)

builder.set_entry_point("extract_order")
builder.add_conditional_edges(
	"extract_order",
	route_after_extraction,
	{"order_review": "order_review", "respond_to_user": "respond_to_user"},
)
builder.add_conditional_edges(
	"order_review",
	route_after_review,
	{"order_confirm": "order_confirm", "decrement_order_retry": "decrement_order_retry"},
)
builder.add_edge("respond_to_user", "get_followup")
builder.add_edge("get_followup", "extract_order")
builder.add_conditional_edges(
	"order_confirm",
	route_after_confirmation,
	{"cook": "cook", "partial_order_decision": "partial_order_decision"},
)
builder.add_conditional_edges(
	"partial_order_decision",
	route_after_decision,
	{"cook": "cook", "new_order": "decrement_order_retry"},
)
builder.add_edge("decrement_order_retry", "new_order")
builder.add_conditional_edges(
	"new_order",
	route_after_new_order,
	{"extract_order": "extract_order", "apology": "apology"},
)
builder.add_conditional_edges(
	"cook",
	route_after_cook,
	{"cook": "cook", "serve": "serve", "retry_order_after_failure": "retry_order_after_failure"},
)
builder.add_conditional_edges(
	"serve",
	route_after_serve,
	{
		"prepare_cook_retry": "prepare_cook_retry",
		"end": END,
		"retry_order_after_failure": "retry_order_after_failure",
	},
)
builder.add_edge("prepare_cook_retry", "cook")
builder.add_edge("retry_order_after_failure", "apology")
builder.add_edge("apology", END)

graph = builder.compile()


def initial_state(user_input: str, **outcomes: list[str]) -> State:
	return {
		"messages": [],
		"user_input": user_input,
		"dish_name": "",
		"required_quantity": 0,
		"available_quantity": "0",
		"status": "",
		# Two retries are available after the initial order: three total orders.
		"order_retry_attempts": 2,
		"cook_retry_attempts": 2,
		"serve_retry_attempts": 2,
		"final_result": "",
		"order_items": [],
		"available_items": [],
		"order_confirmed": False,
		"cook_attempts": 0,
		"serve_attempts": 0,
		**outcomes,
	}


if __name__ == "__main__":
	user_input = input("What would you like to order?\n> ").strip()
	print("\nOrder processing started\n")
	result = dict(initial_state(user_input))
	visited_nodes = []
	for update in graph.stream(result, stream_mode="updates"):
		for node_name, node_update in update.items():
			result.update(node_update)
			visited_nodes.append(node_name)
			print(f"  {len(visited_nodes):>2}. {node_name:<28} {result.get('status', '')}")

	print("\n" + "=" * 56)
	if result["final_result"] == "success":
		print("ORDER COMPLETE")
		print("Your order has been cooked, served, and completed.")
		for item in result.get("order_items", []):
			print(f"  {item['quantity']} x {item['dish_name']}")
	else:
		print("ORDER NOT COMPLETED")
		print("The order was not sent to the kitchen.")
		print("Please place a new order if you would like to try again.")
	print("=" * 56)
	print(
				f"Attempts used: cook {result.get('cook_attempts', 0)}/2, "
				f"serve {result.get('serve_attempts', 0)}/2"
	)
	print(
		f"Retries remaining: order {result.get('order_retry_attempts', 0)}, "
		f"cook {result.get('cook_retry_attempts', 0)}, "
		f"serve {result.get('serve_retry_attempts', 0)}"
	)
