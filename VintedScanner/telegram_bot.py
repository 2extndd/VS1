import sys
import os
import logging
from telegram.ext import Application, CommandHandler
import Config
import json
import time
import asyncio

async def safe_send_document(update, context, file_path):
    for attempt in range(3):
        try:
            await update.message.reply_document(document=open(file_path, "rb"))
            return
        except Exception as e:
            await update.message.reply_text(f"Ошибка отправки: {e}")
            await asyncio.sleep(2)  # пауза между попытками

RESTART_FLAG = "bot_restarted.flag"

def load_sent_messages():
    if os.path.exists("sent_messages.json"):
        try:
            with open("sent_messages.json", "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_sent_messages(messages):
    with open("sent_messages.json", "w") as f:
        json.dump(messages, f)

sent_messages = load_sent_messages()  # [(message_id, timestamp)]

async def delete_old(update, context):
    chat_id = update.effective_chat.id
    now = time.time()
    deleted = 0
    for msg_id, ts in sent_messages[:]:
        if now - ts > 300:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                sent_messages.remove((msg_id, ts))
                deleted += 1
            except Exception:
                pass
    save_sent_messages(sent_messages)
    await update.message.reply_text(f"Удалено сообщений: {deleted}")

async def restart(update, context):
    await update.message.reply_text("Перезапуск скрипта...")
    # Очищаем vinted_items.txt только при /restart
    with open("vinted_items.txt", "w") as f:
        f.write("")
    # Флаг для перезапуска
    with open(RESTART_FLAG, "w") as f:
        f.write("1")
    os.execv(sys.executable, [sys.executable] + sys.argv)

async def status(update, context):
    await update.message.reply_text("Пашет пиздато!")

async def threadid(update, context):
    await update.message.reply_text(f"thread_id: {update.message.message_thread_id}")

async def send_log(update, context):
    log_file = "vinted_scanner.log"
    if os.path.exists(log_file):
        try:
            await update.message.reply_document(document=open(log_file, "rb"))
        except Exception as e:
            await update.message.reply_text(f"Ошибка отправки лога: {e}")
    else:
        await update.message.reply_text("Файл логов не найден.")

async def log(update, context):
    """Отправляет последние 10 строк из файла vinted_scanner.log"""
    log_file = "vinted_scanner.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Берем последние 10 строк
                last_lines = lines[-10:] if len(lines) >= 10 else lines
                log_text = "".join(last_lines)
                if log_text.strip():
                    # Обрезаем сообщение если оно слишком длинное (лимит Telegram ~4096 символов)
                    if len(log_text) > 4000:
                        log_text = "..." + log_text[-3900:]
                    await update.message.reply_text(f"<pre>{log_text}</pre>", parse_mode="HTML")
                else:
                    await update.message.reply_text("Файл логов пуст.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка чтения лога: {e}")
    else:
        await update.message.reply_text("Файл логов не найден.")

async def notify_start(application):
    await application.bot.send_message(chat_id=Config.telegram_chat_id, text="Бот запущен!")
    # НЕ отправляем все вещи из last_items.json при обычном запуске!
    if os.path.exists(RESTART_FLAG):
        await application.bot.send_message(chat_id=Config.telegram_chat_id, text="Бот перезапущен!")
        logging.info("=== VintedScanner script was restarted by Telegram command ===")
        os.remove(RESTART_FLAG)

# ВАЖНО: чтобы бот отправлял только 1 сообщение в секунду,
# в основном скрипте, где отправляются сообщения о новых вещах,
# используйте await asyncio.sleep(1) после каждой отправки!

def main():
    application = Application.builder().token(Config.telegram_bot_token).build()
    # application.add_handler(CommandHandler('refresh', refresh))  # удалено
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('delete_old', delete_old))
    application.add_handler(CommandHandler('threadid', threadid))
    application.add_handler(CommandHandler('restart', restart))
    application.add_handler(CommandHandler('send_log', send_log))  # команда для логов
    application.add_handler(CommandHandler('log', log))  # команда для последних 10 строк лога
    application.post_init = notify_start
    application.run_polling()

if __name__ == '__main__':
    main()
