import math
import os

import pygame

deg2rad = math.pi / 180.0

earth_radius = 6_356_752.3


def lat2meter(lat: float) -> float:
    return earth_radius * lat * deg2rad


def lon2meter(lat: float, lon: float) -> float:
    return earth_radius * lon * deg2rad * math.cos(lat * deg2rad)   # * 1.41421356


def lonlat_distance(a: str | tuple[float, float], b: str | tuple[float, float]) -> float:  # в метрах
    if isinstance(a, str):
        a = [float(i.strip()) for i in a.split(',')]
    if isinstance(b, str):
        b = [float(i.strip()) for i in b.split(',')]
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_latitude = math.radians((a_lat + b_lat) / 2.0)
    lat_lon_factor = math.cos(radians_latitude)
    dx = lat2meter(abs(a_lon - b_lon)) * lat_lon_factor
    dy = lat2meter(abs(a_lat - b_lat))
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


def get_ll(x: int, y: int, long: float, lat: float, spn_long: float, spn_lat: float) -> str:
    return str(long - (y / 450.0 - 0.5) * spn_long) + ',' + str(lat + (x / 600.0 - 0.5) * spn_lat)


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
