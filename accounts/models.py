from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Sex(models.TextChoices):
        MALE = "male"
        FEMALE = "female"
        OTHER = "other"

    class ActivityLevel(models.TextChoices):
        SEDENTARY = "sedentary"
        LIGHT = "light"
        MODERATE = "moderate"
        ACTIVE = "active"
        VERY_ACTIVE = "very_active"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=Sex.choices, null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    # Baseline weight only; weight history lives in logs.WeightLog (Stage 4).
    weight_kg = models.FloatField(null=True, blank=True)
    activity_level = models.CharField(
        max_length=20, choices=ActivityLevel.choices, null=True, blank=True
    )
    goal = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
