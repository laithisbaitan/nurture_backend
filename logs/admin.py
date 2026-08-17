from django.contrib import admin

from .models import FoodLog, WeightLog


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ("user", "food_item", "quantity", "meal_type", "logged_at")
    list_filter = ("meal_type",)
    search_fields = ("user__email", "food_item__name_en", "food_item__name_ar")
    date_hierarchy = "logged_at"


@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "weight_kg", "created_at")
    search_fields = ("user__email",)
    date_hierarchy = "date"
