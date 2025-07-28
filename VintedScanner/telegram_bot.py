import sys
import os
import logging
from telegram.ext import Application, CommandHandler
import Config
import json
import time


RESTART_FLAG = "bot_restarted.flag"

def get_last_items():
    try:
        with open("last_items.json", "r") as f:
            return json.load(f)
    except Exception:
        return []

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

async def refresh(update, context):
    items = get_last_items()
    for item in items:
        msg = await update.message.reply_photo(
            photo=item["image"],
            caption=f"{item['title']}\n{item['price']}\n{item['url']}"
        )
        sent_messages.append((msg.message_id, time.time()))
    save_sent_messages(sent_messages)

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
    # Очищаем vinted_items.txt
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

async def notify_start(application):
    await application.bot.send_message(chat_id=Config.telegram_chat_id, text="Бот запущен!")
    # После рестарта отправляем все вещи из last_items.json
    items = get_last_items()
    for item in items:
        await application.bot.send_photo(
            chat_id=Config.telegram_chat_id,
            photo=item["image"],
            caption=f"{item['title']}\n{item['price']}\n{item['url']}"
        )
    if os.path.exists(RESTART_FLAG):
        await application.bot.send_message(chat_id=Config.telegram_chat_id, text="Бот перезапущен!")
        logging.info("=== VintedScanner script was restarted by Telegram command ===")
        os.remove(RESTART_FLAG)

def main():
    application = Application.builder().token(Config.telegram_bot_token).build()
    application.add_handler(CommandHandler('refresh', refresh))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('delete_old', delete_old))
    application.add_handler(CommandHandler('threadid', threadid))
    application.add_handler(CommandHandler('restart', restart))
    application.post_init = notify_start
    application.run_polling()

if __name__ == '__main__':
    main()
