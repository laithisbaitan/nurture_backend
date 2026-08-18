from django.urls import path

from .views import DailyProgressView, WeeklyProgressView, WeightTrendView

urlpatterns = [
    path("daily/", DailyProgressView.as_view(), name="progress-daily"),
    path("weekly/", WeeklyProgressView.as_view(), name="progress-weekly"),
    path("weight-trend/", WeightTrendView.as_view(), name="progress-weight-trend"),
]
