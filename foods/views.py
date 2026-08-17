from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import FoodItem
from .serializers import FoodItemSearchSerializer, FoodItemSerializer

SEARCH_RESULT_LIMIT = 25


class FoodItemPagination(PageNumberPagination):
    page_size = 20


class FoodItemViewSet(viewsets.ModelViewSet):
    """Global shared food database — deliberately NOT scoped per user."""

    queryset = FoodItem.objects.order_by("-created_at")
    serializer_class = FoodItemSerializer
    pagination_class = FoodItemPagination
    # Spec: list, create, retrieve, patch. No PUT/DELETE in v1.
    http_method_names = ["get", "post", "patch", "head", "options"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response([])
        matches = FoodItem.objects.filter(
            Q(name_en__icontains=query) | Q(name_ar__icontains=query)
        ).order_by("name_en")[:SEARCH_RESULT_LIMIT]
        return Response(FoodItemSearchSerializer(matches, many=True).data)
