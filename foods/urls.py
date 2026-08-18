from rest_framework.routers import SimpleRouter

from .views import FoodItemViewSet

router = SimpleRouter()
router.register("", FoodItemViewSet, basename="fooditem")

urlpatterns = router.urls
