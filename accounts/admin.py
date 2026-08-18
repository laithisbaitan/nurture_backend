from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "age",
        "sex",
        "height_cm",
        "weight_kg",
        "activity_level",
        "goal",
        "updated_at",
    )
    search_fields = ("user__username", "user__email", "user__first_name")
    list_filter = ("sex", "activity_level")
