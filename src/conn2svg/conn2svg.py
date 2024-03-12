# [TODO] to refactor entire module

import drawsvg as svg
from ._tooling import FontTooling

DEFAULT_COLORS = [{'#2f75b5': 'gnd'}]
DEFAULT_COLOR = '#eeeeee'
DEFAULT_PIN_WIDTH = 20
DEFAULT_PIN_HEIGHT = 20
DEFAULT_FONT_FAMILY = 'Arial'

class Params:
    def __init__(self,
                 x: int = None,
                 y: int = None,
                 color: str = DEFAULT_COLOR,
                 net: str = '',
                 net_anchor: str = 'start') -> None:
        self.x = x
        self.y = y
        self.color = color
        self.net = net
        self.net_anchor = net_anchor

    def to_dict(self):
        return {'x': self.x,
                'y': self.y,
                'color': self.color,
                'net': self.net,
                'net_anchor': self.net_anchor}

    def __str__(self) -> str:
        return str(self.to_dict())


class ColRow:
    def __init__(self, column: int, row: int) -> None:
        self._column = column
        self._row = row

    @property
    def column(self) -> int:
        return self._column

    @property
    def row(self) -> int:
        return self._row
    
    def __str__(self) -> str:
        return str([self._column, self._row])


class Pinmap:
    def __init__(self, pincount: int,
                 rows: int,
                 type: str,
                 mode: str,
                 prefixes: list = None,
                 shield_pin: str = None) -> None:
        self._items = {}
        self._pin_pattern(pincount, rows, type, prefixes, mode)
        if rows == 1:
            self._xy_net_anchor_pattern_1(pincount)
        elif rows%2 == 0:
            self._xy_net_anchor_pattern_2(pincount, shield_pin, prefixes)

    def to_dict(self) -> dict:
        return self._items

    def _pin_pattern(self, pincount: int, rows: int, type: str, prefixes: list, mode: str):
        # [TODO] to refactor probably extract it to another class
        pinlist = []
        pinlist = list(range(1, pincount + 1 , 1))
        if type == 'z' and rows == 2:
            if mode == 'lr-tb' or mode == 'rl-bt':
                if mode == 'rl-bt':
                    pinlist.reverse()
            elif mode == 'rl-tb' or mode == 'lr-bt':
                pinnumber = 0
                while pinnumber < pincount:
                    even = pinlist[pinnumber]
                    pinlist[pinnumber] = pinlist[pinnumber + 1]
                    pinlist[pinnumber + 1] = even
                    pinnumber += 2
                if mode == 'lr-bt':
                    pinlist.reverse()
            else:
                raise ValueError("Unknown Pinmap mode: " + str(mode))
        elif type == None and rows == 1:
            if mode == 'tb':
                pass
            elif mode == 'bt':
                pinlist.reverse()
            else:
                raise ValueError("Unknown Pinmap mode: " + str(mode))
        elif len(prefixes) and type == 'z':
            old_pinlist = pinlist
            pinlist = []
            for pin_number in old_pinlist:
                for prefix in prefixes:
                    pinlist.append(str(prefix) + str(pin_number))
            if mode == 'tb-lr':
                pass
            elif mode == 'tb-rl':
                pinnumber = 0
                while pinnumber < pincount:
                    even = pinlist[pinnumber]
                    pinlist[pinnumber] = pinlist[pinnumber + 1]
                    pinlist[pinnumber + 1] = even
                    pinnumber += 2
            else:
                raise ValueError("Unknown Pinmap mode: " + str(mode))
        else:
            raise ValueError("Unknown Pinmap type: " + str(type))

        for pinnumber in pinlist:
            self._items.update({(str(pinnumber)): Params()})

    def _xy_net_anchor_pattern_1(self, pincount: int):
        # [TODO] to refactor probably extract it to another class
        col_row = []
        for pinnumber in range(1, pincount + 1 , 1):
            col_row.append(ColRow(0, pinnumber-1))
        
        i = 0
        # max_y = 0
        for pin, params in self._items.items():
            params.x = col_row[i].column * DEFAULT_PIN_WIDTH
            params.y = col_row[i].row * DEFAULT_PIN_HEIGHT
            params.net_anchor = 'start'
            self._items.update({pin: params})
            i += 1

    def _xy_net_anchor_pattern_2(self, pincount: int, shield_pin: str, prefixes: list):
        # [TODO] to refactor probably extract it to another class
        col_row = []
        column = -1
        row = 0
        prefixcount = 1
        if len(prefixes):
            prefixcount = len(prefixes)
        for pinnumber in range(1, prefixcount * pincount + 1 , 1):
            col_row.append(ColRow(column, row))
            if (pinnumber - 1) % 2:
                row += 1
            if column == 0:
                column = -1
            else:
                column = 0

        i = 0
        max_y = 0
        for pin, params in self._items.items():
            params.x = col_row[i].column * DEFAULT_PIN_WIDTH
            params.y = col_row[i].row * DEFAULT_PIN_HEIGHT
            max_y = max([max_y, params.y])
            if i % 2:
                params.net_anchor = 'start'
            else:
                params.net_anchor = 'end'
            self._items.update({pin: params})
            i += 1
        
        column = -1
        if not shield_pin == None and len(shield_pin):
            params = Params(x = column * DEFAULT_PIN_WIDTH,
                            y = max_y + DEFAULT_PIN_HEIGHT,
                            net_anchor = 'start')
            self._items.update({shield_pin: params})

    def __str__(self) -> str:
        return str([{pin: str(params)} for pin, params in self._items.items()])


