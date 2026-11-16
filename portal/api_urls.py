from django.urls import path

from . import api_views as v

urlpatterns = [
    path("", v.index, name="api_index"),
    path("register/", v.register),
    path("login/", v.login),
    path("me/", v.me),
    path("cars/", v.cars),
    path("cars/<int:car_id>/", v.car, name="api_car"),
    path("cars/<int:car_id>/like/", v.like),
    path("cars/<int:car_id>/rent/", v.rent),
    path("rentals/", v.rentals),
    path("rentals/<int:rental_id>/cancel/", v.rental_cancel),
    path("favorites/", v.favorites),
    path("notifications/", v.notifications),
]
