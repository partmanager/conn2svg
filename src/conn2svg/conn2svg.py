import drawsvg as svg
from ._tooling import FontTooling

DEFAULT_COLORS = {'#2f75b5': ['gnd']}
DEFAULT_BG_COLOR = '#eeeeee'
DEFAULT_PIN_WIDTH = 20
DEFAULT_PIN_HEIGHT = 20
DEFAULT_FONT_SIZE = DEFAULT_PIN_HEIGHT * 0.5
DEFAULT_FONT_FAMILY = 'Arial'


class PinText:
    def __init__(self,
                 text: str = '',
                 x: float = 0,
                 y: float = 0,
                 color: str = '#000000',
                 anchor: str = 'start') -> None:
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.anchor = anchor

    def svg_elements(self) -> list:
        return [self._overline(svg.Text(text = '',
                                        font_size = str(DEFAULT_FONT_SIZE) + 'px',
                                        x = round(self.x, 2),
                                        y = round(self.y, 2),
                                        font_family = DEFAULT_FONT_FAMILY,
                                        text_anchor = self.anchor,
                                        fill = self.color))]

    def width(self) -> float:
        return FontTooling.calculate_text_width(self.text.replace('\\', ''),
                                                DEFAULT_FONT_SIZE,
                                                DEFAULT_FONT_FAMILY)

    def _overline(self, svg_text: svg.Text) -> svg.Text:
        for i in range(0, len(self.text), 1):
            current = self.text[i]
            next = None
            if i < len(self.text) - 1:
                next = self.text[i + 1]

            if next == '\\':
                svg_text.append(svg.TSpan(text=current, text_decoration='overline'))
            elif not current == '\\':
                svg_text.append(svg.TSpan(text=current))
        return svg_text


