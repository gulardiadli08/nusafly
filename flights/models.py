from django.conf import settings
from django.db import models
from django.utils import timezone
import secrets
import string

class Airport(models.Model):
    iata_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)
    country = models.CharField(max_length=80, default="Indonesia")

    class Meta:
        ordering = ["city", "iata_code"]

    def __str__(self):
        return f"{self.city} ({self.iata_code})"

class Airline(models.Model):
    iata_code = models.CharField(max_length=3, blank=True)
    name = models.CharField(max_length=120)
    logo_emoji = models.CharField(max_length=8, default="✈️")

    def __str__(self):
        return self.name

class Flight(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.PROTECT, related_name="flights")
    flight_number = models.CharField(max_length=12)
    origin = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="arrivals")
    departure_at = models.DateTimeField()
    arrival_at = models.DateTimeField()
    price = models.DecimalField(max_digits=12, decimal_places=0)
    available_seats = models.PositiveIntegerField(default=20)
    stops = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, default="SCHEDULED", choices=[("SCHEDULED", "Terjadwal"), ("CANCELLED", "Dibatalkan")])

    class Meta:
        ordering = ["departure_at"]

    def __str__(self):
        return f"{self.flight_number}: {self.origin.iata_code} → {self.destination.iata_code}"

    @property
    def duration_minutes(self):
        return max(0, int((self.arrival_at - self.departure_at).total_seconds() // 60))

class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING_PAYMENT", "Menunggu pembayaran"),
        ("CONFIRMED", "Dibayar (simulasi)"),
        ("CANCELLED", "Dibatalkan"),
    ]
    booking_code = models.CharField(max_length=12, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="flight_bookings")
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT, related_name="bookings")
    passenger_name = models.CharField(max_length=140)
    passenger_email = models.EmailField()
    passenger_count = models.PositiveSmallIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default="PENDING_PAYMENT")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.booking_code:
            alphabet = string.ascii_uppercase + string.digits
            self.booking_code = "FLY" + "".join(secrets.choice(alphabet) for _ in range(7))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.booking_code
