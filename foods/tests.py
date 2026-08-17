from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import FoodItem

FOODS_URL = "/api/foods/"
SEARCH_URL = "/api/foods/search/"

CHICKEN = {
    "name_en": "Chicken Breast",
    "name_ar": "صدر دجاج",
    "serving_size": 100,
    "serving_unit": "g",
    "calories": 165,
    "protein_g": 31,
    "carbs_g": 0,
    "fat_g": 3.6,
    "micros_json": {"potassium_mg": 256},
}

RICE = {
    "name_en": "White Rice (cooked)",
    "name_ar": "أرز أبيض",
    "serving_size": 100,
    "serving_unit": "g",
    "calories": 130,
    "protein_g": 2.7,
    "carbs_g": 28,
    "fat_g": 0.3,
}


class FoodItemTestCase(APITestCase):
    def setUp(self):
        response = self.client.post(
            "/api/auth/register/",
            {"email": "foodie@example.com", "password": "correct-horse-battery"},
        )
        self.user = User.objects.get(email="foodie@example.com")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")


class FoodItemCrudTests(FoodItemTestCase):
    def test_endpoints_require_auth(self):
        self.client.credentials()  # drop the token
        self.assertEqual(self.client.get(FOODS_URL).status_code, 401)
        self.assertEqual(self.client.post(FOODS_URL, CHICKEN, format="json").status_code, 401)
        self.assertEqual(self.client.get(SEARCH_URL, {"q": "x"}).status_code, 401)

    def test_create_sets_created_by_and_manual_source(self):
        response = self.client.post(FOODS_URL, CHICKEN, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["created_by"], self.user.id)
        self.assertEqual(response.data["source"], "manual")
        self.assertEqual(response.data["name_ar"], "صدر دجاج")
        self.assertEqual(response.data["micros_json"], {"potassium_mg": 256})

    def test_create_ignores_user_supplied_created_by_and_source(self):
        payload = {**CHICKEN, "created_by": 999, "source": "ai_processed"}
        response = self.client.post(FOODS_URL, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["created_by"], self.user.id)
        self.assertEqual(response.data["source"], "manual")

    def test_create_missing_required_field_fails(self):
        payload = {**CHICKEN}
        del payload["calories"]
        self.assertEqual(self.client.post(FOODS_URL, payload, format="json").status_code, 400)

    def test_list_is_paginated_and_global(self):
        self.client.post(FOODS_URL, CHICKEN, format="json")
        # A different user's item must still be visible (global DB).
        other = User.objects.create_user("other@example.com", password="pw12345678")
        FoodItem.objects.create(created_by=other, **{k: v for k, v in RICE.items()})
        response = self.client.get(FOODS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_and_patch(self):
        item_id = self.client.post(FOODS_URL, CHICKEN, format="json").data["id"]
        response = self.client.get(f"{FOODS_URL}{item_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name_en"], "Chicken Breast")
        response = self.client.patch(f"{FOODS_URL}{item_id}/", {"calories": 170}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["calories"], 170)

    def test_delete_not_allowed(self):
        item_id = self.client.post(FOODS_URL, CHICKEN, format="json").data["id"]
        self.assertEqual(self.client.delete(f"{FOODS_URL}{item_id}/").status_code, 405)


class FoodSearchTests(FoodItemTestCase):
    def setUp(self):
        super().setUp()
        self.client.post(FOODS_URL, CHICKEN, format="json")
        self.client.post(FOODS_URL, RICE, format="json")

    def test_search_english_case_insensitive(self):
        response = self.client.get(SEARCH_URL, {"q": "chicken"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name_en"], "Chicken Breast")

    def test_search_arabic(self):
        response = self.client.get(SEARCH_URL, {"q": "دجاج"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name_ar"], "صدر دجاج")

    def test_search_results_are_lightweight(self):
        result = self.client.get(SEARCH_URL, {"q": "rice"}).data[0]
        expected_keys = {
            "id", "name_en", "name_ar", "calories", "protein_g",
            "carbs_g", "fat_g", "serving_size", "serving_unit",
        }
        self.assertEqual(set(result.keys()), expected_keys)

    def test_search_no_match_and_empty_query(self):
        self.assertEqual(self.client.get(SEARCH_URL, {"q": "pizza"}).data, [])
        self.assertEqual(self.client.get(SEARCH_URL).data, [])
