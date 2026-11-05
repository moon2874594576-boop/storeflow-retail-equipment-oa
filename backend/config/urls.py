from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from apps.loans.token_views import ActiveTokenRefreshView
from drf_spectacular.views import SpectacularAPIView
from apps.loans.views import (LoginView, MeView, PasswordView, CategoryView, StoreViewSet, AssetViewSet,
    LoanViewSet, DashboardView, AuditViewSet, AccountViewSet, health, frontend)

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="store")
router.register("assets", AssetViewSet, basename="asset")
router.register("requests", LoanViewSet, basename="loan-request")
router.register("audit", AuditViewSet, basename="audit")
router.register("accounts", AccountViewSet, basename="account")
urlpatterns = [
    path("api/health/", health), path("api/auth/login/", LoginView.as_view()),
    path("api/auth/me/", MeView.as_view()), path("api/auth/change_password/", PasswordView.as_view()),
    path("api/auth/refresh/", ActiveTokenRefreshView.as_view()), path("api/categories/", CategoryView.as_view()),
    path("api/dashboard/", DashboardView.as_view()), path("api/schema/", SpectacularAPIView.as_view()),
    path("api/", include(router.urls)), re_path(r"^(?P<path>.*)$", frontend),
]
