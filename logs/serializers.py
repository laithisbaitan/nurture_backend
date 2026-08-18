from rest_framework import serializers

from .models import FoodLog, WeightLog


class FoodLogSerializer(serializers.ModelSerializer):
    # Flat read-only convenience fields so the Flutter log screen doesn't need
    # a second request per row to display names/calories.
    food_name_en = serializers.CharField(source="food_item.name_en", read_only=True)
    food_name_ar = serializers.CharField(source="food_item.name_ar", read_only=True)
    food_calories = serializers.FloatField(source="food_item.calories", read_only=True)
    food_serving_size = serializers.FloatField(source="food_item.serving_size", read_only=True)
    food_serving_unit = serializers.CharField(source="food_item.serving_unit", read_only=True)

    class Meta:
        model = FoodLog
        fields = [
            "id",
            "food_item",
            "quantity",
            "meal_type",
            "logged_at",
            "created_at",
            "food_name_en",
            "food_name_ar",
            "food_calories",
            "food_serving_size",
            "food_serving_unit",
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {"quantity": {"min_value": 0.01}}


class WeightLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightLog
        fields = ["id", "date", "weight_kg", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {"weight_kg": {"min_value": 0.1}}
