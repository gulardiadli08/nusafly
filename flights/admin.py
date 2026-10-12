from django.contrib import admin
from .models import Airport, Airline, Flight, Booking

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("iata_code", "city", "name", "country")
    search_fields = ("iata_code", "city", "name")

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ("name", "iata_code")

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("flight_number", "airline", "origin", "destination", "departure_at", "price", "available_seats", "status")
    list_filter = ("status", "airline", "origin", "destination")
    search_fields = ("flight_number", "origin__city", "destination__city")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_code", "user", "flight", "passenger_count", "total_amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("booking_code", "passenger_name", "passenger_email")
    readonly_fields = ("booking_code", "created_at")
