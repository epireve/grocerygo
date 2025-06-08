from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("deals/", views.deals, name="deals"),
    path("about/", views.about, name="about"),
]
