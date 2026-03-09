from django.urls import path
from .views import (
    RegisterAPIView, CustomAuthToken, UserDetailAPIView,
    RegisterPageView, LoginPageView,
)

urlpatterns = [
    # API endpoints
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('me/', UserDetailAPIView.as_view(), name='user-detail'),

    # Frontend pages
    path('register_page/', RegisterPageView.as_view(), name='register_page'),
    path('login_page/', LoginPageView.as_view(), name='login_page'),
]