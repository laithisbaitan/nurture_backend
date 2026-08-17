from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from foods.models import FoodItem

from .models import FoodLog, WeightLog

LOGS_URL = "/api/logs/"
WEIGHT_URL = "/api/weight/"


def create_food(**overrides):
    defaults = {
        "name_en": "Chicken Breast",
        "name_ar": "صدر دجاج",
        "serving_size": 100,
        "serving_unit": "g",
        "calories": 165,
        "protein_g": 31,
        "carbs_g": 0,
        "fat_g": 3.6,
    }
    defaults.update(overrides)
    return FoodItem.objects.create(**defaults)


class LogsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "me@example.com", email="me@example.com", password="pw-not-relevant"
        )
        self.other = User.objects.create_user(
            "other@example.com", email="other@example.com", password="pw-not-relevant"
        )
        self.food = create_food()
        self.client.force_authenticate(self.user)


class FoodLogTests(LogsTestCase):
    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(LOGS_URL).status_code, 401)
        self.assertEqual(
            self.client.post(LOGS_URL, {"food_item": self.food.id, "quantity": 1}).status_code,
            401,
        )

    def test_create_log_for_requesting_user(self):
        response = self.client.post(
            LOGS_URL,
            {"food_item": self.food.id, "quantity": 1.5, "meal_type": "lunch"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["quantity"], 1.5)
        self.assertEqual(response.data["food_name_en"], "Chicken Breast")
        log = FoodLog.objects.get(id=response.data["id"])
        self.assertEqual(log.user, self.user)

    def test_create_rejects_non_positive_quantity(self):
        response = self.client.post(
            LOGS_URL, {"food_item": self.food.id, "quantity": 0}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_list_defaults_to_today_and_filters_by_date(self):
        yesterday = timezone.now() - timedelta(days=1)
        FoodLog.objects.create(user=self.user, food_item=self.food, quantity=1)
        FoodLog.objects.create(
            user=self.user, food_item=self.food, quantity=2, logged_at=yesterday
        )
        today_response = self.client.get(LOGS_URL)
        self.assertEqual(today_response.status_code, 200)
        self.assertEqual(len(today_response.data), 1)
        self.assertEqual(today_response.data[0]["quantity"], 1.0)

        date_str = yesterday.date().isoformat()
        yesterday_response = self.client.get(LOGS_URL, {"date": date_str})
        self.assertEqual(len(yesterday_response.data), 1)
        self.assertEqual(yesterday_response.data[0]["quantity"], 2.0)

    def test_list_invalid_date_returns_400(self):
        self.assertEqual(self.client.get(LOGS_URL, {"date": "not-a-date"}).status_code, 400)

    def test_users_only_see_their_own_logs(self):
        FoodLog.objects.create(user=self.user, food_item=self.food, quantity=1)
        FoodLog.objects.create(user=self.other, food_item=self.food, quantity=9)
        response = self.client.get(LOGS_URL)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["quantity"], 1.0)

    def test_delete_own_log(self):
        log = FoodLog.objects.create(user=self.user, food_item=self.food, quantity=1)
        response = self.client.delete(f"{LOGS_URL}{log.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(FoodLog.objects.filter(id=log.id).exists())

    def test_cannot_delete_other_users_log(self):
        log = FoodLog.objects.create(user=self.other, food_item=self.food, quantity=1)
        response = self.client.delete(f"{LOGS_URL}{log.id}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(FoodLog.objects.filter(id=log.id).exists())


class WeightLogTests(LogsTestCase):
    def test_requires_auth(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(WEIGHT_URL).status_code, 401)

    def test_create_weight_log_for_requesting_user(self):
        response = self.client.post(
            WEIGHT_URL, {"date": "2026-08-17", "weight_kg": 82.5}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(WeightLog.objects.get(id=response.data["id"]).user, self.user)

    def test_list_ordered_by_date_and_scoped(self):
        WeightLog.objects.create(user=self.user, date="2026-08-15", weight_kg=83.0)
        WeightLog.objects.create(user=self.user, date="2026-08-10", weight_kg=84.0)
        WeightLog.objects.create(user=self.other, date="2026-08-12", weight_kg=70.0)
        response = self.client.get(WEIGHT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            [entry["date"] for entry in response.data], ["2026-08-10", "2026-08-15"]
        )
