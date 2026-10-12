from datetime import datetime, time, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Airport, Booking, Flight

def home(request):
    airports = Airport.objects.all()
    today = timezone.localdate().isoformat()
    return render(request, "home.html", {"airports": airports, "today": today})

def search_flights(request):
    airports = Airport.objects.all()
    origin = request.GET.get("origin", "").upper()
    destination = request.GET.get("destination", "").upper()
    departure_date = request.GET.get("departure_date", "")
    passengers_raw = request.GET.get("passengers", "1")
    try:
        passengers = int(passengers_raw)
        if not 1 <= passengers <= 6:
            raise ValueError
    except ValueError:
        passengers = 1
        messages.error(request, "Jumlah penumpang harus antara 1 dan 6.")
    flights = Flight.objects.filter(status="SCHEDULED", available_seats__gte=passengers).select_related("airline", "origin", "destination")
    if origin:
        flights = flights.filter(origin__iata_code=origin)
    if destination:
        flights = flights.filter(destination__iata_code=destination)
    if departure_date:
        try:
            selected_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            start = timezone.make_aware(datetime.combine(selected_date, time.min))
            end = start + timedelta(days=1)
            flights = flights.filter(departure_at__gte=start, departure_at__lt=end)
        except ValueError:
            return HttpResponseBadRequest("Format tanggal tidak valid.")
    if origin and destination and origin == destination:
        flights = Flight.objects.none()
        messages.error(request, "Kota asal dan tujuan harus berbeda.")
    return render(request, "search_results.html", {
        "airports": airports, "flights": flights, "origin": origin,
        "destination": destination, "departure_date": departure_date,
        "passengers": passengers,
    })

def flight_detail(request, flight_id):
    flight = get_object_or_404(Flight.objects.select_related("airline", "origin", "destination"), pk=flight_id, status="SCHEDULED")
    return render(request, "flight_detail.html", {"flight": flight})

@login_required
@require_POST
def create_booking(request, flight_id):
    with transaction.atomic():
        flight = get_object_or_404(Flight.objects.select_for_update(), pk=flight_id, status="SCHEDULED")
        try:
            count = int(request.POST.get("passenger_count", "1"))
        except ValueError:
            count = 0
        if not 1 <= count <= 6:
            messages.error(request, "Jumlah penumpang tidak valid.")
            return redirect("flight_detail", flight_id=flight.id)
        if flight.available_seats < count:
            messages.error(request, "Kursi demo tidak mencukupi untuk jumlah penumpang ini.")
            return redirect("flight_detail", flight_id=flight.id)
        name = request.POST.get("passenger_name", "").strip()
        email = request.POST.get("passenger_email", "").strip()
        if not name or not email:
            messages.error(request, "Nama dan email penumpang wajib diisi.")
            return redirect("flight_detail", flight_id=flight.id)
        booking = Booking.objects.create(
            user=request.user, flight=flight, passenger_name=name,
            passenger_email=email, passenger_count=count,
            total_amount=flight.price * Decimal(count),
        )
        flight.available_seats -= count
        flight.save(update_fields=["available_seats"])
    messages.success(request, f"Pesanan {booking.booking_code} berhasil dibuat. Pembayaran masih simulasi.")
    return redirect("my_bookings")

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("flight", "flight__airline", "flight__origin", "flight__destination")
    return render(request, "bookings.html", {"bookings": bookings})

@login_required
@require_POST
def pay_booking(request, booking_id):
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update(), pk=booking_id, user=request.user)
        if booking.status == "PENDING_PAYMENT":
            booking.status = "CONFIRMED"
            booking.save(update_fields=["status"])
            messages.success(request, "Pembayaran simulasi berhasil. Tidak ada uang sungguhan yang ditagihkan.")
        else:
            messages.info(request, "Pesanan ini tidak sedang menunggu pembayaran.")
    return redirect("my_bookings")

@login_required
@require_POST
def cancel_booking(request, booking_id):
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update(), pk=booking_id, user=request.user)
        if booking.status == "CANCELLED":
            messages.info(request, "Pesanan sudah dibatalkan.")
        else:
            if booking.status == "PENDING_PAYMENT":
                flight = Flight.objects.select_for_update().get(pk=booking.flight_id)
                flight.available_seats += booking.passenger_count
                flight.save(update_fields=["available_seats"])
            booking.status = "CANCELLED"
            booking.save(update_fields=["status"])
            messages.success(request, "Pesanan dibatalkan.")
    return redirect("my_bookings")

def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        if not username or not email or len(password) < 8:
            messages.error(request, "Isi semua data. Kata sandi minimal 8 karakter.")
        elif User.objects.filter(Q(username__iexact=username) | Q(email__iexact=email)).exists():
            messages.error(request, "Username atau email sudah digunakan.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, "Akun berhasil dibuat.")
            return redirect("home")
    return render(request, "auth.html", {"mode": "register"})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next") or "home")
        messages.error(request, "Username atau kata sandi salah.")
    return render(request, "auth.html", {"mode": "login"})

@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "Anda telah keluar.")
    return redirect("home")