class PinoutDrawing:
    def __init__(self,
                 pincount,
                 rows,
                 type,
                 mode,
                 prefixes: list = None,
                 colors=DEFAULT_COLORS,
                 shield_pin: str = None) -> None:
        self._shield_pin = shield_pin
        self._pin_width = DEFAULT_PIN_WIDTH
        self._pin_height = DEFAULT_PIN_HEIGHT
        self._drawing = svg.Drawing(self._pin_width, self._pin_height)
        self._colors = colors
        self.pinmap = Pinmap(pincount, rows, type, mode, prefixes, shield_pin)
        self._origin_plus_x = 0
        self._origin_minus_x = 0

    def draw_pin(self, x: float, y: float, bg_color: str, name: str, net: str, net_anchor: str):
        offset = 0
        flip = 1
        if net_anchor == 'start':
            offset = self._pin_width
        elif net_anchor == 'end':
            flip = -1

        font_size = self._pin_height * 0.50

        text_color = 'white'
        if self._is_color_bright(bg_color):
            text_color = 'black'

        net_x = x + flip * (self._pin_width / 4) + offset
        name_x = x + self._pin_width / 2
        pin_width = self._pin_width
        if name == self._shield_pin:
            pin_width *= 2
            name_x = 0
            net_x += self._pin_width
        self._drawing.append(svg.Rectangle(x=x,
                                           y=y,
                                           width=pin_width,
                                           height=self._pin_height,
                                           stroke='black',
                                           fill=bg_color))
        self._drawing.append(svg.Text(text = name,
                                      font_size = str(font_size) + 'px',
                                      x = name_x,
                                      y = y + self._pin_height / 2 + self._pin_height * 0.15,
                                      font_family = DEFAULT_FONT_FAMILY,
                                      text_anchor = 'middle',
                                      fill = text_color))

        net_text = svg.Text(text='',
                            font_size = str(font_size) + 'px',
                            x = net_x,
                            y = y + self._pin_height / 2 + self._pin_height * 0.15,
                            font_family = DEFAULT_FONT_FAMILY,
                            text_anchor = net_anchor)
        self._drawing.append(self._text_overline(net_text, net))

        text_width = FontTooling.calculate_text_width(net.replace('\\', ''),
                                                      font_size,
                                                      DEFAULT_FONT_FAMILY)
        
        self._update_drawing_area(net_x + flip * text_width, y + self._pin_height)

    def _update_drawing_area(self, envelope_x: float, envelope_y: float):
        self._origin_plus_x = max([self._origin_plus_x, envelope_x])
        self._origin_minus_x = min([self._origin_minus_x, envelope_x])

        self._drawing.width = abs(self._origin_minus_x) + abs(self._origin_plus_x) + 2
        self._drawing.height = max([self._drawing.height, envelope_y]) + 2
        self._drawing.view_box = (self._origin_minus_x - 1, -1,
                                  self._drawing.width,
                                  self._drawing.height)

    def _text_overline(self, text_element: svg.Text, net: str) -> svg.Text:
        # [TODO] to improve overlining algorithm: currently it overlines each letter separately
        for i in range(0, len(net), 1):
            current = net[i]
            next = None
            if i < len(net) - 1:
                next = net[i + 1]

            if next == '\\':
                text_element.append(svg.TSpan(text=current, text_decoration='overline'))
            elif not current == '\\':
                text_element.append(svg.TSpan(text=current))
        return text_element

    def _is_color_bright(self, color: str) -> bool:
        color = color.replace('#', '')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        luminance = 1 - (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def update_color(self, pin: str, color: str) -> None:
        if pin in self.pinmap._items:
            params = self.pinmap._items[pin]
            params.color = color
            self.pinmap._items.update({pin: params})

    def update_net(self, pin: str, net: str) -> None:
        if pin in self.pinmap._items:
            params = self.pinmap._items[pin]
            params.net = net
            self.pinmap._items.update({pin: params})

    def _draw_pins(self) -> None:
        for name, params in self.pinmap.to_dict().items():
            for color_nets in self._colors:
                color = list(color_nets.keys())[0]
                nets = color_nets[color]
                for net in nets:
                    if net.lower() in params.net.lower().replace('\\', ''):
                        params.color = color
            self.draw_pin(params.x, params.y, params.color, name, params.net, params.net_anchor)

    def to_svg(self, path) -> None:
        self._draw_pins()
        self._drawing.save_svg(path)

    # An old version of fitting of the drawing area withing generated SVG
    # def _autofit_drawing(self, path) -> None:
    #    command = 'inkscape --export-type="svg" --export-area-drawing -o ' + path + ' ' + path
    #    if os.name == 'nt':
    #        os.popen(command + ' 2> nul')
    #    else:
    #        os.popen(command + ' 2> /dev/null')
