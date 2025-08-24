from django.urls import path

from habits.views import (HabitsCreateAPIView,
                          HabitsRetrieveUpdateDestroyAPIView,
                          PublicHabitsListAPIView,
                          UserHabitsListAPIView)

app_name = "habits"

urlpatterns = [
    path("habits/", HabitsCreateAPIView.as_view(), name="habit-create"),
    path("habits/user/", UserHabitsListAPIView.as_view(), name="habits-user-list"),
    path("habits/public/", PublicHabitsListAPIView.as_view(), name="habits-public-list"),
    path("habits/<int:pk>/", HabitsRetrieveUpdateDestroyAPIView.as_view(), name="habit-detail"),
]
