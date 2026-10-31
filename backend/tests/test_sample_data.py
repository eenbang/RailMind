import unittest

from app.adapters.journey_repository import default_repository


class SampleDataTest(unittest.TestCase):
    def test_sample_data_contains_all_journeys(self) -> None:
        journeys = default_repository().all()
        self.assertEqual(len(journeys), 380)
        self.assertEqual(journeys[0].train_no, "Z175")
        self.assertEqual(journeys[-1].train_no, "G7309")


if __name__ == "__main__":
    unittest.main()
