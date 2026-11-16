from django.contrib import admin

from .models import Car, Favorite, Notification, Rental


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "year", "price", "city", "owner", "created_at")
    list_filter = ("brand", "city", "transmission")
    search_fields = ("brand", "model", "owner__phone")


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("car", "user", "start_date", "end_date", "total_price", "status")
    list_filter = ("status",)


admin.site.register(Favorite)
admin.site.register(Notification)
