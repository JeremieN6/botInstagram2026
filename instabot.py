import os
import logging
import time
from instagrapi import Client
import requests
from dotenv import load_dotenv

# Chargement du fichier .env
load_dotenv(".env.local")
print("✅ Fichier .env.local chargé")

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Fonction pour envoyer un message Telegram
def send_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload)

try:
    cl = Client()
    cl.login(USERNAME, PASSWORD)
    send_telegram("🔐 Connexion réussie à Instagram")

    # Liste d'utilisateurs à traiter
    usernames = ["mathildtantot", "sophieraiin", "cecerose"]

    for username in usernames:
        send_telegram(f"🔄 Traitement de {username}...")
        try:
            user_id = cl.user_id_from_username(username)
            medias = cl.user_medias(user_id, amount=5)

            for media in medias:
                cl.media_like(media.id)
                send_telegram(f"❤️ Post liké de {username}")
                comments = cl.media_comments(media.id)
                for c in comments[:5]:
                    cl.media_comment_like(c.pk)
                    send_telegram(f"💬 Commentaire liké sur {username}")

        except Exception as e:
            send_telegram(f"❌ Erreur pour {username} : {str(e)}")

except Exception as err:
    send_telegram(f"🚫 ERREUR GÉNÉRALE : {str(err)}")
