import unittest
from datetime import time

from app.adapters.journey_repository import default_repository
from app.domain.recommendation import RecommendationEngine
from app.domain.models import TimeWindow, TravelRequest


class RecommendationEngineTest(unittest.TestCase):
    def test_filter_and_rank_shanghai_to_hangzhou(self) -> None:
        request = TravelRequest(
            origin="上海",
            destination="杭州",
            departure_window=TimeWindow(time(8), time(12)),
            max_price=100,
            max_duration_minutes=120,
        )
        result = RecommendationEngine().recommend(
            default_repository().all(), request, limit=3
        )

        self.assertGreater(result.filtered_count, 0)
        self.assertEqual(len(result.recommendations), 3)
        self.assertTrue(
            all(
                item.journey.departure_time >= time(8)
                and item.journey.departure_time <= time(12)
                for item in result.recommendations
            )
        )
        self.assertTrue(
            all(item.reasons for item in result.recommendations)
        )

    def test_empty_result_keeps_route_and_can_suggest_relaxation(self) -> None:
        request = TravelRequest(
            origin="上海",
            destination="杭州",
            max_price=1,
        )
        result = RecommendationEngine().recommend(
            default_repository().all(), request
        )

        self.assertEqual(result.recommendations, ())
        self.assertEqual(result.candidate_count, 380)
        self.assertEqual(result.filtered_count, 0)
        self.assertTrue(result.relaxation_suggestions)


if __name__ == "__main__":
    unittest.main()
