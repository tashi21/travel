from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.hotel_search_view, name="search"),
    path("<int:my_id>/", views.details_view, name="details"),
]
