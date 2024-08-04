from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttributeValueViewSet

router = DefaultRouter()
router.register(r'attribute-values', AttributeValueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
