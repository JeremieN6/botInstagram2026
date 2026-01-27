# bot_launcher.py
import asyncio
import logging
import os
from datetime import datetime, timedelta
from threading import Event

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from dotenv import load_dotenv

from script import run_bot

logging.basicConfig(level=logging.INFO)

if os.path.exists(".env.local"):
    load_dotenv(".env.local")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

_current_task = None
_stop_event: Event | None = None
_last_run_started: datetime | None = None
_last_run_completed: datetime | None = None
_last_run_error: str | None = None


def _is_running() -> bool:
    return _current_task is not None and not _current_task.done()


def _format_timedelta(delta: timedelta | None) -> str:
    if not delta:
        return "-"
    total_seconds = int(delta.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{seconds:02d}s"
    if minutes:
        return f"{minutes}m{seconds:02d}s"
    return f"{seconds}s"


def _on_run_complete(fut):
    global _last_run_completed, _last_run_error, _stop_event
    _last_run_completed = datetime.now()
    try:
        fut.result()
        _last_run_error = None
    except Exception as exc:  # pragma: no cover - defensive
        _last_run_error = str(exc)
        logging.exception("Bot execution failed", exc_info=exc)
    _stop_event = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _current_task, _stop_event, _last_run_started
    if _is_running():
        await update.message.reply_text("⚠️ Un traitement est déjà en cours. Utilise /status ou /stop.")
        return

    if BOT_TOKEN is None:
        await update.message.reply_text("❌ TOKEN Telegram manquant – vérifie .env.local")
        return

    loop = asyncio.get_running_loop()
    _stop_event = Event()
    _last_run_started = datetime.now()
    await update.message.reply_text("✅ Bot lancé, tu seras notifié ici.")

    _current_task = loop.run_in_executor(None, lambda: run_bot(origin="telegram", stop_event=_stop_event))
    _current_task.add_done_callback(_on_run_complete)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if _is_running():
        elapsed = datetime.now() - _last_run_started if _last_run_started else None
        await update.message.reply_text(
            f"📊 Le bot est en cours depuis {_format_timedelta(elapsed)}. Utilise /stop pour interrompre."
        )
        return

    if _last_run_completed:
        msg = f"✅ Dernière exécution terminée à {_last_run_completed:%Y-%m-%d %H:%M:%S}."
        if _last_run_error:
            msg += f" (⚠️ Erreur: {_last_run_error})"
    else:
        msg = "ℹ️ Le bot n'a pas encore été lancé dans cette session."
    await update.message.reply_text(msg)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _stop_event
    if not _is_running():
        await update.message.reply_text("ℹ️ Aucun traitement en cours.")
        return

    if _stop_event and _stop_event.is_set():
        await update.message.reply_text("⏳ Une demande d'arrêt est déjà en cours, merci de patienter.")
        return

    if _stop_event:
        _stop_event.set()
    await update.message.reply_text("🛑 Arrêt demandé. Le bot va s'interrompre proprement.")


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("stop", stop))
    app.run_polling()
