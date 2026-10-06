import schedule
import time
import traceback
from datetime import datetime
from auto_maganghub import main_job

def safe_job():
    # Lewati Sabtu (5) & Minggu (6)
    if datetime.now().weekday() >= 5:
        print("[i] Akhir pekan, laporan dilewati.")
        return
    try:
        main_job()
    except Exception:
        print("[!] Job gagal, runner tetap berjalan:") 
        traceback.print_exc()

# Jam 16:00 WIB, tidak tergantung zona waktu sistem
schedule.every().day.at("16:30", "Asia/Jakarta").do(safe_job)

print("Agent MagangHub standby... Akan otomatis mengirim laporan pukul 16:30 WIB.")
print(f"[i] Jadwal berikutnya: {schedule.next_run()}")

while True:
    schedule.run_pending()
    time.sleep(30)