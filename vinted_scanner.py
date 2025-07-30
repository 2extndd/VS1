#!/usr/bin/env python3
import sys
import time
import json
import Config
import smtplib
import logging
import requests
import email.utils
import os
import random
from datetime import datetime
from email.message import EmailMessage
from logging.handlers import RotatingFileHandler
import subprocess

RESTART_FLAG = "bot_restarted.flag"

# Настройка логирования - вывод в файл И в консоль для RailWay
file_handler = RotatingFileHandler("vinted_scanner.log", maxBytes=5000000, backupCount=5)
console_handler = logging.StreamHandler(sys.stdout)

# Форматирование для обоих обработчиков
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)10s():%(lineno)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Настройка корневого логгера
logging.basicConfig(handlers=[file_handler, console_handler],
                    format="%(asctime)s - %(filename)s - %(funcName)10s():%(lineno)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

timeoutconnection = 30
list_analyzed_items = []

# Список различных User-Agent для ротации
user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
]

def get_random_headers():
    """Возвращает случайные headers для запроса"""
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-GPC": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Referer": f"{Config.vinted_url}/",
    }

def random_delay(min_seconds=0.5, max_seconds=2):
    """Быстрая случайная задержка между запросами"""
    delay = random.uniform(min_seconds, max_seconds)
    logging.info(f"Quick delay: {delay:.1f}s")
    time.sleep(delay)

async def notify_ban_status(ban_duration, consecutive_errors, is_recovering=False):
    """Отправляет уведомление о бане в Telegram чат"""
    try:
        if is_recovering:
            status_text = f"🔄 **Восстановление после блокировки**\n\n"
            status_text += f"• Возобновляю сканирование\n"
            status_text += f"• Предыдущих ошибок: {consecutive_errors}\n"
            status_text += f"• Время паузы было: {ban_duration}с"
        else:
            status_text = f"🚫 **IP ЗАБЛОКИРОВАН VINTED**\n\n"
            status_text += f"• Consecutive 403 errors: {consecutive_errors}\n"
            status_text += f"• Пауза на: {ban_duration} секунд\n"
            status_text += f"• Автовосстановление через: {ban_duration}с\n"
            status_text += f"• Время блокировки: {datetime.now().strftime('%H:%M:%S')}"
        
        import requests
        url = f"https://api.telegram.org/bot{Config.telegram_bot_token}/sendMessage"
        requests.post(url, data={
            "chat_id": Config.telegram_chat_id,
            "text": status_text,
            "parse_mode": "Markdown"
        }, timeout=10)
        
        logging.info(f"Ban status notification sent: {'recovering' if is_recovering else 'blocked'}")
    except Exception as e:
        logging.error(f"Failed to send ban notification: {e}")

def adaptive_ban_recovery(consecutive_errors):
    """Адаптивная система восстановления после банов"""
    if consecutive_errors <= 2:
        return 15  # Короткая пауза для легких блокировок
    elif consecutive_errors <= 5:
        return 45  # Средняя пауза
    elif consecutive_errors <= 10:
        return 120  # Длинная пауза
    else:
        return 300  # Очень длинная пауза для серьезных блокировок

headers = get_random_headers()

def load_analyzed_item():
    list_analyzed_items.clear()
    try:
        with open("vinted_items.txt", "r", errors="ignore") as f:
            for line in f:
                if line:
                    list_analyzed_items.append(line.rstrip())
    except IOError as e:
        logging.error(e, exc_info=True)
        sys.exit()

def save_analyzed_item(hash):
    try:
        with open("vinted_items.txt", "a") as f:
            f.write(str(hash) + "\n")
    except IOError as e:
        logging.error(e, exc_info=True)
        sys.exit()

