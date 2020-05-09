import json
import datetime
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
    json_event = json.loads(request)

    return json_event


def get_place(place_id):
    """запро в кудаго-api на получение инфы о месте"""
    fields = "id,title,address,location,price"
    url = f"https://kudago.com/public-api/v1.4/places/{place_id}/" \
          f"?lang=&fields={fields}&expand="
    request = requests.get(url).text
    logging.debug(request)
    json_place = json.loads(request)

    return json_place


def find_events(categories, size, location):
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
          "&location=" + location + "&actual_since=" + \
          "&actual_until=" + "&is_free=" + \
          "&categories=" + categories + "&lon=&lat=&radius="
    request = requests.get(url).text
    logging.debug(request)
    json_events = json.loads(request)["results"]

    return json_events


def start_parsing(db):
    """заполняем базу данными"""
    categories_ev = "cinema"
    # ,stand-up,business-events,concert,festival,party,theater"
    """
    TODO
    не хочет сразу все категории, цикл тройной вложенности- больно
    на сл неделе что-нибудь придумаю
    """
    cities = {"msk", "spb"}
    size = "10"
    for city in cities:
        data = find_events(categories_ev, size, city)
        print(data)
        for event in data:
            try:
                place_data = get_place(event["place"]["id"])
                db.add_event(event["title"], event["location"]['slug'],
                             place_data["title"], event["site_url"],
                             event["dates"][0]['start'])
                #db.add_place(place_data["title"], place_data["address"],
                #             place_data["location"])
            except Exception as e:
                print(e)