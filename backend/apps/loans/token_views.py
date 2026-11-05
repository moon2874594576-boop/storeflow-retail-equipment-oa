from rest_framework_simplejwt.views import TokenRefreshView
from .authentication import ActiveTokenRefreshSerializer


class ActiveTokenRefreshView(TokenRefreshView):
    serializer_class = ActiveTokenRefreshSerializer
