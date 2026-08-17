from rest_framework.routers import SimpleRouter

from .views import FoodLogViewSet, WeightLogViewSet

router = SimpleRouter()
router.register("logs", FoodLogViewSet, basename="foodlog")
router.register("weight", WeightLogViewSet, basename="weightlog")

urlpatterns = router.urls