def send_email(item_title, item_price, item_url, item_image, item_size=""):
    try:
        msg = EmailMessage()
        msg["To"] = Config.smtp_toaddrs
        msg["From"] = email.utils.formataddr(("Vinted Scanner", Config.smtp_username))
        msg["Subject"] = "Vinted Scanner - New Item"
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid()
        body = f"{item_title}\n{item_price}"
        if item_size:
            body += f", SIZE: {item_size}"
        body += f"\n🔗 {item_url}\n📷 {item_image}"
        msg.set_content(body)
        with smtplib.SMTP(Config.smtp_server, 587) as smtpserver:
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo()
            smtpserver.login(Config.smtp_username, Config.smtp_psw)
            smtpserver.send_message(msg)
            logging.info("E-mail sent")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error sending email: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"Error sending email: {e}", exc_info=True)

def send_slack_message(item_title, item_price, item_url, item_image, item_size=""):
    webhook_url = Config.slack_webhook_url 
    message = f"*{item_title}*\n🏷️ {item_price}"
    if item_size:
        message += f", SIZE: {item_size}"
    message += f"\n🔗 {item_url}\n📷 {item_image}"
    slack_data = {"text": message}
    try:
        response = requests.post(
            webhook_url, 
            data=json.dumps(slack_data),
            headers={"Content-Type": "application/json"},
            timeout=timeoutconnection
        )
        if response.status_code != 200:
            logging.error(f"Slack notification failed: {response.status_code}, {response.text}")
        else:
            logging.info("Slack notification sent")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending Slack message: {e}")

def send_telegram_topic_message(item, thread_id, max_retries=5):
    """
    Отправляет уведомление о новом товаре в Telegram топик с автоматическим fallback в общий чат
    
    Args:
        item: словарь с данными товара (title, price, url, image, size)
        thread_id: ID топика в Telegram
        max_retries: максимальное количество попыток отправки
    """
    caption = f"<b>{item['title']}</b>\n🏷️ {item['price']}"
    if item.get("size"):
        caption += f", SIZE: {item['size']}"
    caption += f"\n🔗 {item['url']}"
    
    url = f"https://api.telegram.org/bot{Config.telegram_bot_token}/sendPhoto"
    params = {
        "chat_id": Config.telegram_chat_id,
        "photo": item["image"],
        "caption": caption,
        "parse_mode": "HTML",
        "message_thread_id": thread_id
    }
    
    for attempt in range(max_retries):
        response = requests.post(url, data=params)
        if response.status_code == 200:
            logging.info(f"Telegram topic notification sent to thread {thread_id}")
            return True
        elif response.status_code == 400:
            # Проверяем если это ошибка "thread not found"
            try:
                error_data = response.json()
                if "message thread not found" in error_data.get("description", "").lower():
                    logging.warning(f"Thread {thread_id} not found, sending to main chat")
                    # Отправляем в основной чат без thread_id
                    params_main = params.copy()
                    del params_main["message_thread_id"]
                    params_main["caption"] = caption
                    
                    response_main = requests.post(url, data=params_main)
                    if response_main.status_code == 200:
                        logging.info(f"Message sent to main chat instead of thread {thread_id}")
                        return True
                    else:
                        logging.error(f"Failed to send to main chat: {response_main.status_code}, {response_main.text}")
                        break
                else:
                    logging.error(f"Telegram API error: {response.status_code}, {response.text}")
                    break
            except Exception as e:
                logging.error(f"Error parsing response: {e}")
                break
        elif response.status_code == 429:
            try:
                retry_after = response.json().get("parameters", {}).get("retry_after", 30)
            except Exception:
                retry_after = 30
            warn_text = f"⚠️ ВНИМАНИЕ: Telegram API отправил Too Many Requests! Бот на паузе {retry_after} сек.\n" \
                        f"Строка из лога:\n429 Too Many Requests. Waiting {retry_after} seconds before retry..."
            # Отправляем предупреждение в чат
            try:
                requests.post(
                    f"https://api.telegram.org/bot{Config.telegram_bot_token}/sendMessage",
                    data={
                        "chat_id": Config.telegram_chat_id,
                        "text": warn_text
                    }
                )
            except Exception as e:
                logging.error(f"Ошибка отправки предупреждения в чат: {e}")
            logging.warning(f"429 Too Many Requests. Waiting {retry_after} seconds before retry...")
            time.sleep(retry_after)
        else:
            logging.error(f"Telegram topic notification failed: {response.status_code}, {response.text}")
            break
        time.sleep(1)
    return False

