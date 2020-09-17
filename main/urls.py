from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

    path("", views.home, name="main"),
    path("add", views.add_habit, name="add"),
    path("habit/<str:name>", views.habit_details, name="details"),
    path("statistics", views.statistics, name="statistics"),
]
