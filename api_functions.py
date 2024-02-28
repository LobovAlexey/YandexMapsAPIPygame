import requests
import map_utils


class Geocoder:
    api_server: str = "http://geocode-maps.yandex.ru/1.x/"
    apikey: str = "40d1649f-0493-4b70-98ba-98533de7710b"

    @staticmethod
    def get(toponym: str) -> dict | None:
        response = requests.get(url=Geocoder.api_server, params={
            'apikey': Geocoder.apikey,
            "geocode": toponym,
            "format": "json"
        })
        if not response:
            return
        response = response.json()

        toponym = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

        return {
            'll': toponym['Point']['pos'].replace(' ', ', '),
            'name': toponym['name'],
            'address': toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted'],
            'postal_code': toponym['metaDataProperty']['GeocoderMetaData']['Address'].get('postal_code', '')
        }


class StaticMaps:
    api_server: str = "http://static-maps.yandex.ru/1.x/"
    types: list = ['map', 'sat', 'sat,skl']

    @staticmethod
    def get_map(ll: str, spn: str, type_index: int, pt: str = None) -> requests.Response:
        params = {
            'll': ll,
            'spn': spn,
            'l': StaticMaps.types[type_index % 3]
        }
        if pt is not None:
            params['pt'] = f'{pt},comma'

        return requests.get(url=StaticMaps.api_server, params=params)


class Search:
    api_server: str = "https://search-maps.yandex.ru/v1/"
    apikey: str = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    @staticmethod
    def get_organisation(ll: str) -> str | None:  # ll
        text = Geocoder.get(ll)['address']
        response = requests.get(url=Search.api_server, params={
            'apikey': Search.apikey,
            'text': text,
            'lang': 'ru_RU',
            'type': 'biz'
        })
        if not response:
            return
        response = response.json()
        if len(response['features']) == 0:
            return
        response = response['features'][0]
        resp_ll = ','.join(map(str, response['geometry']['coordinates']))
        if map_utils.lonlat_distance(ll, resp_ll) > 50.0:
            return
        return resp_ll


def act_menu_dots():
    return


def act_x_mark():
    return
