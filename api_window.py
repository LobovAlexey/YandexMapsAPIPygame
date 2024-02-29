import pygame
import pygame.freetype

import api_functions
import map_utils


class Window:
    __font_path = './Anonymous_Pro.ttf'
    __search_offset = (16, 16)  # x, y offsets
    __search_rect = (1.0 / 2.0, 32)  # Width coefficient + height

    __search_outline_color = pygame.Color(127, 127, 127)
    __search_color = pygame.Color(191, 191, 191)
    __search_text_color = pygame.Color(0, 0, 0)

    __search_outline_width = 2

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

    __map_surface: pygame.Surface

    __search_font: pygame.font.FontType
    search_query: str

    __address_font: pygame.font.FontType
    object_address: str

    __coordinates_font: pygame.font.FontType
    coordinates: str

    __is_exited: bool

    def __init__(self, width: int = 720, height: int = 720) -> None:
        pygame.init()
        self.__map_surface = pygame.Surface((width, height))
        self.__map_surface.fill((255, 255, 255))
        self.__search_font = pygame.font.FontType(Window.__font_path, Window.__search_rect[1] * 2 // 3)
        self.search_query = 'Центр Москвы'
        self.font = pygame.freetype.Font(None, 24)
        self.__address_font = pygame.font.FontType(Window.__font_path, self.__address_font_size)
        self.object_address = ''
        self.__coordinates_font = pygame.font.FontType(Window.__font_path, self.__coordinates_font_size)
        self.coordinates = '0.0, 0.0'
        self.__is_exited = False

        self.width = width
        self.height = height
        self.__screen = pygame.display.set_mode((width, height))
        self.__clock = pygame.time.Clock()

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

    def display_object_address(self) -> None:
        if self.object_address == '':
            return
        text = self.__address_font.render(self.object_address, True, Window.__address_color)
        self.__screen.blit(text, (Window.__search_offset[0],
                                  Window.__search_offset[1] + Window.__search_rect[1] + Window.__address_offset))

    def display_coordinates(self) -> None:
        if self.coordinates is None:
            return
        text = self.__coordinates_font.render(self.coordinates, True, Window.__coordinates_color)
        self.__screen.blit(text, (Window.__search_offset[0],
                                  Window.__search_offset[1] + Window.__search_rect[1]
                                  + self.__address_font.size('|')[1] + Window.__address_offset * 2))

    # ---------------- Main functions ----------------

    def loop(self) -> None:
        while True:
            self.__clock.tick(30)
            self.check_events()
            if self.__is_exited:
                break
            self.font.render_to(self.__screen, (10, 10), self.search_query)
            self.draw()

    def search(self, query: str) -> None:
        self.search_query = query
        toponym = api_functions.Geocoder.get(query)
        if toponym is None:
            print("Ошибка при получении координат")
            return

        ll = toponym['ll']
        self.coordinates = ll
        response = api_functions.StaticMaps.get_map(ll=ll, spn="0.01,0.01", type_index=0)
        if not response:
            print("Ошибка при получении карты")
            return
        map_surface = map_utils.bytes_to_surface(response.content)
        self.__screen.blit(map_surface, (0.0, 0.0))

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
                        case _:
                            self.search_query += event.unicode
                case pygame.KEYUP:
                    match event.type:
                        case _:
                            pass
                case _:
                    pass

    def draw(self) -> None:
        self.draw_map()
        self.draw_search()
        self.display_search_query()
        self.display_object_address()
        self.display_coordinates()
        pygame.display.flip()

    def quit(self) -> None:
        self.__is_exited = True  # Типа окошко закрывается
