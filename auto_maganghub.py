import os
import asyncio
import time
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

# Gemini Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Class Laporan Harian
class LaporanHarian(BaseModel):
    uraian_aktivitas: str = Field(description="Uraian aktivitas harian (min 110 karakter).")
    pembelajaran: str = Field(description="Pembelajaran yang diperoleh (min 110 karakter).")
    kendala: str = Field(description="Kendala dan penanganannya (min 110 karakter).")

# Function Generate Laporan & Prompt Engineering
def generate_laporan(catatan_harian: str) -> LaporanHarian:
    # Daftar model utama dan cadangan jika server 503 / overload
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
    max_attempts_per_model = 3

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Kamu adalah asisten AI laporan magang. Ubah catatan singkat pengguna "
            "menjadi teks laporan formal berkualitas. "
            "ATURAN WAJIB: Setiap bidang (uraian_aktivitas, pembelajaran, kendala) HARUS "
            "berisi MINIMAL 110 KARAKTER agar memenuhi syarat sistem."
        )),
        ("user", "Catatan aktivitas hari ini: {catatan}")
    ])

    for model_name in models_to_try:
        print(f"[+] Mencoba memproses dengan model: {model_name}")
        
        for attempt in range(1, max_attempts_per_model + 1):
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    api_key=GEMINI_API_KEY,
                    temperature=0.7,
                    timeout=60,
                )
                structured_llm = llm.with_structured_output(LaporanHarian)
                chain = prompt | structured_llm

                return chain.invoke({"catatan": catatan_harian})

            except Exception as e:
                print(f"[!] [Percobaan {attempt}/{max_attempts_per_model}] Server sibuk/error: {e}")
                if attempt < max_attempts_per_model:
                    wait_time = attempt * 5  # Menunggu 5d, 10d, dst. sebelum coba lagi
                    print(f"[+] Menunggu {wait_time} detik sebelum mencoba ulang...")
                    time.sleep(wait_time)
                else:
                    print(f"[!] Gagal menggunakan {model_name}, mencoba model cadangan...\n")

    raise RuntimeError("Gagal mendapatkan respon dari server Gemini setelah beberapa kali percobaan.")

# Automation Playwright dengan cookie session
async def submit_to_maganghub(laporan: LaporanHarian):
    async with async_playwright() as p:
        user_data_dir = "./user_data"

        # Koordinat lokasi PT Prakarsalanggeng Maju Bersama
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False, 
            geolocation={"latitude": -6.202264888227225, "longitude": 106.46284744536752},
            permissions=["geolocation"]
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Buka halaman Maganghub
        print("[+] Membuka halaman Maganghub...")
        await page.goto("https://monev.maganghub.kemnaker.go.id/dashboard/")

        # Cek apakah sudah di dashboard atau perlu login
        try:
            # Coba cari tombol laporan dalam waktu 5 detik
            await page.wait_for_selector("text=Isi Laporan Hari Ini", timeout=5000)
            print("[+] Sesi login aktif, langsung mengisi laporan...")
        except Exception:
            print("\n" + "="*60)
            print("[!] ANDA BELUM LOGIN ATAU TERLEMPAR KE HALAMAN LOGIN/SSO.")
            print("[!] Silakan lakukan LOGIN MANUAL di jendela browser yang terbuka.")
            print("[!] Waktu tunggu disediakan 3 menit hingga Anda masuk ke Dashboard...")
            print("="*60 + "\n")
            
            # Beri waktu 3 menit (180.000 ms) bagi Anda untuk mengetik email/password & OTP
            await page.wait_for_selector("text=Isi Laporan Hari Ini", timeout=180000)

        # Klik tombol isi laporan hari ini
        await page.click("text=Isi Laporan Hari Ini")
        await page.wait_for_selector("text=Tambah laporan")

        # Mengisi textarea di maganghub
        textareas = page.locator("textarea")
        await textareas.nth(0).fill(laporan.uraian_aktivitas)
        await textareas.nth(1).fill(laporan.pembelajaran)
        await textareas.nth(2).fill(laporan.kendala)

        # Centang checkbox konfirmasi kehadiran
        await page.check('input[type="checkbox"]')

        # Klik tombol Simpan dan Kirim
        print("[+] Menekan tombol Simpan dan Kirim...")
        await page.click("text=Simpan dan Kirim")

        print("[✓] Laporan harian berhasil dikirim otomatis!")
        await asyncio.sleep(5)
        await context.close()

# Main function untuk eksekusi script
def main_job():
    file_catatan = "catatan.txt"

    if os.path.exists(file_catatan):
        with open(file_catatan, "r", encoding="utf-8") as f:
            catatan_input = f.read().strip()
    else:
        catatan_input = ""

    if not catatan_input:
        catatan_input = "Melanjutkan koordinasi tim, pengerjaan tugas rutin harian, serta debugging sistem."

    print(f"\n[+] Membaca {file_catatan}: '{catatan_input}'")
    print("[+] Mengolah dengan Gemini via LangChain...")
    hasil = generate_laporan(catatan_input)
    
    print("\n=== Pratinjau Hasil Laporan ===")
    print(f"1. Uraian    : {hasil.uraian_aktivitas}")
    print(f"2. Belajar   : {hasil.pembelajaran}")
    print(f"3. Kendala   : {hasil.kendala}\n")
    
    asyncio.run(submit_to_maganghub(hasil))

if __name__ == "__main__":
    main_job()