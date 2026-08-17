from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import FoodItem
from .serializers import (
    FoodItemSearchSerializer,
    FoodItemSerializer,
    FoodPhotoUploadSerializer,
)

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
        # Manual entry always starts as "manual", regardless of the payload.
        serializer.save(created_by=self.request.user, source=FoodItem.Source.MANUAL)

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
    )
    def photo(self, request):
        """Step 1 of the photo flow: upload only an image.

        Creates a placeholder FoodItem with source=photo_pending_ai. Step 2 is a
        normal PATCH /api/foods/{id}/ filling in nutrition and setting
        source=manual. An AI extraction step can later slot between the two.
        """
        serializer = FoodPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = FoodItem.objects.create(
            photo=serializer.validated_data["photo"],
            name_en="",
            name_ar="",
            serving_size=0,
            serving_unit="",
            calories=0,
            protein_g=0,
            carbs_g=0,
            fat_g=0,
            source=FoodItem.Source.PHOTO_PENDING_AI,
            created_by=request.user,
        )
        return Response(
            FoodItemSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response([])
        matches = FoodItem.objects.filter(
            Q(name_en__icontains=query) | Q(name_ar__icontains=query)
        ).order_by("name_en")[:SEARCH_RESULT_LIMIT]
        return Response(FoodItemSearchSerializer(matches, many=True).data)
