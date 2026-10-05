# MagangHub Agent Attendance 🚀

Bot otomatisasi berbasis AI untuk mengisi dan mengirim laporan harian peserta magang di portal **MagangHub Kemnaker** secara terjadwal. Menggunakan **LangChain + Google Gemini API** untuk mengubah catatan kasar menjadi laporan formal, dan **Playwright** untuk otomatisasi browser.

---

## ✨ Fitur Utama

- **AI Content Generation**: Mengolah catatan singkat dari `catatan.txt` menjadi 3 bagian laporan formal (*Uraian Aktivitas*, *Pembelajaran*, *Kendala*).
- **Minimum Character Guarantee**: Setiap bidang dipaksa minimal 110 karakter sesuai syarat sistem MagangHub.
- **Geolocation Setting**: Mengatur koordinat lokasi browser ke titik **PT Prakarsalanggeng Maju Bersama** (`-6.201491596563132`, `106.46303524820786`).
- **Persistent Session Handling**: Cookie dan sesi browser disimpan di `./user_data`, jadi login SSO Kemnaker cukup sekali di awal.
- **Automated Daily Scheduler**: `runner.py` menjalankan pengisian laporan setiap pukul **16:00 WIB**, melewati Sabtu dan Minggu, dan tetap hidup walau satu job gagal.

---

## 🛠️ Teknologi

- **Python 3.10+**
- **LangChain** (`langchain-google-genai`) & **Google Gemini API** (`gemini-3.6-flash`)
- **Playwright** (Async Python API)
- **Pydantic** (validasi output terstruktur dari AI)
- **Schedule** + **pytz** (penjadwalan dengan zona waktu)

---

## 📁 Struktur Proyek

```text
Maganghub-Agent-Attendance/
├── user_data/           # Session & cookies browser Playwright (dibuat otomatis)
├── .env                 # API Key rahasia (Gemini API Key)
├── .env.example         # Template variabel lingkungan
├── .gitignore           # File/folder yang diabaikan Git
├── auto_maganghub.py    # AI generator + Playwright automation
├── runner.py            # Scheduler otomatis jam 16:00 WIB
├── catatan.txt          # Input catatan aktivitas harian
└── requirements.txt     # Dependensi Python
```

---

## 📦 Isi `requirements.txt`

```text
langchain-google-genai
langchain-core
pydantic
playwright
python-dotenv
schedule
pytz
```

## 🔐 Isi `.env.example`

```text
GEMINI_API_KEY=isi_api_key_gemini_kamu
```

## 🙈 Isi `.gitignore`

```text
.env
user_data/
__pycache__/
venv/
```

---

## 🚀 Cara Pakai

### 1. Clone repository

```bash
git clone https://github.com/naubass/Maganghub-Agent-Attendance.git
cd Maganghub-Agent-Attendance
```

### 2. Buat virtual environment (disarankan)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependensi

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Siapkan API Key Gemini

1. Buat API key di [Google AI Studio](https://aistudio.google.com/apikey).
2. Salin template lalu isi:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

3. Buka `.env` dan isi `GEMINI_API_KEY` dengan key kamu.

### 5. Isi catatan harian

Edit `catatan.txt` dengan ringkasan kegiatan hari ini, cukup singkat:

```text
Meeting koordinasi tim, membuat endpoint API baru, dan debugging bug login.
```

Kalau file kosong atau tidak ada, script memakai catatan default.

### 6. Login pertama kali (sekali saja)

Jalankan manual untuk menyimpan sesi login:

```bash
python auto_maganghub.py
```

- Browser Chromium akan terbuka.
- Login manual via SSO Kemnaker (email, password, OTP) dalam waktu 3 menit.
- Sesi tersimpan di `./user_data`, jadi run berikutnya tidak perlu login lagi.

> ⚠️ Perintah ini **langsung mengirim laporan**, tidak menunggu jam 16:00. Pakai hanya untuk login awal atau tes.

### 7. Jalankan scheduler harian

```bash
python runner.py
```

Kalau berhasil akan muncul:

```text
Agent MagangHub standby... Akan otomatis mengirim laporan pukul 16:00 WIB.
```

Biarkan terminal tetap terbuka dan laptop tidak sleep sampai jam 16:00. Pada jam tersebut bot akan membaca `catatan.txt`, membuat laporan lewat Gemini, lalu mengisi dan mengirim formulir di MagangHub.

### 8. (Opsional) Tes jadwal cepat

Di `runner.py`, ubah sementara `"16:00"` menjadi satu menit ke depan, jalankan `python runner.py`, lalu kembalikan ke `"16:00"`.

---

## 🔁 Alur Harian

1. Pagi/siang: update `catatan.txt` dengan kegiatan hari ini.
2. Pastikan `python runner.py` sedang berjalan.
3. Pukul 16:00 WIB: laporan dibuat dan dikirim otomatis.
4. Cek hasilnya di dashboard MagangHub.

---

## 🧯 Troubleshooting

| Masalah | Penyebab & Solusi |
|---|---|
| Laporan terkirim langsung, tidak nunggu jam 16:00 | Kamu menjalankan `auto_maganghub.py`. Jalankan `python runner.py`. |
| `ModuleNotFoundError` | Aktifkan venv dan jalankan `pip install -r requirements.txt`. |
| Browser tidak terbuka / error Playwright | Jalankan `playwright install chromium`. |
| Diminta login lagi | Sesi kedaluwarsa. Login manual saat jendela browser terbuka (batas 3 menit). |
| Error `user_data` terkunci | Tutup semua jendela Chromium sisa run sebelumnya, lalu ulangi. |
| Error Gemini / model not found | Cek `GEMINI_API_KEY` di `.env` dan pastikan nama model di `auto_maganghub.py` valid untuk akunmu. |
| Jam tidak sesuai WIB | `runner.py` sudah memakai `Asia/Jakarta`. Pastikan `pytz` terinstal. |
| Tidak ada laporan di akhir pekan | Memang disengaja, Sabtu dan Minggu dilewati. |
| Selector tidak ketemu | Tampilan portal berubah. Perbarui selector di `submit_to_maganghub()`. |

---

## ⚠️ Disclaimer

Proyek ini dibuat untuk keperluan belajar dan efisiensi pribadi. Isi `catatan.txt` dengan kegiatan yang benar-benar kamu kerjakan, dan pastikan penggunaannya sesuai aturan program MagangHub dan perusahaan tempatmu magang. Jangan commit file `.env` dan folder `user_data/` ke repository publik.
