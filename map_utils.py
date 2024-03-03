import math
import os

import pygame


def lonlat_distance(a, b) -> float:  # в метрах
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


def get_ll(x: int, y: int, long: float, lat: float, spn_long: float, spn_lat: float) -> str:
    return str(long - (y / 450.0 - 0.5) * spn_long) + ',' + \
        str(lat + (x / 600.0 - 0.5) * spn_lat)


def bytes_to_surface(content: bytes) -> pygame.Surface:
    map_file_name = '_map.png'
    with open(map_file_name, 'wb') as map_file:
        map_file.write(content)
    _surface = pygame.image.load(map_file_name)
    os.remove(map_file_name)
    return _surface


def limit_row_width(s: str, font: pygame.font.FontType, w: float) -> str:
    if font.size(s)[0] >= w:
        while font.size(s + '...')[0] >= w:
            s = s[:-1]
        return s[:-1] + '...'
    return s


class SearchQuery:
    def __init__(self):
        self.query = ""

    def add_char(self, char):
        self.query += char

    def delete_last_char(self):
        if self.query:
            self.query = self.query[:-1]

    def clear_query(self):
        self.query = ""


def format_object_info(name, address, postal_code=None):
    formatted_info = f"Имя обьекта: {name}\nАдресс: {address}"
    if postal_code:
        formatted_info += f"\nПочтовый индекс: {postal_code}"
    return formatted_info


