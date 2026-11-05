from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.user_urls')),
    path('api/employees/', include('apps.employees.urls')),
    path('api/approvals/', include('apps.approvals.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
]