def handle_restart_flag():
    if os.path.exists(RESTART_FLAG):
        logging.info("=== VintedScanner script was restarted by Telegram command ===")
        os.remove(RESTART_FLAG)
        # НЕ отправляем старые вещи после перезапуска!

def scan_all_topics():
    load_analyzed_item()
    session = requests.Session()
    try:
        # Используем случайные headers
        init_headers = get_random_headers()
        session.get(Config.vinted_url, headers=init_headers, timeout=timeoutconnection)
        random_delay(0.5, 1)  # Короткая пауза после инициализации
    except Exception as e:
        logging.error(f"Error initializing session: {e}")
    
    cookies = session.cookies.get_dict()
    consecutive_403_errors = 0
    max_403_errors = 3
    last_ban_notification = 0

    for topic_name, topic_info in Config.topics.items():
        try:
            logging.info(f"🔍 Scanning topic: {topic_name}")
            
            # Проверяем количество 403 ошибок подряд
            if consecutive_403_errors >= max_403_errors:
                ban_duration = adaptive_ban_recovery(consecutive_403_errors)
                
                # Отправляем уведомление о бане (не чаще раз в минуту)
                current_time = time.time()
                if current_time - last_ban_notification > 60:
                    try:
                        import asyncio
                        asyncio.run(notify_ban_status(ban_duration, consecutive_403_errors, False))
                        last_ban_notification = current_time
                    except Exception as e:
                        logging.error(f"Failed to notify ban: {e}")
                
                logging.warning(f"🚫 IP blocked! Taking {ban_duration}s break (errors: {consecutive_403_errors})")
                time.sleep(ban_duration)
                
                # Уведомление о восстановлении
                try:
                    import asyncio
                    asyncio.run(notify_ban_status(ban_duration, consecutive_403_errors, True))
                except Exception as e:
                    logging.error(f"Failed to notify recovery: {e}")
                
                consecutive_403_errors = 0
                logging.info(f"🔄 Resuming scanning after {ban_duration}s break")
            
            # Быстрая задержка между топиками для скорости
            random_delay(0.5, 1.5)
            
            params = topic_info["query"].copy()
            # фильтруем catalog_ids
            catalog_ids = params.get("catalog_ids", "")
            exclude_ids = topic_info.get("exclude_catalog_ids", "")
            if catalog_ids:
                ids = [x.strip() for x in catalog_ids.split(",") if x.strip()]
                exclude = [x.strip() for x in exclude_ids.split(",") if x.strip()]
                filtered = [x for x in ids if x not in exclude]
                params["catalog_ids"] = ",".join(filtered)
            thread_id = topic_info["thread_id"]
            data = None
            
            # Используем свежие headers для каждого запроса
            request_headers = get_random_headers()
            response = requests.get(f"{Config.vinted_url}/api/v2/catalog/items", 
                                  params=params, 
                                  cookies=cookies, 
                                  headers=request_headers, 
                                  timeout=timeoutconnection)
            
            # Проверяем статус ответа
            if response.status_code == 403:
                consecutive_403_errors += 1
                logging.warning(f"⚠️ 403 Forbidden #{consecutive_403_errors} - IP rate limited")
                continue
            elif response.status_code != 200:
                consecutive_403_errors = 0  # Сбрасываем счетчик при других ошибках
                logging.error(f"❌ Bad response status: {response.status_code}")
                continue
            else:
                # Успешный запрос - сбрасываем счетчик ошибок
                if consecutive_403_errors > 0:
                    logging.info(f"✅ Request successful after {consecutive_403_errors} errors - recovery complete")
                consecutive_403_errors = 0
            
            # Проверяем content-type
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logging.error(f"Non-JSON response received\nContent-Type: {content_type}\nStatus: {response.status_code}\nParams: {params}\nResponse: {response.text[:500]}")
                continue
            
            # Проверяем что ответ не пустой
            if not response.text.strip():
                logging.error(f"Empty response received\nStatus: {response.status_code}\nParams: {params}")
                continue
            
            # Пробуем декодировать JSON
            try:
                data = response.json()
            except Exception as json_error:
                logging.error(f"JSONDecodeError: {json_error}\nStatus code: {response.status_code}\nContent-Type: {content_type}\nRequest params: {params}\nResponse text: {response.text[:500]}", exc_info=True)
                continue

            # Проверяем что data получен и валиден
            if not data:
                logging.error(f"No data received for params: {params}")
                continue
                
            if not isinstance(data, dict):
                logging.error(f"Invalid data format (not dict): {type(data)}\nParams: {params}")
                continue
                
            if "items" not in data:
                logging.error(f"No 'items' field in response\nData keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}\nParams: {params}")
                continue

            if data and "items" in data:
                exclude_ids = topic_info.get("exclude_catalog_ids", "")
                exclude_set = set(str(x.strip()) for x in exclude_ids.split(",") if x.strip())
                for item in data["items"]:
                    catalog_id = item.get("catalog_id", "")
                    if catalog_id != "":
                        if str(catalog_id) in exclude_set:
                            continue
                    item_id = str(item["id"])
                    item_title = item["title"]
                    item_url = item["url"]
                    item_price = f'{item["price"]["amount"]} {item["price"]["currency_code"]}'
                    item_image = item["photo"]["full_size_url"]
                    # Получаем размер, если есть
                    item_size = ""
                    if "size_title" in item and item["size_title"]:
                        item_size = item["size_title"]
                    elif "size" in item and item["size"]:
                        item_size = item["size"]
                    # Отправляем только новые вещи
                    if item_id not in list_analyzed_items:
                        if Config.smtp_username and Config.smtp_server:
                            send_email(item_title, item_price, item_url, item_image, item_size)
                            time.sleep(1)
                        if Config.slack_webhook_url:
                            send_slack_message(item_title, item_price, item_url, item_image, item_size)
                            time.sleep(1)
                        if Config.telegram_bot_token and Config.telegram_chat_id:
                            send_telegram_topic_message({
                                "image": item_image,
                                "title": item_title,
                                "price": item_price,
                                "url": item_url,
                                "size": item_size
                            }, thread_id)
                            time.sleep(1)
                        list_analyzed_items.append(item_id)
                        save_analyzed_item(item_id)
        
        except requests.exceptions.Timeout:
            logging.error(f"Request timeout for topic '{topic_name}' with params: {params}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for topic '{topic_name}': {e}\nParams: {params}", exc_info=True)
        except Exception as topic_error:
            logging.error(f"Error processing topic '{topic_name}': {topic_error}", exc_info=True)

