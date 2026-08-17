from django.contrib.auth.models import User
from rest_framework.test import APITestCase

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
REFRESH_URL = "/api/auth/refresh/"
ME_URL = "/api/auth/me/"

EMAIL = "test@example.com"
PASSWORD = "correct-horse-battery"


class AuthTests(APITestCase):
    def register(self, email=EMAIL, password=PASSWORD, name="Test User"):
        return self.client.post(
            REGISTER_URL, {"email": email, "password": password, "name": name}
        )

    def test_register_creates_user_and_profile_and_returns_tokens(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["email"], EMAIL)
        user = User.objects.get(email=EMAIL)
        self.assertTrue(hasattr(user, "profile"))

    def test_register_duplicate_email_fails(self):
        self.register()
        response = self.register()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(email=EMAIL).count(), 1)

    def test_register_weak_password_fails(self):
        response = self.register(password="123")
        self.assertEqual(response.status_code, 400)

    def test_login_with_email_returns_tokens(self):
        self.register()
        response = self.client.post(LOGIN_URL, {"email": EMAIL, "password": PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password_fails(self):
        self.register()
        response = self.client.post(LOGIN_URL, {"email": EMAIL, "password": "wrong"})
        self.assertEqual(response.status_code, 401)

    def test_refresh_returns_new_access_token(self):
        refresh_token = self.register().data["refresh"]
        response = self.client.post(REFRESH_URL, {"refresh": refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)


class MeEndpointTests(APITestCase):
    def setUp(self):
        response = self.client.post(
            REGISTER_URL, {"email": EMAIL, "password": PASSWORD, "name": "Test User"}
        )
        self.access_token = response.data["access"]

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get(ME_URL).status_code, 401)
        self.assertEqual(self.client.patch(ME_URL, {"age": 30}).status_code, 401)

    def test_get_me_returns_flat_profile(self):
        self.authenticate()
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], EMAIL)
        self.assertEqual(response.data["name"], "Test User")
        self.assertIsNone(response.data["age"])

    def test_patch_me_updates_profile_fields(self):
        self.authenticate()
        response = self.client.patch(
            ME_URL,
            {
                "age": 30,
                "sex": "male",
                "height_cm": 180.0,
                "weight_kg": 80.5,
                "activity_level": "moderate",
                "goal": "lose weight",
                "name": "Laith",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["age"], 30)
        self.assertEqual(response.data["weight_kg"], 80.5)
        self.assertEqual(response.data["name"], "Laith")
        user = User.objects.get(email=EMAIL)
        self.assertEqual(user.profile.goal, "lose weight")
        self.assertEqual(user.first_name, "Laith")

    def test_patch_me_rejects_invalid_choice(self):
        self.authenticate()
        response = self.client.patch(ME_URL, {"sex": "invalid"})
        self.assertEqual(response.status_code, 400)
