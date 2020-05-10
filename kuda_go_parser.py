import json
from datetime import datetime, timedelta
import requests
import logging
from pg_api import PgAPI


def get_event(event_id):
    """Функция кидает запрос в кудаго-api на инфу о событии

    на вход строка - id события в базе кудаго
    на выходе json с полями {id,dates,title,place,description,
                             location,price,is_free,site_url}
    """
    fields = "id,dates,title,place,description,location,price," \
             "is_free,site_url"
    url = f"https://kudago.com/public-api/v1.4/events/" \
          f"{event_id}/?lang=&fields{fields}=&expand="
    request = requests.get(url).text
    logging.debug(request)
    json_event = json.loads(request).get("results", None)

    return json_event


def get_place(place_id):
    """запро в кудаго-api на получение инфы о месте"""
    fields = "id,title,address,location,price"
    url = f"https://kudago.com/public-api/v1.4/places/{place_id}/" \
          f"?lang=&fields={fields}&expand="
    request = requests.get(url).text
    logging.debug(request)
    print(request)
    json_place = json.loads(request).get("results", None)

    return json_place


def find_events(categories, size, location, time_start, time_end):
    """Функция кидает запрос в кудаго-api на получение списка
             событий

            на вход строка - категории 'concert,stand-up.....'
            на выходе список json с  {id,dates,title,place,
            description,location,price,is_free,site_url}
             ☻/
            /▌
            / \
            """
    fields = "id,dates,title,place,location,price," \
             "is_free,site_url"
    url = "https://kudago.com/public-api/v1.4/events/?lang=&" \
          "fields=" + fields + "&expand=&order_by=" + \
          "&text_format=" + "&ids=&page_size=" + size + \
          "&location=" + location + "&actual_since=" + str(time_start) + \
          "&actual_until=" + str(time_end) + "&is_free=" + \
          "&categories=" + categories + "&lon=&lat=&radius="
    request = requests.get(url).text
    logging.debug(request)
    print(request)
    json_events = json.loads(request).get("results", None)

    return json_events


def start_parsing(db):
    """заполняем базу данными"""
    categories_ev = [{"tag": "cinema", "name": "Кино"},
                     {"tag": "concert", "name": "Концерты"},
                     {"tag": "exhibition", "name": "Выставки"},
                     {"tag": "festival", "name": "Фестивали"},
                     {"tag": "stand-up", "name": "Стенд-ап"},
                     {"tag": "party", "name": "Вечеринки"}]

    cities = [
        {'name': 'Москва',
         'tag': 'msk'},
        {'name': 'Санкт-петербург',
         'tag': 'spb'}
    ]

    size = "10"
    time_start = datetime.now().timestamp()
    time_end = datetime.now() + timedelta(days=10)
    time_end = time_end.timestamp()
    for city in cities:
        db.add_city(**city)

        for category in categories_ev:
            logging.debug("Finding category", category['name'])
            data = find_events(category["tag"], size,
                               city['tag'], time_start, time_end)
            if not data:
                logging.debug("No data was found for {} category".format(category['name']))
                continue
            for event in data:
                # Но вообще надо сделать нормально выбор категорий
                # category = {'name': "Кино", 'tag': 'cinema'}
                if event['place']:
                    place_data = get_place(event["place"]["id"])
                else:
                    place_data = None
                db.add_event(name=event["title"],
                             category=category,
                             finish_datetime=datetime.fromtimestamp(
                                 event["dates"][0]['end']),
                             start_datetime=datetime.fromtimestamp(
                                 event["dates"][0]['start']),
                             city_name=city['name'],
                             place_name=place_data["title"] if place_data
                             else None,
                             url=event["site_url"])
                if place_data:
                    db.add_place(name=(place_data["title"]),
                                 address=place_data["address"],
                                 city_name=city['name'])
