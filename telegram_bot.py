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

async def safe_log(update, context):
    """Безопасная команда для просмотра лога без HTML парсинга"""
    log_file = "vinted_scanner.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                # Берем последние 10 строк
                last_lines = lines[-10:] if len(lines) >= 10 else lines
                log_text = "".join(last_lines)
                if log_text.strip():
                    # Убираем все потенциально опасные символы
                    safe_text = ""
                    for char in log_text:
                        if ord(char) < 128 and char.isprintable() or char in '\n\r\t':
                            safe_text += char
                        else:
                            safe_text += '?'
                    
                    # Разбиваем на части если слишком длинное
                    if len(safe_text) > 3500:
                        safe_text = "..." + safe_text[-3400:]
                    
                    await update.message.reply_text(f"📋 Лог (последние строки):\n\n{safe_text}")
                else:
                    await update.message.reply_text("📋 Файл логов пуст.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)[:200]}")
    else:
        await update.message.reply_text("❌ Файл логов не найден.")

async def status(update, context):
    """Улучшенная команда статуса с дополнительной информацией"""
    try:
        # Проверяем файлы
        log_exists = "✅" if os.path.exists("vinted_scanner.log") else "❌"
        items_exists = "✅" if os.path.exists("vinted_items.txt") else "❌"
        config_exists = "✅" if os.path.exists("Config.py") else "❌"
        
        # Считаем количество обработанных элементов
        items_count = 0
        if os.path.exists("vinted_items.txt"):
            try:
                with open("vinted_items.txt", "r") as f:
                    items_count = len(f.readlines())
            except:
                items_count = "?"
        
        status_text = f"""🤖 **VintedScanner Status**

📁 **Файлы:**
• Лог: {log_exists}
• База элементов: {items_exists} 
• Конфиг: {config_exists}

📊 **Статистика:**
• Обработано элементов: {items_count}

⚡ **Статус:** Пашет пиздато!"""
        
        await update.message.reply_text(status_text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Пашет пиздато! (статус: {e})")

async def threadid(update, context):
    await update.message.reply_text(f"thread_id: {update.message.message_thread_id}")

async def send_log(update, context):
    log_file = "vinted_scanner.log"
    if os.path.exists(log_file):
        try:
            # Проверяем размер файла
            file_size = os.path.getsize(log_file)
            if file_size > 50 * 1024 * 1024:  # 50MB лимит Telegram
                await update.message.reply_text("❌ Файл лога слишком большой (>50MB). Используйте /log для последних строк.")
                return
            
            with open(log_file, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename="vinted_scanner.log",
                    caption="📄 Полный файл лога VintedScanner"
                )
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка отправки лога: {e}")
            # Попробуем отправить как текст
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if len(content) > 4000:
                        content = "...последние символы...\n" + content[-3500:]
                    await update.message.reply_text(f"Лог как текст:\n```\n{content}\n```", parse_mode="Markdown")
            except Exception as e2:
                await update.message.reply_text(f"❌ Не удалось отправить лог: {e2}")
    else:
        await update.message.reply_text("❌ Файл логов не найден.")

async def log(update, context):
    """Отправляет последние 10 строк из файла vinted_scanner.log"""
    log_file = "vinted_scanner.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                # Берем последние 10 строк
                last_lines = lines[-10:] if len(lines) >= 10 else lines
                log_text = "".join(last_lines)
                if log_text.strip():
                    # Очищаем от HTML тегов и специальных символов
                    import re
                    log_text = re.sub(r'<[^>]+>', '', log_text)  # Удаляем HTML теги
                    log_text = log_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    # Обрезаем сообщение если оно слишком длинное (лимит Telegram ~4096 символов)
                    if len(log_text) > 3500:  # Оставляем запас для тегов
                        log_text = "..." + log_text[-3400:]
                    
                    # Отправляем как обычный текст без HTML парсинга
                    await update.message.reply_text(f"📋 **Последние строки лога:**\n\n```\n{log_text}\n```", parse_mode="Markdown")
                else:
                    await update.message.reply_text("📋 Файл логов пуст.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка чтения лога: {e}")
            # Попробуем отправить как обычный текст
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    last_lines = lines[-5:] if len(lines) >= 5 else lines  # Берем меньше строк
                    log_text = "".join(last_lines)
                    if log_text.strip():
                        # Убираем все специальные символы
                        safe_text = ''.join(char for char in log_text if ord(char) < 128)
                        await update.message.reply_text(f"Лог (упрощенный):\n{safe_text}")
            except Exception as e2:
                await update.message.reply_text(f"❌ Критическая ошибка чтения лога: {e2}")
    else:
        await update.message.reply_text("❌ Файл логов не найден.")

async def notify_start(application):
    await application.bot.send_message(chat_id=Config.telegram_chat_id, text="Бот запущен!")
    # НЕ отправляем все вещи из last_items.json при обычном запуске!
    if os.path.exists(RESTART_FLAG):
        await application.bot.send_message(chat_id=Config.telegram_chat_id, text="Бот перезапущен!")
        logging.info("=== VintedScanner script was restarted by Telegram command ===")
        os.remove(RESTART_FLAG)

async def help_command(update, context):
    """Команда помощи со списком всех команд"""
    help_text = """🤖 **VintedScanner Bot - Команды**

📊 **Основные:**
/status - Статус бота и статистика
/threadid - Показать ID текущего топика

📋 **Логи:**
/log - Последние 10 строк лога (безопасно)
/safe_log - Альтернативный просмотр лога
/send_log - Отправить файл лога

⚙️ **Управление:**
/restart - Перезапустить сканер
/help - Показать эту справку

💡 **Подсказки:**
• Используйте /safe_log если /log не работает
• /restart очищает базу обработанных элементов
• Все команды работают только в настроенном чате"""

    await update.message.reply_text(help_text, parse_mode="Markdown")

async def start_command(update, context):
    """Команда /start"""
    start_text = """🚀 **VintedScanner Bot запущен!**

Я автоматически мониторю Vinted и отправляю уведомления о новых товарах.

Используйте /help для списка команд или /status для проверки работы."""
    
    await update.message.reply_text(start_text, parse_mode="Markdown")

# ВАЖНО: чтобы бот отправлял только 1 сообщение в секунду,
# в основном скрипте, где отправляются сообщения о новых вещах,
# используйте await asyncio.sleep(1) после каждой отправки!

def main():
    application = Application.builder().token(Config.telegram_bot_token).build()
    
    # Основные команды
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('threadid', threadid))
    
    # Команды логирования
    application.add_handler(CommandHandler('log', log))  
    application.add_handler(CommandHandler('safe_log', safe_log))  
    application.add_handler(CommandHandler('send_log', send_log))  
    
    # Управление
    application.add_handler(CommandHandler('restart', restart))
    
    # application.add_handler(CommandHandler('refresh', refresh))  # удалено
    # CommandHandler('delete_old', delete_old) удален - команда больше не актуальна
    
    application.post_init = notify_start
    application.run_polling()

if __name__ == '__main__':
    main()
