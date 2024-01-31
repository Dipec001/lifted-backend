from django.urls import path
from .import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.index, name='home'),
    path('apple/login/', views.AppleLogin.as_view(), name='apple-login'),
    path('apple/register/', views.UserRegistration.as_view(), name='apple-register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('feeds/', views.FeedListCreateView.as_view(), name='feed-list-create'),
    path('feeds/<uuid:pk>/', views.FeedRetrieveUpdateView.as_view(), name='feed-retrieve-update'),
    path('feeds/<uuid:pk>/like/', views.LikeActionView.as_view(), name='like-action'),
    path('feeds/<uuid:pk>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
]