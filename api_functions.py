import requests
import math
import pygame
import os

import api_window


def lonlat_distance(a: str, b: str) -> float:  # в метрах
    if type(a) is str:
        a = [float(i.strip()) for i in a.split(',')]
    if type(b) is str:
        b = [float(i.strip()) for i in b.split(',')]
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_latitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_latitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


class Geocoder:
    api_server: str = "http://geocode-maps.yandex.ru/1.x/"
    apikey: str = "40d1649f-0493-4b70-98ba-98533de7710b"

    @staticmethod
    def get(toponym: str) -> dict:
        response = requests.get(url=Geocoder.api_server, params={
            'apikey': Geocoder.apikey,
            "geocode": toponym,
            "format": "json"
        })
        if not response:
            return {}
        response = response.json()

        toponym = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

        return {
            'll': toponym['Point']['pos'].replace(' ', ','),
            'name': toponym['name'],
            'address': toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted'],
            'postal_code': toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
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


def to_surface(content: bytes) -> pygame.Surface:
    map_file_name = '_map.png'
    with open(map_file_name, 'wb') as map_file:
        map_file.write(content)
    _surface = pygame.image.load(map_file_name)
    os.remove(map_file_name)
    return _surface


class Search:
    api_server: str = "https://search-maps.yandex.ru/v1/"
    apikey: str = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    @staticmethod
    def get_organisation(ll: str) -> str:  # ll
        text = Geocoder.get(ll)['address']
        response = requests.get(url=Search.api_server, params={
            'apikey': Search.apikey,
            'text': text,
            'lang': 'ru_RU',
            'type': 'biz'
        })
        if not response:
            return ''
        response = response.json()
        if len(response['features']) == 0:
            return ''
        response = response['features'][0]
        resp_ll = ','.join(map(str, response['geometry']['coordinates']))
        if lonlat_distance(ll, resp_ll) > 50:
            return ''
        return resp_ll


def get_ll(x: int, y: int, long: float, lat: float, spn_long: float, spn_lat: float) -> str:
    return str(long - (y / 450 - 0.5) * spn_long) + ',' + \
            str(lat + (x / 600 - 0.5) * spn_lat)


def debug() -> None:
    pass


if __name__ == '__main__':
    debug()
    window = api_window.Window()
    window.loop()
    exit(0)
