from django.contrib import admin

from .models import FoodItem


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        "name_en",
        "name_ar",
        "serving_size",
        "serving_unit",
        "calories",
        "protein_g",
        "carbs_g",
        "fat_g",
        "source",
        "created_by",
        "updated_at",
    )
    search_fields = ("name_en", "name_ar")
    list_filter = ("source", "serving_unit")