class Pin:
    def __init__(self,
                 designator: PinText,
                 net: PinText,
                 x: float = 0,
                 y: float = 0,
                 color: str = DEFAULT_BG_COLOR,
                 pin_width: float = DEFAULT_PIN_WIDTH) -> None:
        self.pin_width = pin_width
        self.designator = designator
        self.net = net
        self.x = x
        self.y = y
        self.color = color

    @property
    def width(self):
        self._set_elements()
        width = self.net.x + self.net.width()
        if self.x < 0:
            width = self.net.x - self.net.width()
        return width

    def _set_elements(self) -> None:
        self.designator.x = self.x + self.pin_width / 2
        self.designator.y = self.y + DEFAULT_PIN_HEIGHT / 2 + DEFAULT_FONT_SIZE / 3
        self.designator.anchor = 'middle'
        if not self._is_color_bright(self.color):
            self.designator.color = '#ffffff'

        self.net.x = self.x + DEFAULT_PIN_WIDTH * 1.25
        if self.x < 0:
            self.net.x = self.x - DEFAULT_PIN_WIDTH * 0.25
            self.net.anchor = 'end'
        self.net.y = self.designator.y

    def svg_elements(self) -> list:
        self._set_elements()
        elements = [svg.Rectangle(x=round(self.x, 2),
                                  y=round(self.y, 2),
                                  width=self.pin_width,
                                  height=DEFAULT_PIN_HEIGHT,
                                  stroke='black',
                                  fill=self.color)]
        elements.extend(self.designator.svg_elements())
        elements.extend(self.net.svg_elements())
        return elements

    def _is_color_bright(self, color: str) -> bool:
        color = color.replace('#', '')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        luminance = 1 - (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5


class PinPattern:
    MATRIX = {'header': {'tb': [[], '1col'],
                         'bt': [['reverse'], '1col'],
                         'tb-lr': [[], '2col'],
                         'tb-rl': [['flip_half'], '2col'],
                         'bt-rl': [['reverse'], '2col'],
                         'bt-lr': [['reverse', 'flip_half'], '2col'],
                         'lr-tb': [['odd_even'], '2col'],
                         'lr-bt': [['odd_even', 'flip_half', 'reverse'], '2col'],
                         'rl-tb': [['odd_even', 'flip_half'], '2col'],
                         'rl-bt': [['odd_even', 'reverse'], '2col']},
              'dsub': {'tb-lr': [[], '1left'],
                       'bt-rl': [['reverse'], '1right'],
                       'bt-lr': [['reverse', 'flip_half'], '1left'],
                       'tb-rl': [['flip_half', 'shift_left'], '1right']}}

    def __init__(self,
                 pin_count: int,
                 type: str,
                 mode: str,
                 prefixes: list = None,
                 shield_designator: str = None) -> None:
        self._pins = []
        self._generate(pin_count, type, mode, prefixes, shield_designator)

    def to_dict(self) -> dict:
        output = {}
        for pin in self._pins:
            output.update({pin.designator.text: pin})
        return output

    def designators(self) -> list:
        return list(self.to_dict().keys())

    def _generate(self, pin_count: int, type: str, mode: str, prefixes: list, shld: str) -> list:
        self._generate_designators(pin_count, prefixes)
        if type in self.MATRIX:
            modes = self.MATRIX[type]
            if mode in modes:
                for transform in modes[mode][0]:
                    if transform == 'reverse':
                        self._pins = self._pins[::-1]
                    elif transform == 'flip_half':
                        half = round(len(self._pins)/2)
                        self._pins = self._pins[half::] + self._pins[:half:]
                    elif transform == 'odd_even':
                        self._pins = self._pins[::2] + self._pins[1::2]
                    elif transform == 'shift_left':
                        self._pins = self._pins + [self._pins.pop(0)]
                    else:
                        raise ValueError('Unknown pin pattern transformation:', transform)
                if modes[mode][1] == '1col':
                    self._generate_1col(pin_count)
                elif modes[mode][1] == '2col':
                    self._generate_2col(pin_count, shld)
            else:
                raise ValueError('Unknown pin pattern mode:', mode)
        else:
            raise ValueError('Unknown pin pattern type:', type)

    def _generate_designators(self, pin_count: int, prefixes: list) -> list:
        self._pins = []
        if prefixes:
            for prefix in prefixes:
                for number in range(1, round(pin_count/len(prefixes)) + 1 , 1):
                    self._pins.append(Pin(designator=PinText(prefix+str(number)),
                                          net=PinText()))
        else:
            for number in range(1, pin_count + 1 , 1):
                self._pins.append(Pin(designator=PinText(str(number)),
                                      net=PinText()))

    def _generate_1col(self, pin_count: int):
        for i in range(0, pin_count, 1):
            self._pins[i].y = i * DEFAULT_PIN_HEIGHT

    def _generate_2col(self, pin_count: int, shld: str):
        x = -1 * DEFAULT_PIN_WIDTH
        y = 0
        half = False
        for i in range(0, pin_count, 1):
            self._pins[i].x = x
            self._pins[i].y = y
            y += DEFAULT_PIN_HEIGHT
            if not half and i + 1 >= pin_count / 2:
                y = 0
                x = 0
                half = True
        if shld != None and len(shld):
            self._pins.append(Pin(designator=PinText(shld),
                                  net=PinText(),
                                  x = - DEFAULT_PIN_WIDTH,
                                  y = y,
                                  pin_width=DEFAULT_PIN_WIDTH*2))


class PinoutDrawing:
    def __init__(self,
                 pin_count,
                 type,
                 mode,
                 colors: dict = DEFAULT_COLORS,
                 prefixes: list = None,
                 shield_designator: str = None) -> None:
        self._colors = colors
        self.drawing = svg.Drawing(DEFAULT_PIN_WIDTH, DEFAULT_PIN_HEIGHT)
        self.pins = PinPattern(pin_count, type, mode, prefixes, shield_designator).to_dict()

    def update_color(self, pin: str, color: str) -> None:
        if pin in self.pins:
            value = self.pins[pin]
            value.color = color
            self.pins.update({pin: value})

    def update_net(self, pin: str, net: str) -> None:
        if pin in self.pins:
            value = self.pins[pin]
            value.net.text = net
            for color, nets in self._colors.items():
                for _net in nets:
                    if _net in net.lower().replace('\\', ''):
                        value.color = color
            self.pins.update({pin: value})

    def _update_drawing_area(self, minus_x: float, plus_x: float, y: float):
        self.drawing.width = abs(minus_x) + abs(plus_x) + 2
        self.drawing.height = y + 2
        self.drawing.view_box = (minus_x - 1, -1, self.drawing.width, self.drawing.height)

    def to_svg(self, path) -> None:
        plus_x = 0
        minus_x = 0
        y = 0
        for pin in self.pins.values():
            minus_x, plus_x = (min([minus_x, pin.width]), max([plus_x, pin.width]))
            y = max([y, pin.y])
            for element in pin.svg_elements():
                self.drawing.append(element)
        self._update_drawing_area(minus_x, plus_x, y + DEFAULT_PIN_HEIGHT)
        self.drawing.save_svg(path)
