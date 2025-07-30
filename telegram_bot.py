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

# Функции для работы с отправленными сообщениями удалены (delete_old команда больше не актуальна)

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
                    await update.message.reply_text(f"```\n{log_text}\n```", parse_mode="Markdown")
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
    # CommandHandler('delete_old', delete_old) удален - команда больше не актуальна
    application.add_handler(CommandHandler('threadid', threadid))
    application.add_handler(CommandHandler('restart', restart))
    application.add_handler(CommandHandler('send_log', send_log))  # команда для логов
    application.add_handler(CommandHandler('log', log))  # команда для последних 10 строк лога
    application.post_init = notify_start
    # Включаем поддержку форум-топиков
    application.run_polling(allowed_updates=["message", "forum_topic_created", "forum_topic_closed", "forum_topic_reopened"])

if __name__ == '__main__':
    main()
