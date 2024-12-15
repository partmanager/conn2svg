import drawsvg as svg
from ._tooling import FontTooling

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
    def minx_width(self):
        width = self.net.width() + 1.25 * DEFAULT_PIN_WIDTH
        min_x = self.net.x - 1.25 * DEFAULT_PIN_WIDTH
        if self.net.anchor == 'end':
            min_x = self.net.x - self.net.width()
        return (min_x, width)

    def svg_elements(self) -> list:
        if not self._is_color_bright(self.color):
            self.designator.color = '#ffffff'
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
    MATRIX = {'header': {'tb': [[], 'header_dsub'],
                         'bt': [['reverse'], 'header_dsub'],
                         'tb-lr': [[], 'header_dsub'],
                         'tb-rl': [['flip_half'], 'header_dsub'],
                         'bt-rl': [['reverse'], 'header_dsub'],
                         'bt-lr': [['reverse', 'flip_half'], 'header_dsub'],
                         'lr-tb': [['odd_even'], 'header_dsub'],
                         'lr-bt': [['odd_even', 'flip_half', 'reverse'], 'header_dsub'],
                         'rl-tb': [['odd_even', 'flip_half'], 'header_dsub'],
                         'rl-bt': [['odd_even', 'reverse'], 'header_dsub']},
              'dsub': {'tb-lr': [[], 'header_dsub'],
                       'bt-rl': [['reverse'], 'header_dsub'],
                       'bt-lr': [['reverse', 'flip_dsub'], 'header_dsub'],
                       'tb-rl': [['flip_dsub'], 'header_dsub']}}

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
                    elif transform == 'flip_dsub':
                        half = round(len(self._pins)/2 + 0.1)
                        if '-lr' in mode:
                            half = round(len(self._pins)/2 - 0.1)
                        self._pins = self._pins[half::] + self._pins[:half:]
                    else:
                        raise ValueError('Unknown pin pattern transformation:', transform)
                if modes[mode][1] == 'header_dsub':
                    self._generate_header_dsub(pin_count, type, mode, shld)
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

    def _generate_header_dsub(self, pin_count: int, type: str, mode: str, shld: str) -> None:
        x = -DEFAULT_PIN_WIDTH
        y = 0
        anchor = 'end'
        if type == 'dsub' and '-rl' in mode:
            y = DEFAULT_PIN_HEIGHT / 2
        half = False
        for i in range(0, pin_count, 1):
            self._pins[i].x = x
            self._pins[i].y = y
            self._pins[i].net.y = y + 2 * DEFAULT_PIN_HEIGHT / 3
            self._pins[i].net.x = x + DEFAULT_PIN_WIDTH * 1.25
            if anchor == 'end':
                self._pins[i].net.x = x - DEFAULT_PIN_WIDTH * 0.25
                self._pins[i].net.anchor = 'end'
            self._pins[i].designator.x = x + DEFAULT_PIN_WIDTH / 2
            self._pins[i].designator.y = y + DEFAULT_PIN_HEIGHT / 2 + DEFAULT_FONT_SIZE / 3
            self._pins[i].designator.anchor = 'middle'

            y += DEFAULT_PIN_HEIGHT
            if mode != 'tb' and mode != 'bt':
                i_offset = 1
                y_offset = 0
                if type == 'dsub':
                    if '-rl' in mode:
                        i_offset = 2
                    else:
                        y_offset = DEFAULT_PIN_HEIGHT / 2
                if not half and i + i_offset >= pin_count / 2:
                    y = y_offset
                    x = 0
                    anchor = 'start'
                    half = True
        if shld != None and len(shld):
            text_y = y + DEFAULT_PIN_HEIGHT / 2 + DEFAULT_FONT_SIZE / 3
            self._pins.append(Pin(designator=PinText(shld,
                                                     x = 0,
                                                     y = text_y,
                                                     anchor = 'middle'),
                                    net=PinText('',
                                                x = 1.25 * DEFAULT_PIN_WIDTH,
                                                y = text_y),
                                    x = -DEFAULT_PIN_WIDTH,
                                    y = y,
                                    pin_width=DEFAULT_PIN_WIDTH*2))


class PinoutDrawing:
    def __init__(self,
                 pin_count: int = None,
                 type: str = None,
                 mode: str = None,
                 colors: dict = None,
                 prefixes: list = None,
                 pin_net_pairs: dict = None,
                 shield_designator: str = None) -> None:
        self._colors = {}
        if colors != None:
            self._colors = colors
        self.pins = {}
        if pin_count != None and type != None and mode != None:
            self.pins = PinPattern(pin_count, type, mode, prefixes, shield_designator).to_dict()
            if pin_net_pairs != None:
                self.update_nets(pin_net_pairs)

    def update_nets(self, pin_net_pairs: dict) -> None:
        for pin, net in pin_net_pairs.items():
            self.update_net(pin, net)

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
                    if _net.lower() in net.lower().replace('\\', ''):
                        value.color = color
            self.pins.update({pin: value})

    def svg_drawing(self):
        drawing = svg.Drawing(DEFAULT_PIN_WIDTH, DEFAULT_PIN_HEIGHT)
        plus_x = 0
        minus_x = 0
        y = 0
        for pin in self.pins.values():
            minus_x = min([minus_x, pin.minx_width[0]])
            plus_x = max([plus_x, pin.minx_width[0] + pin.minx_width[1]])
            y = max([y, pin.y])
            for element in pin.svg_elements():
                drawing.append(element)
        drawing.width = abs(minus_x) + abs(plus_x) + DEFAULT_FONT_SIZE / 2
        drawing.height = y + DEFAULT_PIN_HEIGHT + 2
        drawing.view_box = (minus_x - 1, -1, drawing.width, drawing.height)
        return drawing

    def to_svg(self, path) -> None:
        self.svg_drawing().save_svg(path)

    def __add__(self, other):
        output = self

        if self._colors != other._colors:
            for color, nets in other._colors.items():
                if color in self._colors:
                    nets = list(dict.fromkeys(self._colors[color] + other._colors[color]))
                output._colors.update({color: nets})

        width = self.svg_drawing().width - other.svg_drawing().view_box[0]
        for designator, pin in other.pins.items():
            pin.x += width
            pin.designator.x += width
            pin.net.x += width
            output.pins.update({designator: pin})

        return output
