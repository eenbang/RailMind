import unittest

from app.adapters.intent_parser import RuleBasedIntentParser


class RuleBasedIntentParserTest(unittest.TestCase):
    def test_extracts_common_trip_conditions(self) -> None:
        draft, clarifications = RuleBasedIntentParser().parse(
            "从上海到杭州，上午出发，预算 100 元"
        )

        self.assertEqual(draft.origin, "上海")
        self.assertEqual(draft.destination, "杭州")
        self.assertEqual(draft.max_price, 100)
        self.assertIsNotNone(draft.departure_window)
        self.assertEqual(draft.missing_fields, ())
        self.assertEqual(clarifications, ())

    def test_keeps_missing_route_explicit(self) -> None:
        draft, _ = RuleBasedIntentParser().parse("想坐早上的高铁")

        self.assertEqual(draft.missing_fields, ("origin", "destination"))


if __name__ == "__main__":
    unittest.main()
