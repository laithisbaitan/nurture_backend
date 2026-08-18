from datetime import datetime, timezone as dt_timezone

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from foods.models import FoodItem
from logs.models import FoodLog, WeightLog

DAILY_URL = "/api/progress/daily/"
WEEKLY_URL = "/api/progress/weekly/"
TREND_URL = "/api/progress/weight-trend/"


class ProgressTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "me@example.com", email="me@example.com", password="pw-not-relevant"
        )
        self.other = User.objects.create_user(
            "other@example.com", email="other@example.com", password="pw-not-relevant"
        )
        self.client.force_authenticate(self.user)

        self.chicken = FoodItem.objects.create(
            name_en="Chicken Breast",
            name_ar="صدر دجاج",
            serving_size=100,
            serving_unit="g",
            calories=165,
            protein_g=31,
            carbs_g=0,
            fat_g=3.6,
            micros_json={"iron_mg": 1.0, "potassium_mg": 256},
        )
        self.rice = FoodItem.objects.create(
            name_en="White Rice",
            name_ar="أرز أبيض",
            serving_size=100,
            serving_unit="g",
            calories=130,
            protein_g=2.7,
            carbs_g=28,
            fat_g=0.3,
            micros_json={"iron_mg": 0.2},
        )

    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(DAILY_URL).status_code, 401)
        self.assertEqual(self.client.get(WEEKLY_URL).status_code, 401)
        self.assertEqual(self.client.get(TREND_URL).status_code, 401)

    def test_daily_defaults_to_today_and_sums_macros_and_micros(self):
        now = timezone.now()
        FoodLog.objects.create(user=self.user, food_item=self.chicken, quantity=2, logged_at=now)
        FoodLog.objects.create(user=self.user, food_item=self.rice, quantity=1.5, logged_at=now)
        FoodLog.objects.create(user=self.other, food_item=self.chicken, quantity=10, logged_at=now)

        response = self.client.get(DAILY_URL)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["date"], timezone.localdate().isoformat())
        self.assertAlmostEqual(data["total_calories"], 525.0)
        self.assertAlmostEqual(data["total_protein_g"], 66.05)
        self.assertAlmostEqual(data["total_carbs_g"], 42.0)
        self.assertAlmostEqual(data["total_fat_g"], 7.65)
        self.assertAlmostEqual(data["micros_json"]["iron_mg"], 2.3)
        self.assertAlmostEqual(data["micros_json"]["potassium_mg"], 512.0)

    def test_daily_with_date_param_and_invalid_date(self):
        target = datetime(2026, 8, 17, 12, 0, tzinfo=dt_timezone.utc)
        FoodLog.objects.create(user=self.user, food_item=self.chicken, quantity=1, logged_at=target)

        response = self.client.get(DAILY_URL, {"date": "2026-08-17"})
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.data["total_calories"], 165.0)

        bad = self.client.get(DAILY_URL, {"date": "17-08-2026"})
        self.assertEqual(bad.status_code, 400)

    def test_weekly_returns_7_days_from_start(self):
        FoodLog.objects.create(
            user=self.user,
            food_item=self.chicken,
            quantity=1,
            logged_at=datetime(2026, 8, 18, 12, 0, tzinfo=dt_timezone.utc),
        )
        FoodLog.objects.create(
            user=self.user,
            food_item=self.rice,
            quantity=2,
            logged_at=datetime(2026, 8, 20, 12, 0, tzinfo=dt_timezone.utc),
        )

        response = self.client.get(WEEKLY_URL, {"start": "2026-08-18"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)
        self.assertEqual(response.data[0]["date"], "2026-08-18")
        self.assertEqual(response.data[6]["date"], "2026-08-24")
        self.assertAlmostEqual(response.data[0]["total_calories"], 165.0)
        self.assertAlmostEqual(response.data[2]["total_calories"], 260.0)
        self.assertAlmostEqual(response.data[1]["total_calories"], 0.0)

    def test_weekly_invalid_start_returns_400(self):
        response = self.client.get(WEEKLY_URL, {"start": "bad"})
        self.assertEqual(response.status_code, 400)

    def test_weight_trend_scoped_and_ordered(self):
        WeightLog.objects.create(user=self.user, date="2026-08-12", weight_kg=83.2)
        WeightLog.objects.create(user=self.user, date="2026-08-10", weight_kg=84.0)
        WeightLog.objects.create(user=self.other, date="2026-08-11", weight_kg=70.0)

        response = self.client.get(TREND_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"date": "2026-08-10", "weight_kg": 84.0},
                {"date": "2026-08-12", "weight_kg": 83.2},
            ],
        )
