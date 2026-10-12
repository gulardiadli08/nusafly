# NusaFly — Website Pemesanan Tiket Pesawat (Demo)

Aplikasi Django untuk latihan dan demo lokal. UI berbahasa Indonesia; backend menggunakan Django dan SQLite agar mudah dijalankan tanpa instalasi database terpisah.

> **Penting:** penerbangan, harga, kursi, dan pembayaran adalah data simulasi. Aplikasi ini tidak terhubung ke maskapai atau payment gateway sungguhan.

## Fitur
- Beranda dan pencarian penerbangan berdasarkan asal, tujuan, tanggal, serta jumlah penumpang.
- Hasil pencarian dan halaman detail penerbangan.
- Registrasi, login, dan logout.
- Membuat pesanan, kode booking, riwayat pesanan, pembayaran simulasi, dan pembatalan.
- Django Admin untuk mengelola bandara, maskapai, penerbangan, dan pesanan.
- Responsive layout untuk desktop dan mobile.

## Persyaratan
- Python 3.10+ (disarankan Python 3.12 atau versi yang didukung Django 5.2)
- Internet hanya diperlukan saat pertama memasang Django melalui pip.

## Jalankan di Windows (PowerShell)
Buka PowerShell pada folder `flight-booking-local`, lalu jalankan:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Buka `http://127.0.0.1:8000/`.

Jika PowerShell menolak aktivasi environment, jalankan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, kemudian aktifkan ulang environment. Alternatifnya, gunakan Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Admin tersedia di `http://127.0.0.1:8000/admin/`. Jalankan `createsuperuser` terlebih dahulu untuk membuat akun admin.

## Jalankan di macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

## Alur uji cepat
1. Buka beranda, cari rute CGK → DPS atau CGK → SUB pada tanggal yang tersedia.
2. Daftar akun, atau masuk bila sudah punya akun.
3. Pilih penerbangan, isi data penumpang, lalu buat pesanan.
4. Buka **Pesanan saya**, lalu gunakan **Bayar (simulasi)** atau **Batalkan**.
5. Login ke `/admin/` untuk mengelola data demo.

Seed command dapat dijalankan ulang untuk memastikan katalog demo tersedia. Data yang sudah ada tidak otomatis dihapus.

## Struktur
- `flightbooking/`: konfigurasi Django.
- `flights/`: model, view, admin, dan seed command.
- `templates/`: halaman HTML Django.
- `static/css/style.css`: styling responsive.
- `static/js/app.js`: interaksi kecil di browser.
- `AGENTS.md`: pedoman proyek dan coding agent.

## Catatan untuk pengembangan berikutnya
Ini merupakan MVP awal. Sebelum digunakan untuk pengguna sungguhan, tambahkan pengujian otomatis, validasi dan kebijakan booking yang lebih kuat, konfigurasi secret via environment, throttling login, serta review keamanan. Gunakan payment gateway dan data penerbangan resmi hanya setelah integrasi dan pengujian yang tepat.
