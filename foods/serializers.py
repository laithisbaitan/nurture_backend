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
        # photo only enters through POST /api/foods/photo/ (step 1 of the photo
        # flow); source is writable so step 2 can flip photo_pending_ai -> manual,
        # but regular creates force source=manual in the view.
        # created_by is always taken from the requesting user, never the payload.
        read_only_fields = ["id", "photo", "created_by", "created_at", "updated_at"]


class FoodPhotoUploadSerializer(serializers.Serializer):
    """Step 1 of the two-step photo flow: just the image, nothing else."""

    photo = serializers.ImageField()


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