def main():
    handle_restart_flag()
    try:
        scan_all_topics()
    except Exception as e:
        logging.error(f"Error in scan_all_topics: {e}", exc_info=True)

if __name__ == "__main__":
    subprocess.Popen(["python3", "telegram_bot.py"])
    
    # Отправляем уведомление о запуске
    try:
        import requests
        url = f"https://api.telegram.org/bot{Config.telegram_bot_token}/sendMessage"
        requests.post(url, data={
            "chat_id": Config.telegram_chat_id,
            "text": f"🚀 **VintedScanner запущен!**\n\n⚡ Быстрый режим: проверки каждые 5-10 секунд\n🛡️ Авто-восстановление после банов\n📊 19 топиков активно\n\n🕐 Запуск: {datetime.now().strftime('%H:%M:%S')}",
            "parse_mode": "Markdown"
        }, timeout=10)
    except:
        pass
    
    while True:
        try:
            main()
        except KeyboardInterrupt:
            logging.info("Scanner stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}", exc_info=True)
        
        # БЫСТРЫЙ режим: 5-10 секунд между циклами для 60 проверок в час
        quick_delay = random.randint(5, 10)
        logging.info(f"⚡ Next scan in {quick_delay}s (Quick mode: 60 checks/hour)")
        time.sleep(quick_delay)
