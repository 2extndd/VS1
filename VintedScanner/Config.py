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

# Список топиков и параметров для поиска
topics = {
    "bags": {
        "thread_id": 718,
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '212366',
            'order': 'newest_first',
            'price_to': '45',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Rick Owens": {
        "thread_id": 843,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '145654',
            'order': 'newest_first',
            'price_to': '100',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Prada": {
        "thread_id": 747,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '2050,1231,82',
            'brand_ids': '3573',
            'order': 'newest_first',
            'price_to': '80',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Isaac Selam + Boris Bidjian": {
        "thread_id": 1229,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '393343,484649,1670540,978010',
            'order': 'newest_first',
            'price_to': '150',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Maison Margiela + mm6": {
        "thread_id": 1278,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '2050,1231,4,82,1187',
            'brand_ids': '639289',
            'order': 'newest_first',
            'price_to': '100',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Raf Simons + ALL": {
        "thread_id": 1351,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '4000998, 543679, 184436, 3090176',
            'order': 'newest_first',
            'price_to': '100',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Alyx": {
        "thread_id": 2308,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '79, 76, 82',
            'catalog_ids': '2050',
            'brand_ids': '1455187, 362587',
            'order': 'newest_first',
            'price_to': '60',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Misbhv": {
        "thread_id": 2308,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '79, 76',
            'brand_ids': '47515',
            'order': 'newest_first',
            'price_to': '60',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Y-3 and Y's": {
        "thread_id": 2394,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '117012, 6397426, 200474, 2887534',
            'order': 'newest_first',
            'price_to': '100',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Japanese Items and LUX": {
        "thread_id": 2959,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '83680, 349786, 919209, 36953, 319587, 505614, 373316, 11521, 344976, 75090',
            'order': 'newest_first',
            'price_to': '100',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Japanese Items and LUX #2 (типо кэрол, дорогая япония, анн демель и т.д.)": {
        "thread_id": 2959,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '24861, 344976, 17991, 724036, 51445',
            'order': 'newest_first',
            'price_to': '200',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Japanese Items and LUX #3 (том кром, дамир дома)": {
        "thread_id": 2959,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '',
            'brand_ids': '461946, 610205, 123118',
            'order': 'newest_first',
            'price_to': '50',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "CDG + Junya": {
        "thread_id": 2977,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '2050, 1231, 82',
            'brand_ids': '56974, 2318552, 235040, 5589958, 1330138, 4022828, 3753069',
            'order': 'newest_first',
            'price_to': '80',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "JPG + Helmut Lang": {
        "thread_id": 3412,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '2050, 1231, 82',
            'brand_ids': '4129, 71474, 47829',
            'order': 'newest_first',
            'price_to': '80',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    },
    "Dolce&Gabbana верх и аксессуары": {
        "thread_id": 3540,
        "query": {
            'page': '1',
            'per_page': '2',
            'search_text': '',
            'catalog_ids': '1206, 76, 79, 94, 19',
            'brand_ids': '1043, 5988099',
            'order': 'newest_first',
            'price_to': '80',
        },
        "exclude_catalog_ids": "26, 98, 146, 139"
    }
}
