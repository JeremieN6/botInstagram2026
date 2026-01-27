import os
import time
import random
from threading import Event
from datetime import datetime

import requests
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired
from dotenv import load_dotenv

# Load .env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SETTINGS_PATH = "settings.json"

MAX_LIKES_PER_ACCOUNT = 3
MAX_COMMENT_LIKES_PER_POST = 10

ACCOUNTS_TO_TARGET = [
    "mathildtantot", "popstantot", "sophieraiin", "cecerose",
    "cece_rosee_", "yumi.etoo", "wettmelons", "devon.shae"
]

WAIT_NOTIFICATION_BATCH_SIZE = 6


class StopRequested(Exception):
    """Raised when a manual stop is requested via Telegram."""


class BotStats:
    def __init__(self):
        self.posts_liked = 0
        self.comments_liked = 0
        self.challenges_encountered = 0
        self.wait_count = 0
        self.total_wait_time = 0.0
        self.errors_count = 0
        self.wait_batch_count = 0
        self.wait_batch_time = 0.0

    def format_wait_time(self):
        minutes = int(self.total_wait_time // 60)
        seconds = int(self.total_wait_time % 60)
        if minutes > 0:
            return f"{minutes}min{seconds}s"
        return f"{seconds}s"

    def get_summary(self):
        return (
            "🎯 Le Bot a terminé :\n"
            f"- 💖 {self.posts_liked} posts likés\n"
            f"- 💬 {self.comments_liked} commentaires likés\n"
            f"- 🚫 {self.challenges_encountered} challenges\n"
            f"- ⚠️ {self.errors_count} erreurs\n"
            f"- ⌛ {self.wait_count} attentes pour {self.format_wait_time()} d'attente totale"
        )

    def _notify_wait_batch(self):
        send_telegram_message(
            f"⏳ `{self.wait_batch_count}` attentes ont totalisé `{self.wait_batch_time:.1f}` secondes."
        )
        self.wait_batch_count = 0
        self.wait_batch_time = 0.0

    def register_wait(self, delay):
        if delay <= 0:
            return
        self.wait_count += 1
        self.total_wait_time += delay
        self.wait_batch_count += 1
        self.wait_batch_time += delay
        if self.wait_batch_count >= WAIT_NOTIFICATION_BATCH_SIZE:
            self._notify_wait_batch()

    def flush_wait_notifications(self):
        if self.wait_batch_count:
            self._notify_wait_batch()


def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.get(url, params=params)
    except Exception as e:
        print(f"[Telegram Error] {e}")


# Test de démarrage
send_telegram_message("✅ Test message - Bot is running.")


def init_instagram_client():
    cl = Client()
    try:
        if os.path.exists(SETTINGS_PATH):
            cl.load_settings(SETTINGS_PATH)
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SETTINGS_PATH)
    except ChallengeRequired:
        send_telegram_message("⚠️ *Challenge Instagram requis.* Interruption du bot.")
        raise
    except Exception as e:
        send_telegram_message(f"🔁 *Nouvelle tentative de login...* Erreur : `{e}`")
        cl = Client()
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SETTINGS_PATH)
    return cl


def ensure_not_stopped(stop_event):
    if stop_event and stop_event.is_set():
        raise StopRequested()


def wait_random_delay(min_sec, max_sec, stats, stop_event=None):
    delay = random.uniform(min_sec, max_sec)
    if stop_event is None:
        stats.register_wait(delay)
        time.sleep(delay)
        return

    waited = 0.0
    step = 0.5
    while waited < delay:
        if stop_event.is_set():
            if waited:
                stats.register_wait(waited)
            raise StopRequested()
        chunk = min(step, delay - waited)
        time.sleep(chunk)
        waited += chunk

    stats.register_wait(waited)


def run_bot(origin="manuel", stop_event: Event | None = None):
    stats = BotStats()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_telegram_message(f"🚀 *Script lancé* en mode `{origin}` à `{now}`")

    cl = init_instagram_client()
    random.shuffle(ACCOUNTS_TO_TARGET)

    aborted = False

    try:
        for account in ACCOUNTS_TO_TARGET:
            ensure_not_stopped(stop_event)
            try:
                send_telegram_message(f"🔍 Traitement de `{account}`...")
                user_id = cl.user_id_from_username(account)

                try:
                    medias = cl.user_medias(user_id, amount=5)
                except KeyError as err:
                    stats.errors_count += 1
                    send_telegram_message(
                        f"⚠️ Impossible de récupérer les médias de `{account}` (message Instagram: `{err}`) – passage au suivant."
                    )
                    continue

                random.shuffle(medias)
                posts_liked = 0

                for media in medias[:MAX_LIKES_PER_ACCOUNT]:
                    ensure_not_stopped(stop_event)
                    media_info = cl.media_info(media.id)
                    if media_info.has_liked:
                        send_telegram_message(f"🔁 Post déjà liké pour `{account}` – passage au suivant.")
                        continue

                    cl.media_like(media.id)
                    posts_liked += 1
                    stats.posts_liked += 1
                    send_telegram_message(f"❤️ Post liké pour `{account}`")
                    wait_random_delay(4, 7, stats, stop_event)

                    comments = cl.media_comments(media.id)
                    comments_liked = 0
                    comments_checked = 0

                    for comment in comments[:MAX_COMMENT_LIKES_PER_POST]:
                        ensure_not_stopped(stop_event)
                        comments_checked += 1
                        if comment.has_liked:
                            continue
                        cl.comment_like(comment.pk)
                        comments_liked += 1
                        stats.comments_liked += 1
                        wait_random_delay(2, 4, stats, stop_event)

                    if comments_checked > 0 and comments_liked == 0:
                        send_telegram_message("💬 Aucun nouveau commentaire à liker – tous déjà traités.")
                    elif comments_liked > 0:
                        send_telegram_message(f"💬 `{comments_liked}` commentaires likés sur le post de `{account}`")

                    wait_random_delay(5, 10, stats, stop_event)

                if posts_liked == 0:
                    send_telegram_message(f"✅ Tous les derniers posts de `{account}` ont déjà été likés – rien à faire.")

            except ChallengeRequired:
                stats.challenges_encountered += 1
                send_telegram_message(f"🚫 *Challenge requis* pour `{account}` – passage au suivant.")
                continue
            except LoginRequired:
                stats.errors_count += 1
                send_telegram_message("🔁 *Session expirée* – reconnexion...")
                cl = init_instagram_client()
            except StopRequested:
                raise
            except Exception as e:
                stats.errors_count += 1
                send_telegram_message(f"❌ *Erreur avec `{account}`* : `{e}`")

            wait_random_delay(15, 30, stats, stop_event)

    except StopRequested:
        aborted = True

    stats.flush_wait_notifications()
    end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if aborted:
        send_telegram_message(f"🛑 *Script interrompu manuellement* à `{end}`")
    else:
        send_telegram_message(f"✅ *Script terminé* à `{end}`")
    send_telegram_message(stats.get_summary())


if __name__ == "__main__":
    run_bot()
