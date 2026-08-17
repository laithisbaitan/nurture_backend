from django.conf import settings
from django.db import models


class FoodItem(models.Model):
    class Source(models.TextChoices):
        # Only MANUAL is used in Stage 2; the others exist so the photo/AI
        # stages need no schema migration.
        MANUAL = "manual"
        PHOTO_PENDING_AI = "photo_pending_ai"
        AI_PROCESSED = "ai_processed"

    name_en = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    photo = models.ImageField(upload_to="food_photos/", null=True, blank=True)
    serving_size = models.FloatField()
    serving_unit = models.CharField(max_length=20)  # e.g. "g", "ml", "piece"
    calories = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()
    fiber_g = models.FloatField(null=True, blank=True)
    sugar_g = models.FloatField(null=True, blank=True)
    sodium_mg = models.FloatField(null=True, blank=True)
    # Flexible key-value store for extra micronutrients (no migration needed
    # to add a new one), e.g. {"vitamin_c_mg": 12.0, "iron_mg": 1.5}.
    micros_json = models.JSONField(default=dict, blank=True)
    source = models.CharField(
        max_length=20, choices=Source.choices, default=Source.MANUAL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="food_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name_en} ({self.name_ar})"
