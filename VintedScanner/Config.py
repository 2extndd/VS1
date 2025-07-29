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
            'price_to': '45',
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
            'catalog_ids': '2050,1231,82',
            'brand_ids': '3573',
            'order': 'newest_first',
            'price_to': '80',
        }
    },

    "Isaac Selam + Boris Bidjian": {
        "thread_id":1229,  # ID топика для Isaac Selam + Boris Bidjian
        "query": {
            'page': '1',
            'per_page': '7',
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
            'per_page': '7',
            'search_text': '',
            'catalog_ids': '2050,1231,4,82,1187', #1187 - женские акссесы, 82 - мужские аксессуары, 4 - женские вещи, 1231 - мужские обувь
            'brand_ids': '639289',
            'order': 'newest_first',
            'price_to': '100',
        }
    },

    "Raf Simons + ALL": {
        "thread_id":1351,  # ID топика для Raf Simons + ALL
        "query": {
            'page': '1',
            'per_page': '7',
            'search_text': '',
            'catalog_ids': '', 
            'brand_ids': '4000998, 543679, 184436, 3090176',
            'order': 'newest_first',
            'price_to': '100',
        }
    },


    "Alyx": {
        "thread_id":2308,  # ID топика для Alyx
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '79, 76, 82',
            'catalog_ids': '2050', 
            'brand_ids': '1455187, 362587',
            'order': 'newest_first',
            'price_to': '60',
        }
    },

    "Misbhv": {
        "thread_id":2308,  # ID топика для Alyx
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '79, 76', 
            'brand_ids': '47515',
            'order': 'newest_first',
            'price_to': '60',
        }
    },

    

    "Y-3 and Y's": {
        "thread_id":2394,  # ID топика для Y-3 and Y's
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '', 
            'brand_ids': '117012, 6397426, 200474, 2887534',
            'order': 'newest_first',
            'price_to': '100',
        }
    },
    
    "Japanese Items and LUX": {
        "thread_id":2959,  # ID топика для Japanese Items and LUX
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '', 
            'brand_ids': '83680, 349786, 919209,  36953,  319587, 505614, 373316, 11521,  344976, 75090 ',
            'order': 'newest_first',
            'price_to': '100',
        }
    },

        "Japanese Items and LUX #2 (типо кэрол, дорогая япония, анн демель и т.д.)": {
        "thread_id":2959,  # ID топика для Japanese Items and LUX
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '', 
            'brand_ids': '24861, 344976, 17991, 724036, 51445, ',
            'order': 'newest_first',
            'price_to': '200',
        }
    },


        "Japanese Items and LUX #3 (том кром, дамир дома)": {
        "thread_id":2959,  # ID топика для Japanese Items and LUX
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '', 
            'brand_ids': '461946, 610205, 123118',
            'order': 'newest_first',
            'price_to': '50',
        }
    },

    
            "CDG + Junya": {
        "thread_id":2977,  # ID топика для CDG + Junya
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '2050, 1231, 82', 
            'brand_ids': '56974, 2318552, 235040, 5589958, 1330138, 4022828, 3753069',
            'order': 'newest_first',
            'price_to': '80',
        }
    },

            "JPG + Helmut Lang": {
        "thread_id":3412,  # ID топика для JPG + Helmut Lang
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '2050, 1231, 82', 
            'brand_ids': '4129, 71474, 47829',
            'order': 'newest_first',
            'price_to': '80',
        }
    },

            "Dolce&Gabbana верх и аксессуары": {
        "thread_id":3412,  # ID топика для JPG + Helmut Lang
        "query": {
            'page': '1',
            'per_page': '5',
            'search_text': '',
            'catalog_ids': '1206, 76, 79, 94, 19', 
            'brand_ids': '1043, 5988099',
            'order': 'newest_first',
            'price_to': '80',
        }
    },

    



}
