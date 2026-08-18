from django.conf import settings
from django.db import models
from django.utils import timezone


class FoodLog(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = "breakfast"
        LUNCH = "lunch"
        DINNER = "dinner"
        SNACK = "snack"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_logs"
    )
    food_item = models.ForeignKey(
        "foods.FoodItem", on_delete=models.PROTECT, related_name="logs"
    )
    quantity = models.FloatField()  # number of servings, can be fractional
    meal_type = models.CharField(
        max_length=10, choices=MealType.choices, null=True, blank=True
    )
    # default=now but editable, so users can log retroactively
    logged_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.quantity} x {self.food_item.name_en}"


class WeightLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="weight_logs"
    )
    date = models.DateField()
    weight_kg = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.weight_kg} kg on {self.date}"
