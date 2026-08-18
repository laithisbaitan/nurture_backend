from datetime import date as date_cls, timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from logs.models import FoodLog, WeightLog


def parse_date_param(value, field_name):
    try:
        return date_cls.fromisoformat(value)
    except ValueError:
        from rest_framework.exceptions import ValidationError

        raise ValidationError({field_name: "Invalid date, expected YYYY-MM-DD."})


def build_daily_totals(user, target_date):
    logs = FoodLog.objects.filter(user=user, logged_at__date=target_date).select_related(
        "food_item"
    )

    totals = {
        "date": target_date.isoformat(),
        "total_calories": 0.0,
        "total_protein_g": 0.0,
        "total_carbs_g": 0.0,
        "total_fat_g": 0.0,
        "micros_json": {},
    }

    for entry in logs:
        multiplier = entry.quantity
        food = entry.food_item
        totals["total_calories"] += food.calories * multiplier
        totals["total_protein_g"] += food.protein_g * multiplier
        totals["total_carbs_g"] += food.carbs_g * multiplier
        totals["total_fat_g"] += food.fat_g * multiplier

        for key, value in (food.micros_json or {}).items():
            if isinstance(value, (int, float)):
                totals["micros_json"][key] = totals["micros_json"].get(key, 0.0) + (
                    float(value) * multiplier
                )

    return totals


class DailyProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get("date")
        target_date = parse_date_param(date_str, "date") if date_str else timezone.localdate()
        return Response(build_daily_totals(request.user, target_date))


class WeeklyProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_str = request.query_params.get("start")
        start_date = (
            parse_date_param(start_str, "start") if start_str else timezone.localdate()
        )
        days = [
            build_daily_totals(request.user, start_date + timedelta(days=offset))
            for offset in range(7)
        ]
        return Response(days)


class WeightTrendView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = WeightLog.objects.filter(user=request.user).order_by("date", "created_at")
        return Response([{"date": row.date.isoformat(), "weight_kg": row.weight_kg} for row in rows])
