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

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "Priority": "u=0, i",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

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
    # Явно приводим thread_id к int
    try:
        thread_id_int = int(thread_id)
    except Exception:
        thread_id_int = thread_id
    
    # Отправляем через GET параметры для URL изображений
    params = {
        "chat_id": Config.telegram_chat_id,
        "photo": item["image"],
        "caption": caption,
        "parse_mode": "HTML",
        "message_thread_id": thread_id_int
    }
    
    for attempt in range(max_retries):
        # Используем GET запрос для отправки через URL
        response = requests.get(url, params=params)
        logging.info(f"Telegram API GET call: status {response.status_code} for thread_id {thread_id_int}")
        if response.status_code == 200:
            logging.info(f"Telegram topic notification sent to thread {thread_id_int}")
            return True
        elif response.status_code == 400:
            # Проверяем если это ошибка "thread not found"
            try:
                error_data = response.json()
                error_desc = error_data.get("description", "").lower()
                logging.error(f"Telegram API 400 error: {error_desc}")
                if "message thread not found" in error_desc or "topic not found" in error_desc:
                    logging.warning(f"Thread {thread_id_int} not found - НЕ отправляем в main chat!")
                    return False  # НЕ отправляем в main chat!
                else:
                    logging.error(f"Other Telegram API error: {response.status_code}, {response.text}")
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
        session.post(Config.vinted_url, headers=headers, timeout=timeoutconnection)
    except Exception as e:
        logging.error(f"Error initializing session: {e}")
    cookies = session.cookies.get_dict()

    for topic_name, topic_info in Config.topics.items():
        try:
            logging.info(f"Scanning topic: {topic_name}")
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
            
            response = requests.get(f"{Config.vinted_url}/api/v2/catalog/items", params=params, cookies=cookies, headers=headers, timeout=timeoutconnection)
            
            # Проверяем статус ответа
            if response.status_code != 200:
                logging.error(f"Bad response status: {response.status_code}\nRequest params: {params}\nResponse text: {response.text[:500]}")
                continue
            
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
                        logging.info(f"NEW ITEM FOUND: {item_title} - sending to thread {thread_id}")
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
    while True:
        try:
            main()
        except KeyboardInterrupt:
            logging.info("Scanner stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}", exc_info=True)
        time.sleep(5)
