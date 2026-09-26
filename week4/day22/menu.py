"""Restaurant menu, pricing, categories, and current inventory."""

MENU: dict[str, dict[str, str | int]] = {
    "paneer butter masala": {
        "category": "main course",
        "price": 300,
        "quantity": 10,
    },
    "chicken biryani": {
        "category": "main course",
        "price": 350,
        "quantity": 8,
    },
    "veg biryani": {
        "category": "main course",
        "price": 280,
        "quantity": 12,
    },
    "chicken burger": {
        "category": "fast food",
        "price": 450,
        "quantity": 20,
    },
    "veg burger": {
        "category": "fast food",
        "price": 300,
        "quantity": 15,
    },
    "masala dosa": {
        "category": "south indian",
        "price": 180,
        "quantity": 10,
    },
    "butter naan": {
        "category": "bread",
        "price": 60,
        "quantity": 25,
    },
    "chicken tikka": {
        "category": "starter",
        "price": 320,
        "quantity": 6,
    },
    "paneer tikka": {
        "category": "starter",
        "price": 280,
        "quantity": 7,
    },
    "french fries": {
        "category": "side",
        "price": 150,
        "quantity": 20,
    },
    "cold coffee": {
        "category": "beverage",
        "price": 140,
        "quantity": 15,
    },
    "mango lassi": {
        "category": "beverage",
        "price": 120,
        "quantity": 10,
    },
    "gulab jamun": {
        "category": "dessert",
        "price": 100,
        "quantity": 8,
    },
    "chocolate brownie": {
        "category": "dessert",
        "price": 180,
        "quantity": 5,
    },
}

MENU_ITEMS = ", ".join(MENU)

