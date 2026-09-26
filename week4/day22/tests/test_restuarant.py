import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import restuarant


def groq_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class RestaurantGraphTests(unittest.TestCase):
    def fake_groq(self, **kwargs):
        if kwargs.get("response_format"):
            return groq_response(
                json.dumps(
                    {
                        "is_food_order": True,
                        "dish_name": "chicken biryani",
                        "quantity": 2,
                    }
                )
            )
        return groq_response("I am a restaurant ordering agent. Please choose from the menu.")

    @patch.object(restuarant.groq_client.chat.completions, "create")
    @patch("builtins.input", return_value="yes")
    def test_order_completes(self, _input, create):
        create.side_effect = self.fake_groq

        result = restuarant.graph.invoke(
            restuarant.initial_state(
                "I want two chicken biryani",
                cook_outcomes=["success"],
                serve_outcomes=["success"],
            )
        )

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["final_result"], "success")
        self.assertEqual(result["cook_attempts"], 1)
        self.assertEqual(result["serve_attempts"], 1)

    @patch.object(restuarant.groq_client.chat.completions, "create")
    @patch("builtins.input", return_value="yes")
    def test_cook_exhaustion_apologizes(self, _input, create):
        create.side_effect = self.fake_groq

        result = restuarant.graph.invoke(
            restuarant.initial_state(
                "I want two chicken biryani",
                cook_outcomes=["failure", "failure"],
            )
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["final_result"], "failure")
        self.assertEqual(result["cook_attempts"], 2)
        self.assertEqual(result["cook_retry_attempts"], 0)

    @patch.object(restuarant.groq_client.chat.completions, "create")
    @patch("builtins.input", return_value="yes")
    def test_serve_exhaustion_apologizes(self, _input, create):
        create.side_effect = self.fake_groq

        result = restuarant.graph.invoke(
            restuarant.initial_state(
                "I want two chicken biryani",
                cook_outcomes=["success", "success"],
                serve_outcomes=["failure", "failure"],
            )
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["final_result"], "failure")
        self.assertEqual(result["serve_attempts"], 2)
        self.assertEqual(result["serve_retry_attempts"], 0)
        self.assertEqual(result["cook_retry_attempts"], 1)


if __name__ == "__main__":
    unittest.main()
