from __future__ import annotations
import pygame
import pygame.freetype

import api_functions
import map_utils

from time import time as now


class Rect:
    departure: pygame.Rect
    coefficient: float

    __states: list[pygame.Rect, ...]
    __current_state: int
    __progress: float

    def __init__(self, x: float, y: float, w: float, h: float, k: float) -> None:
        self.departure = pygame.Rect(x, y, w, h)
        self.coefficient = k
        self.__states = [self.departure.copy()]
        self.__current_state = 0
        self.__progress = 1.0

    def set_state(self, index: int) -> None:
        self.departure = Rect(self.x, self.y, self.w, self.h, self.coefficient)
        self.__current_state = index
        self.__progress = 0.0

    def add_state(self, x: float, y: float, w: float, h: float) -> None:
        self.__states.append(pygame.Rect(x, y, w, h))

    def get_current_state(self) -> pygame.Rect:
        return self.__states[self.__current_state]

    def set_progress(self, new_progress: float) -> None:
        self.__progress = max(0.0, min(new_progress, 1.0))

    def update(self, delta_time: float) -> None:
        self.__progress = min(self.__progress + delta_time * self.coefficient, 1.0)

    @property
    def x(self) -> float:
        return self.departure.x * (1.0 - self.__progress) + self.__states[self.__current_state].x * self.__progress

    @property
    def y(self) -> float:
        return self.departure.y * (1.0 - self.__progress) + self.__states[self.__current_state].y * self.__progress

    @property
    def w(self) -> float:
        return self.departure.w * (1.0 - self.__progress) + self.__states[self.__current_state].w * self.__progress

    @property
    def h(self) -> float:
        return self.departure.h * (1.0 - self.__progress) + self.__states[self.__current_state].h * self.__progress

    @property
    def progress(self) -> float:
        return self.__progress

    @property
    def state(self) -> float:
        return self.__current_state

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def copy(self) -> Rect:
        result = Rect(self.__states[0].x, self.__states[0].y, self.__states[0].w, self.__states[0].h, self.coefficient)
        for state in self.__states[1:]:
            result.add_state(*state.copy())
        result.set_progress(self.__progress)
        return result


