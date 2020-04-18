import json
import datetime
import requests
import logging


def find_events(categories):
    """Функция кидает запрос в кудаго-api на получение списка событий

    на вход строка - категории 'concert,stand-up.....'
    на выходе список json с полями {id,dates,title,place,description,
                                    location,price,is_free,site_url}
    что еще в описание добавить?
     ☻/
    /▌
    / \
    """
    fields = "id,dates,title,place,description,location,price," \
             "is_free,site_url"
    url = "https://kudago.com/public-api/v1.4/events/?lang=&fields=" \
          + fields + "&expand=&order_by=" + "&text_format=" \
          + "&ids=&page_size=5" + "&location=" + "msk" \
          + "&actual_since=" + "&actual_until=" + "&is_free=" + \
          "&categories=" + categories + "&lon=&lat=&radius="
    request = requests.get(url).text
    logging.debug(request)
    json_events = json.loads(request)["results"]

    return json_events


def get_event(event_id):
    """Функция кидает запрос в кудаго-api на получение инфы о событии

    на вход строка - id события в базе кудаго
    на выходе json с полями {id,dates,title,place,description,
                             location,price,is_free,site_url}
    """
    fields = "id,dates,title,place,description,location,price," \
             "is_free,site_url"
    url = f"https://kudago.com/public-api/v1.4/events/{event_id}/?" \
          f"lang=&fields{fields}=&expand="
    request = requests.get(url).text
    logging.debug(request)
    json_event = json.loads(request)["results"]

    return json_event
