import random
import subprocess
import time

import schedule


def job():
    print("⏰ Lancement automatique du script Instagram...")
    subprocess.run(["python", "script.py"], check=False)


def _register_daily_job(hour, minute):
    schedule.every(2).days.at(f"{hour:02d}:{minute:02d}").do(job)


# Exécution tous les 2 jours à une heure légèrement aléatoire pour casser le pattern
_register_daily_job(hour=10, minute=random.randint(0, 20))

while True:
    schedule.run_pending()
    time.sleep(60)