class Window:
    __letter_dict = 'qwertyuiopasdfghjklzxcvbnm,./-йцукенгшщзхъфывапролджэячсмитьбюё 1234567890'

    __font_path = './Anonymous_Pro.ttf'
    __search_offset = (16, 16)  # x, y offsets
    __search_rect = (1.0 / 2.0, 32)  # Width coefficient + height

    __search_outline_color = pygame.Color(127, 127, 127)
    __search_color = pygame.Color(191, 191, 191)
    __search_text_color = pygame.Color(0, 0, 0)

    __search_outline_width = 1

    __address_font_size = 16
    __address_color = pygame.Color(63, 63, 63)
    __address_offset = 8  # From search bar

    __coordinates_font_size = 12
    __coordinates_color = pygame.Color(63, 63, 63)
    __coordinates_offset = 4  # From address row

    width: int
    height: int
    __screen: pygame.Surface
    __clock: pygame.time.Clock

    __MAX_FPS = 30
    __delta_time: float

    __map_surface: pygame.Surface

    __center_lat: float = 0.0
    __center_lon: float = 0.0
    __scale: float = 1.0
    __mode: int = 0
    __SCHEMA = 0
    __SPUTNIK = 1
    __HYBRID = 2

    __search_font: pygame.font.FontType
    search_query: str

    __address_font: pygame.font.FontType
    object_address: str
    postal_code: str

    __coordinates_font: pygame.font.FontType
    query_coordinates: str | None

    __menu_icon_img: pygame.Surface
    __menu_icon_rect: pygame.Rect
    __menu_icon_is_mouse_on: bool

    __menu_icon_offset = 16
    __menu_icon_round_radius = 4
    __menu_icon_background_color = pygame.Color(239, 239, 239, 127)
    __menu_icon_outline_color = pygame.Color(255, 255, 255, 127)
    __menu_icon_outline_width = 2

    __nav_icon_img_1: pygame.Surface
    __nav_icon_1_rect: Rect
    __nav_icon_1_on_mouse: bool
    __nav_icon_img_2: pygame.Surface
    __nav_icon_2_rect: Rect
    __nav_icon_2_on_mouse: bool
    __nav_icon_img_3: pygame.Surface
    __nav_icon_3_rect: Rect
    __nav_icon_3_on_mouse: bool

    __nav_background_color = pygame.Color(127, 127, 127, 127)

    __menu_icon_background_rect: pygame.Rect
    __menu_nav_background_rect: Rect

    __is_menu_showed: bool

    __waypoint: tuple[float, float] | None
    __waypoint_icon: pygame.Surface
    __waypoint_rect = (20, 20)

    __cross_image: pygame.Surface
    __cross_rect: pygame.Rect
    __cross_on_mouse: bool

    __switch_mode: bool
    __switch_base: pygame.Rect
    __switch_circle: Rect
    __switch_off_color = pygame.Color(127, 127, 127)
    __switch_on_color = pygame.Color(63, 63, 63)
    __switch_outline_color = pygame.Color(191, 191, 191)
    __switch_circle_color = __switch_outline_color
    __switch_on_mouse: bool

    __cursor_pos: tuple[float, float]

    __mouse_on: bool

    __is_exited: bool

    def __init__(self, width: int = 600, height: int = 450) -> None:
        pygame.init()
        self.width = width
        self.height = height
        self.__screen = pygame.display.set_mode((width, height))
        self.__clock = pygame.time.Clock()
        self.__delta_time = 1.0 / self.__MAX_FPS

        self.__map_surface = pygame.Surface((width, height))
        self.__map_surface.fill((255, 255, 255))

        self.__search_font = pygame.font.FontType(Window.__font_path, Window.__search_rect[1] * 2 // 3)
        self.search_query = 'Центр Москвы'
        self.font = pygame.freetype.Font(None, 24)
        self.__address_font = pygame.font.FontType(Window.__font_path, self.__address_font_size)
        self.object_address = 'Центр Москвы'
        self.postal_code = '101000'
        self.__coordinates_font = pygame.font.FontType(Window.__font_path, self.__coordinates_font_size)
        self.query_coordinates = '0.0,0.0'

        self.__menu_icon_img = pygame.transform.scale(pygame.image.load('./icon/menu.png'), (40, 40))
        self.__menu_icon_rect = pygame.Rect(self.width - 40 - self.__menu_icon_offset,
                                            self.__menu_icon_offset, 40, 40)
        self.__menu_icon_is_mouse_on = False

        self.__menu_icon_background_rect = pygame.Rect(
            self.__menu_icon_rect.x - 8, self.__menu_icon_rect.y - 8,
            self.__menu_icon_rect.w + 16, self.__menu_icon_rect.h + 16
        )

        self.__menu_nav_background_rect = Rect(
            self.__menu_icon_rect.x - 8, self.__menu_icon_rect.y - 8,
            self.__menu_icon_rect.w + 16, self.__menu_icon_rect.h + 16,
            2.0
        )
        self.__menu_nav_background_rect.add_state(
            self.__menu_icon_rect.x - self.__menu_icon_rect.w * 3 - 8 * 5, self.__menu_icon_rect.y - 8,
            self.__menu_icon_rect.w * 4 + 8 * 6, self.__menu_icon_rect.h + 8 * 2
        )

        self.__nav_icon_img_1 = pygame.transform.scale(pygame.image.load('./icon/map.png'), (40, 40))
        temp = self.__nav_icon_img_1.get_rect()
        self.__nav_icon_1_rect = Rect(self.__menu_icon_rect.x, self.__menu_icon_rect.y, temp.w, temp.h, 2.0)
        self.__nav_icon_1_rect.add_state(
            self.__menu_icon_rect.x - self.__nav_icon_1_rect.w * 3 - 8 * 4, self.__menu_icon_rect.y, temp.w, temp.h
        )
        self.__nav_icon_1_on_mouse = False

        self.__nav_icon_img_2 = pygame.transform.scale(pygame.image.load('./icon/worldwide.png'), (40, 40))
        temp = self.__nav_icon_img_2.get_rect()
        self.__nav_icon_2_rect = Rect(self.__menu_icon_rect.x, self.__menu_icon_rect.y, temp.w, temp.h, 2.0)
        self.__nav_icon_2_rect.add_state(
            self.__menu_icon_rect.x - self.__nav_icon_2_rect.w * 2 - 8 * 3, self.__menu_icon_rect.y, temp.w, temp.h
        )
        self.__nav_icon_2_on_mouse = False

        self.__nav_icon_img_3 = pygame.transform.scale(pygame.image.load('./icon/apple.png'), (40, 40))
        temp = self.__nav_icon_img_3.get_rect()
        self.__nav_icon_3_rect = Rect(self.__menu_icon_rect.x, self.__menu_icon_rect.y, temp.w, temp.h, 2.0)
        self.__nav_icon_3_rect.add_state(
            self.__menu_icon_rect.x - self.__nav_icon_3_rect.w - 8 * 2, self.__menu_icon_rect.y, temp.w, temp.h
        )
        self.__nav_icon_3_on_mouse = False

        self.__is_menu_showed = False

        self.__waypoint = (0.0, 0.0)
        self.__waypoint_icon = pygame.transform.scale(pygame.image.load('./icon/ang.png'), self.__waypoint_rect)

        self.__cross_image = pygame.transform.scale(pygame.image.load('./icon/cross.png'), (16, 16))
        self.__cross_rect = pygame.Rect(self.width * 0.5 - 24, self.__search_offset[1] + 8, 16, 16)
        self.__cross_on_mouse = False

        self.__switch_mode = False
        self.__switch_base = pygame.Rect(self.width * 0.5 + 4, self.__search_offset[1] + self.__search_rect[1] / 6.0,
                                         self.__search_rect[1], self.__search_rect[1] / 1.5)
        self.__switch_circle = Rect(self.__switch_base.x + 4, self.__switch_base.y + 4,
                                    self.__search_rect[1] / 2 - 4, self.__search_rect[1] / 2 - 4, 4.0)
        self.__switch_circle.add_state(self.__switch_base.right - self.__switch_circle.w - 4,
                                       self.__switch_circle.y, self.__switch_circle.w, self.__switch_circle.h)
        self.__switch_on_mouse = False

        self.__mouse_on = False

        self.__is_exited = False

        self.search(self.search_query)

    # ---------------- Draw functions ----------------

    def draw_map(self) -> None:
        self.__screen.blit(self.__map_surface, (0.0, 0.0))

    def draw_round_square(self, x: float, y: float, w: float, h: float, r: int,
                          c: pygame.Color, co: pygame.Color = pygame.Color(0, 0, 0), o: int = 0):
        pygame.draw.rect(self.__screen, co, (x, y, w, h), width=o, border_radius=r)
        pygame.draw.rect(self.__screen, c, (x + o, y + o, w - o * 2.0, h - o * 2.0), width=0, border_radius=r - o)

    def draw_search(self) -> None:
        search_width = self.width * Window.__search_rect[0] - Window.__search_offset[0]
        self.draw_round_square(Window.__search_offset[0], Window.__search_offset[1],
                               search_width, Window.__search_rect[1], Window.__search_rect[1] // 2,
                               Window.__search_color, Window.__search_outline_color, Window.__search_outline_width)

    def display_search_query(self) -> None:
        text = self.search_query
        if text == '':
            text = 'Поиск'
        else:
            limit = self.width * Window.__search_rect[0] - Window.__search_rect[1]
            text = map_utils.limit_row_width(text, self.__search_font, limit)
        text = self.__search_font.render(text, True, Window.__search_text_color)
        self.__screen.blit(text, (Window.__search_offset[0] + Window.__search_rect[1] / 2,
                                  Window.__search_offset[1] + (Window.__search_rect[1] - text.get_size()[1]) / 2))
        self.__screen.blit(self.__cross_image, self.__cross_rect)

    def display_object_address(self) -> None:
        if self.object_address == '':
            return
        s = self.object_address + ((': ' + self.postal_code) if self.__switch_mode and self.postal_code else '')
        text = self.__address_font.render(s, True, Window.__address_color)
        self.__screen.blit(text, (Window.__search_offset[0],
                                  Window.__search_offset[1] + Window.__search_rect[1] + Window.__address_offset))

    def display_coordinates(self) -> None:
        if self.query_coordinates is None:
            return
        text = self.__coordinates_font.render(self.query_coordinates, True, Window.__coordinates_color)
        self.__screen.blit(text, (Window.__search_offset[0], Window.__search_offset[1] + Window.__search_rect[1]
                                  + self.__address_font.size('|')[1] + Window.__address_offset * 2))

    def display_menu_button(self) -> None:
        self.__menu_nav_background_rect.update(self.__delta_time)
        self.__nav_icon_3_rect.update(self.__delta_time)
        self.__nav_icon_2_rect.update(self.__delta_time)
        self.__nav_icon_1_rect.update(self.__delta_time)
        self.draw_round_square(
            *self.__menu_nav_background_rect.get_rect(),
            r=self.__menu_icon_round_radius, c=self.__menu_icon_background_color,
            co=self.__menu_icon_outline_color, o=self.__menu_icon_outline_width)
        if self.__nav_icon_1_on_mouse:
            self.draw_round_square(*self.__nav_icon_1_rect.get_rect(),
                                   r=self.__menu_icon_round_radius, c=self.__nav_background_color)
        if self.__nav_icon_2_on_mouse:
            self.draw_round_square(*self.__nav_icon_2_rect.get_rect(),
                                   r=self.__menu_icon_round_radius, c=self.__nav_background_color)
        if self.__nav_icon_3_on_mouse:
            self.draw_round_square(*self.__nav_icon_3_rect.get_rect(),
                                   r=self.__menu_icon_round_radius, c=self.__nav_background_color)
        self.__screen.blit(self.__nav_icon_img_3, self.__nav_icon_3_rect.get_rect())
        self.__screen.blit(self.__nav_icon_img_2, self.__nav_icon_2_rect.get_rect())
        self.__screen.blit(self.__nav_icon_img_1, self.__nav_icon_1_rect.get_rect())
        self.draw_round_square(
            *self.__menu_icon_background_rect,
            r=self.__menu_icon_round_radius, c=self.__menu_icon_background_color,
            co=self.__menu_icon_outline_color, o=self.__menu_icon_outline_width)
        self.__screen.blit(self.__menu_icon_img, self.__menu_icon_rect)

    def display_waypoint(self) -> None:
        if self.__waypoint is None:
            return
        self.__screen.blit(self.__waypoint_icon, self.ll2xy(*self.__waypoint))

    def draw_switch(self) -> None:
        self.__switch_circle.update(self.__delta_time)

        c = self.__switch_off_color.lerp(self.__switch_on_color,
                                         1.0 - abs(int(self.__switch_mode) - self.__switch_circle.progress))
        self.draw_round_square(*self.__switch_base, r=self.__switch_base.h // 2, c=c,
                               co=self.__switch_outline_color, o=2)
        pygame.draw.circle(self.__screen, self.__switch_circle_color,
                           self.__switch_circle.get_rect().center, self.__switch_circle.w // 2)

    # ---------------- Main functions ----------------

    def loop(self) -> None:
        while True:
            start_time = now()

            self.__clock.tick(self.__MAX_FPS)
            self.check_events()
            if self.__is_exited:
                print('Bye!')
                break
            self.draw()

            self.__delta_time = max(1.0 / self.__MAX_FPS, now() - start_time)

    def search(self, address: str) -> None:
        toponym = api_functions.Geocoder.get(address)

        if toponym is None:
            print('Объект не был найден или не определён')
            return

        self.object_address = toponym['address']
        self.postal_code = toponym['postal_code']
        ll = toponym['ll']
        self.query_coordinates = ll
        self.__center_lat, self.__center_lon = map(float, ll.split(','))

        self.__waypoint = (self.__center_lat, self.__center_lon)

        self.update_map()

    def xy2ll(self, x: float, y: float) -> tuple[float, float]:
        x = (x - self.width // 2) / self.width * self.__scale * 3 + self.__center_lat
        y = -(y - self.height // 2) / self.height * self.__scale * 2 + self.__center_lon
        return x, y

    def ll2xy(self, lat: float, lon: float) -> tuple[float, float]:
        x = map_utils.lat2meter(lat - self.__center_lat) \
            / (self.width * self.__scale) + self.width // 2
        y = -map_utils.lon2meter(self.__center_lat, lon - self.__center_lon) \
            / (self.height * self.__scale) + self.height // 2
        return x, y

    def update_map(self) -> None:
        response = api_functions.StaticMaps.get_map(ll=f'{self.__center_lat},{self.__center_lon}',
                                                    spn=f'{self.__scale},{self.__scale}', type_index=self.__mode)
        if not response:
            print('Ошибка при получении карты')
        self.__map_surface = map_utils.bytes_to_surface(response.content)

    def check_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    self.quit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_RETURN:
                            self.search(self.search_query)
                        case pygame.K_BACKSPACE:
                            self.search_query = self.search_query[:-1]
                        case pygame.K_UP:
                            self.__center_lon = min(self.__center_lon + self.__scale * 0.25, 90 - self.__scale * 0.5)
                            self.update_map()
                        case pygame.K_DOWN:
                            self.__center_lon = max(self.__center_lon - self.__scale * 0.25, -90 + self.__scale * 0.5)
                            self.update_map()
                        case pygame.K_RIGHT:
                            self.__center_lat = min(self.__center_lat + self.__scale * 0.25, 90 - self.__scale * 0.5)
                            self.update_map()
                        case pygame.K_LEFT:
                            self.__center_lat = max(self.__center_lat - self.__scale * 0.25, -90 + self.__scale * 0.5)
                            self.update_map()
                        case pygame.K_PAGEUP:
                            self.__scale = min(max(0.0009765625, (self.__scale + 1) ** (0.75 ** 1) - 1), 64)
                            self.update_map()
                        case pygame.K_PAGEDOWN:
                            self.__scale = min(max(0.0009765625, (self.__scale + 1) ** (0.75 ** -1) - 1), 64)
                            self.update_map()
                        case pygame.K_TAB:
                            self.update_map()
                        case _:
                            if event.unicode.lower() in self.__letter_dict:
                                self.search_query += event.unicode
                case pygame.MOUSEWHEEL:
                    self.__scale = min(max(0.0009765625, (self.__scale + 1) ** (0.75 ** event.y) - 1), 64)
                    self.update_map()
                case pygame.MOUSEMOTION:
                    self.__menu_icon_is_mouse_on = self.__menu_icon_rect.collidepoint(event.pos)
                    if self.__is_menu_showed:
                        self.__nav_icon_3_on_mouse = self.__nav_icon_3_rect.get_rect().collidepoint(event.pos)
                        self.__nav_icon_2_on_mouse = self.__nav_icon_2_rect.get_rect().collidepoint(event.pos)
                        self.__nav_icon_1_on_mouse = self.__nav_icon_1_rect.get_rect().collidepoint(event.pos)
                    self.__cross_on_mouse = self.__cross_rect.collidepoint(event.pos)
                    self.__switch_on_mouse = self.__switch_circle.get_rect().collidepoint(event.pos)
                    if (self.__menu_icon_is_mouse_on or self.__nav_icon_3_on_mouse
                            or self.__nav_icon_2_on_mouse or self.__nav_icon_1_on_mouse
                            or self.__cross_on_mouse or self.__switch_on_mouse):
                        if self.__mouse_on is False:
                            pygame.mouse.set_cursor(pygame.cursors.broken_x)
                            self.__mouse_on = True
                    elif self.__mouse_on is True:
                        pygame.mouse.set_cursor(pygame.cursors.arrow)
                        self.__mouse_on = False

                    self.__cursor_pos = self.ll2xy(*self.xy2ll(*event.pos))
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        if self.__is_menu_showed:
                            if self.__nav_icon_1_on_mouse:
                                self.__mode = self.__SCHEMA
                                self.update_map()
                                return
                            elif self.__nav_icon_2_on_mouse:
                                self.__mode = self.__SPUTNIK
                                self.update_map()
                                return
                            elif self.__nav_icon_3_on_mouse:
                                self.__mode = self.__HYBRID
                                self.update_map()
                                return
                        if self.__menu_icon_is_mouse_on:
                            self.__is_menu_showed = not self.__is_menu_showed
                            new_state_index = int(self.__is_menu_showed)
                            self.__menu_nav_background_rect.set_state(new_state_index)
                            self.__nav_icon_3_rect.set_state(new_state_index)
                            self.__nav_icon_2_rect.set_state(new_state_index)
                            self.__nav_icon_1_rect.set_state(new_state_index)
                        elif self.__cross_on_mouse and self.query_coordinates:
                            self.search_query = ''
                            self.object_address = ''
                            self.query_coordinates = None
                            self.__waypoint = None
                        elif self.__switch_on_mouse:
                            self.__switch_mode = not self.__switch_mode
                            self.__switch_circle.set_state(int(self.__switch_mode))
                        else:
                            lat, lon = self.xy2ll(*event.pos)
                            self.search(f'{lat},{lon}')
                    elif event.button == pygame.BUTTON_RIGHT:
                        lat, lon = self.xy2ll(*event.pos)
                        ll = api_functions.Search.get_organisation(f'{lat},{lon}')
                        if ll is None:
                            return
                        self.search(ll)

    def draw(self) -> None:
        self.draw_map()
        pygame.draw.circle(self.__screen, (127, 127, 127, 127), self.ll2xy(*self.xy2ll(*self.__cursor_pos)), 4)

        self.draw_search()
        self.display_waypoint()
        self.display_search_query()
        self.display_object_address()
        self.display_coordinates()

        self.draw_switch()

        self.display_menu_button()
        pygame.display.flip()

    def quit(self) -> None:
        self.__is_exited = True  # Типа окошко закрывается
