from datetime import date as date_cls

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import FoodLog, WeightLog
from .serializers import FoodLogSerializer, WeightLogSerializer


def parse_date_param(value):
    try:
        return date_cls.fromisoformat(value)
    except ValueError:
        raise ValidationError({"date": "Invalid date, expected YYYY-MM-DD."})


class FoodLogViewSet(viewsets.ModelViewSet):
    """A user's food diary. Queryset is always scoped to request.user."""

    serializer_class = FoodLogSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        queryset = FoodLog.objects.filter(user=self.request.user).select_related(
            "food_item"
        )
        if self.action == "list":
            date_str = self.request.query_params.get("date")
            target = parse_date_param(date_str) if date_str else timezone.localdate()
            queryset = queryset.filter(logged_at__date=target).order_by("logged_at")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WeightLogViewSet(viewsets.ModelViewSet):
    """A user's weight history, ordered by date. Scoped to request.user."""

    serializer_class = WeightLogSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return WeightLog.objects.filter(user=self.request.user).order_by(
            "date", "created_at"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
