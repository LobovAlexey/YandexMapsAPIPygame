import pygame


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
    __coordinates_offset = 4    # From address row

    width: int
    height: int
    __screen: pygame.Surface
    __clock: pygame.time.Clock

    __search_font: pygame.font.FontType
    search_query: str

    __address_font: pygame.font.FontType
    object_address: str

    __coordinates_font: pygame.font.FontType
    coordinates: tuple[float, float] | None

    __is_exited: bool

    def __init__(self, width: int = 720, height: int = 720) -> None:
        pygame.init()
        self.__search_font = pygame.font.FontType(Window.__font_path, Window.__search_rect[1] * 2 // 3)
        self.search_query = 'xsrdctvfybguhnijmok,pl.pouifdcfvghjhknml,;.yryihhtfugtuf'
        self.__address_font = pygame.font.FontType(Window.__font_path, self.__address_font_size)
        self.object_address = 'testtesttest'
        self.__coordinates_font = pygame.font.FontType(Window.__font_path, self.__coordinates_font_size)
        self.coordinates = (0.214312, 3.13413513)
        self.__is_exited = False

        self.width = width
        self.height = height
        self.__screen = pygame.display.set_mode((width, height))
        self.__clock = pygame.time.Clock()

    def draw_map(self) -> None:  # Сварганьте что-нибудь, не шарю, как карту отображать. Это дело ваше
        pass

    def draw_search(self) -> None:
        search_width = self.width * Window.__search_rect[0] - Window.__search_offset[0]
        # Outline
        pygame.draw.ellipse(self.__screen, Window.__search_outline_color,
                            (Window.__search_offset[0] - Window.__search_outline_width,
                             Window.__search_offset[0] - Window.__search_outline_width,
                             Window.__search_rect[1] + Window.__search_outline_width * 2,
                             Window.__search_rect[1] + Window.__search_outline_width * 2),
                            Window.__search_outline_width)
        pygame.draw.rect(self.__screen, Window.__search_outline_color,
                         (Window.__search_offset[0] + Window.__search_rect[1] / 2 - Window.__search_outline_width,
                          Window.__search_offset[1] - Window.__search_outline_width,
                          search_width - Window.__search_rect[1] - Window.__search_outline_width * 2,
                          Window.__search_rect[1] + Window.__search_outline_width * 2),
                         Window.__search_outline_width)
        pygame.draw.ellipse(self.__screen, Window.__search_outline_color,
                            (Window.__search_offset[0] - Window.__search_outline_width + search_width -
                             Window.__search_rect[1],
                             Window.__search_offset[0] - Window.__search_outline_width,
                             Window.__search_rect[1] + Window.__search_outline_width * 2,
                             Window.__search_rect[1] + Window.__search_outline_width * 2),
                            Window.__search_outline_width)
        # Fill
        pygame.draw.ellipse(self.__screen, Window.__search_color,
                            (Window.__search_offset, (Window.__search_rect[1], Window.__search_rect[1])))
        pygame.draw.rect(self.__screen, Window.__search_color,
                         (Window.__search_offset[0] + Window.__search_rect[1] / 2, Window.__search_offset[1],
                          search_width - Window.__search_rect[1], Window.__search_rect[1]))
        pygame.draw.ellipse(self.__screen, Window.__search_color,
                            (Window.__search_offset[0] + search_width - Window.__search_rect[1],
                             Window.__search_offset[1], Window.__search_rect[1], Window.__search_rect[1]))

    def display_search_query(self) -> None:
        text = self.search_query
        if text == '':
            text = 'Поиск'
        else:
            limit_width = self.width * Window.__search_rect[0] - Window.__search_rect[1]
            if self.__search_font.size(text)[0] >= limit_width:
                text = text[:-1]
                while self.__search_font.size(text)[0] >= limit_width:
                    text = text[:-1]
                text = text[:-4] + '...'
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
        text = self.__coordinates_font.render(', '.join(map(str, self.coordinates)), True, Window.__coordinates_color)
        self.__screen.blit(text, (Window.__search_offset[0],
                                  Window.__search_offset[1] + Window.__search_rect[1]
                                  + self.__address_font.size('|')[1] + Window.__address_offset * 2))

    def loop(self) -> None:
        while True:
            self.__clock.tick(30)
            self.check_events()
            if self.__is_exited:
                break
            self.draw()

    def check_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    self.quit()
                case pygame.KEYDOWN:
                    match event.key:
                        case _:
                            pass
                case pygame.KEYUP:
                    match event.type:
                        case _:
                            pass
                case _:
                    pass

    def draw(self) -> None:
        self.__screen.fill((255, 255, 255))
        self.draw_map()
        self.draw_search()
        self.display_search_query()
        self.display_object_address()
        self.display_coordinates()
        pygame.display.flip()

    def quit(self) -> None:
        self.__is_exited = True  # Типа окошко закрывается
