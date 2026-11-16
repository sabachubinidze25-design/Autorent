from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cars/", views.car_list, name="cars"),
    path("cars/add/", views.add_car, name="add_car"),
    path("cars/<int:car_id>/", views.car_detail, name="car_detail"),
    path("cars/<int:car_id>/like/", views.like_car, name="like_car"),
    path("rentals/<int:rental_id>/", views.rental_detail, name="rent_success"),
    path("rentals/<int:rental_id>/cancel/", views.rental_cancel, name="rental_cancel"),
    path("profile/", views.profile, name="profile"),
    path("notifications/", views.notifications, name="notifications"),
    path("support/", views.support, name="support"),
    # Any other address ending with "/" shows the friendly 404 page.
    re_path(r"^.*/$", views.page_not_found),
]
