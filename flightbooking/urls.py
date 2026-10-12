from django.contrib import admin
from django.urls import path
from flights import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("cari/", views.search_flights, name="search_flights"),
    path("penerbangan/<int:flight_id>/", views.flight_detail, name="flight_detail"),
    path("pesan/<int:flight_id>/", views.create_booking, name="create_booking"),
    path("pesanan/", views.my_bookings, name="my_bookings"),
    path("pesanan/<int:booking_id>/bayar/", views.pay_booking, name="pay_booking"),
    path("pesanan/<int:booking_id>/batal/", views.cancel_booking, name="cancel_booking"),
    path("daftar/", views.register, name="register"),
    path("masuk/", views.login_view, name="login"),
    path("keluar/", views.logout_view, name="logout"),
]
