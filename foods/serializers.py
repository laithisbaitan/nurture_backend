from rest_framework import serializers

from .models import FoodItem


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            "id",
            "name_en",
            "name_ar",
            "photo",
            "serving_size",
            "serving_unit",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "fiber_g",
            "sugar_g",
            "sodium_mg",
            "micros_json",
            "source",
            "created_by",
            "created_at",
            "updated_at",
        ]
        # photo becomes writable in Stage 3 (two-step photo flow);
        # created_by is always taken from the requesting user, never the payload.
        read_only_fields = ["id", "photo", "source", "created_by", "created_at", "updated_at"]


class FoodItemSearchSerializer(serializers.ModelSerializer):
    """Lightweight shape for the Flutter search screen."""

    class Meta:
        model = FoodItem
        fields = [
            "id",
            "name_en",
            "name_ar",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "serving_size",
            "serving_unit",
        ]
