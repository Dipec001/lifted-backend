from django.urls import path
from .import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.index, name='home'),
    path('sentry-debug/', views.trigger_error),
    path('apple/login/', views.AppleLogin.as_view(), name='apple-login'),
    path('apple/register/', views.UserRegistration.as_view(), name='apple-register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('feeds/', views.FeedListCreateView.as_view(), name='feed-list-create'),
    path('feeds/<uuid:pk>/', views.FeedRetrieveUpdateView.as_view(), name='feed-retrieve-update'),
    path('feeds/<uuid:pk>/like/', views.LikeActionView.as_view(), name='like-action'),
    path('feeds/<uuid:pk>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('workouts/', views.WorkoutListView.as_view(), name='workouts'),
    path('exercises/', views.ExercisesView.as_view(), name='list_all_exercises'),
    path('exercises/<str:workout>/', views.ExercisesView.as_view(), name='list_workout_type_exercises'),
    # User Workout Endpoints
    path('user-workouts/', views.UserWorkoutListCreateAPIView.as_view(), name='user-workout-list-create'),
    path('user-workouts/<int:pk>/', views.UserWorkoutRetrieveUpdateView.as_view(), name='user-workout-retrieve'),
    path('edit-set/<int:set_id>/', views.EditSetAPIView.as_view(), name='edit_set'),
    path('delete-set/<int:set_id>/', views.DeleteSetAPIView.as_view(), name='delete_set'),
    path('add-set/<int:selected_exercise_id>/', views.AddSetAPIView.as_view(), name='add_set'),

    #FOllow
    path('follow/<int:pk>/', views.FollowAPIView.as_view(), name='follow'),
    # path('unfollow/<int:pk>/', views.UnFollowAPIView.as_view(), name='unfollow'),

]