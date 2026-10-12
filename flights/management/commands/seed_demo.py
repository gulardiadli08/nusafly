from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from flights.models import Airport, Airline, Flight

class Command(BaseCommand):
    help = "Membuat data bandara, maskapai, dan penerbangan demo yang aman diulang."

    def handle(self, *args, **options):
        airports_data = [
            ("CGK", "Soekarno-Hatta International Airport", "Jakarta"),
            ("DPS", "I Gusti Ngurah Rai International Airport", "Denpasar"),
            ("SUB", "Juanda International Airport", "Surabaya"),
            ("YIA", "Yogyakarta International Airport", "Yogyakarta"),
            ("KNO", "Kualanamu International Airport", "Medan"),
            ("UPG", "Sultan Hasanuddin International Airport", "Makassar"),
            ("BPN", "Sultan Aji Muhammad Sulaiman Airport", "Balikpapan"),
        ]
        airports = {}
        for code, name, city in airports_data:
            airport, _ = Airport.objects.update_or_create(iata_code=code, defaults={"name": name, "city": city, "country": "Indonesia"})
            airports[code] = airport
        airline_data = [
            ("ID", "Batik Air", "🟥"),
            ("QG", "Citilink", "🟩"),
            ("IU", "Super Air Jet", "🟧"),
            ("GA", "Garuda Indonesia", "🟦"),
        ]
        airlines = {}
        for code, name, emoji in airline_data:
            airline, _ = Airline.objects.update_or_create(iata_code=code, defaults={"name": name, "logo_emoji": emoji})
            airlines[code] = airline
        routes = [
            ("CGK", "DPS", "ID", "ID 6512", 105, 115, 1250000, 0),
            ("CGK", "DPS", "QG", "QG 684", 180, 190, 980000, 0),
            ("CGK", "SUB", "IU", "IU 702", 130, 145, 780000, 0),
            ("CGK", "YIA", "GA", "GA 204", 95, 105, 1100000, 0),
            ("DPS", "CGK", "ID", "ID 6509", 220, 230, 1320000, 0),
            ("SUB", "CGK", "QG", "QG 711", 300, 310, 820000, 0),
            ("CGK", "KNO", "GA", "GA 182", 390, 405, 1450000, 0),
            ("CGK", "UPG", "IU", "IU 320", 460, 475, 1180000, 0),
            ("CGK", "BPN", "QG", "QG 420", 520, 535, 990000, 0),
            ("YIA", "DPS", "ID", "ID 6371", 580, 590, 870000, 0),
        ]
        today = timezone.localdate()
        created = 0
        for index, (origin, destination, carrier, number, hour, minute, price, stops) in enumerate(routes):
            # Spread departures across the next 21 days at local Jakarta time.
            day_offset = index % 14
            departure_day = today + timedelta(days=day_offset)
            departure = timezone.make_aware(datetime.combine(departure_day, datetime.min.time()).replace(hour=hour % 24, minute=minute % 60))
            # If departure hour is earlier than current time today, move to tomorrow.
            if departure <= timezone.now():
                departure += timedelta(days=1)
            arrival = departure + timedelta(minutes=95 + (index % 5) * 20)
            Flight.objects.update_or_create(
                flight_number=number,
                defaults={
                    "airline": airlines[carrier], "origin": airports[origin],
                    "destination": airports[destination], "departure_at": departure,
                    "arrival_at": arrival, "price": Decimal(price),
                    "available_seats": 18 + index % 20, "stops": stops, "status": "SCHEDULED",
                },
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Data demo siap: {len(airports)} bandara, {len(airlines)} maskapai, {created} penerbangan."))
