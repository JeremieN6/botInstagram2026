import schedule
import time
import subprocess

def job():
    print("⏰ Lancement automatique du script Instagram...")
    subprocess.run(["python", "script.py"])

# 2 exécutions par jour
schedule.every().day.at("10:00").do(job)
schedule.every().day.at("18:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
