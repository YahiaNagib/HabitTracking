from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

    path("", views.home, name="main"),
    path("add", views.AddHabit, name="add"),
    path("habit/<str:name>", views.HabitDetails, name="details"),
    path("statistics", views.Statistics, name="statistics"),
    path("statistics/<str:name>", views.HabitStatistics, name="habitStatistics"),

]
