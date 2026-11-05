from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApprovalTypeViewSet, ApprovalViewSet

router = DefaultRouter()
router.register(r'types', ApprovalTypeViewSet, basename='approval-type')
router.register(r'', ApprovalViewSet, basename='approval')

urlpatterns = [
    path('', include(router.urls)),
]
