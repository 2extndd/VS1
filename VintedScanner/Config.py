# SMTP Settings for e-mail notification
smtp_username = ""
smtp_psw = ""
smtp_server = ""
smtp_toaddrs = ["User <example@example.com>"]

# Slack WebHook for notification
slack_webhook_url = ""

# Telegram Token and ChatID for notification
telegram_bot_token = "8103604647:AAFoZVtAQxg5prugi_u2-YAkXFnf3WRTM-Q"
telegram_chat_id = "-1002721134127"

# Vinted URL: change the TLD according to your country (.fr, .es, etc.)
vinted_url = "https://www.vinted.de"

# Vinted queries for research
# "page", "per_page" and "order" you may not edit them
# "search_text" is the free search field, this field may be empty if you wish to search for the entire brand.
# "catalog_ids" is the category in which to eventually search, if the field is empty it will search in all categories. Vinted assigns a numeric ID to each category, e.g. 2996 is the ID for e-Book Reader
# "brand_ids" if you want to search by brand. Vinted assigns a numeric ID to each brand, e.g. 417 is the ID for Louis Vuitton
# "order" you can change it to relevance, newest_first, price_high_to_low, price_low_to_high


# Список топиков и параметров для поиска
topics = {
    "bags": {
        "thread_id":718,  # ID топика для сумок
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '212366',
            'order': 'newest_first',
            'price_to': '40',
        }
    },
    "Rick Owens": {
        "thread_id":843,  # ID топика для Rick Owens
        "query": {
            'page': '1',
            'per_page': '10',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '145654',
            'order': 'newest_first',
            'price_to': '100',
        }
    },
    "Prada": {
        "thread_id":747,  # ID топика для Prada
        "query": {
            'page': '1',
            'per_page': '10',
            'search_text': '',
            'catalog_ids': '2050,1231,4,16',
            'brand_ids': '3573',
            'order': 'newest_first',
            'price_to': '80',
        }
    },

    "Isaac Selam + Boris Bidjian": {
        "thread_id":1229,  # ID топика для Isaac Selam + Boris Bidjian
        "query": {
            'page': '1',
            'per_page': '10',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '393343,484649,1670540,978010',
            'order': 'newest_first',
            'price_to': '150',
        }
    },

    "Maison Margiela + mm6": {
        "thread_id":1278,  # ID топика для Maison Margiela + mm6
        "query": {
            'page': '1',
            'per_page': '10',
            'search_text': '',
            'catalog_ids': '2050,1231,4,82,1187', #1187 - женские акссесы, 82 - мужские аксессуары, 
            'brand_ids': '639289,,
            'order': 'newest_first',
            'price_to': '100',
        }
    },



    # Добавьте другие типы вещей и топики по аналогии
}
