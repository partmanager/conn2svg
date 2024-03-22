import unittest
from conn2svg import PinPattern, PinoutDrawing


class TestPinPattern(unittest.TestCase):
    def test__generate_pins(self):
        self.assertEqual(PinPattern(8, 'header', 'tb-lr').designators(),
                         ['1', '2', '3', '4', '5', '6', '7', '8'])
        self.assertEqual(PinPattern(8, 'header', 'tb-lr', ['A']).designators(),
                         ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'])
        self.assertEqual(PinPattern(8, 'header', 'tb-lr', ['A', 'B']).designators(),
                         ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'])

    def test_header_type(self):
        self.assertEqual(PinPattern(8, 'header', 'tb').designators(),
                         ['1', '2', '3', '4', '5', '6', '7', '8'])
        self.assertEqual(PinPattern(8, 'header', 'bt').designators(),
                         ['8', '7', '6', '5', '4', '3', '2', '1'])
        self.assertEqual(PinPattern(8, 'header', 'tb-lr').designators(),
                         ['1', '2', '3', '4', '5', '6', '7', '8'])
        self.assertEqual(PinPattern(8, 'header', 'tb-rl').designators(),
                         ['5', '6', '7', '8', '1', '2', '3', '4'])
        self.assertEqual(PinPattern(8, 'header', 'bt-rl').designators(),
                         ['8', '7', '6', '5', '4', '3', '2', '1'])
        self.assertEqual(PinPattern(8, 'header', 'bt-lr').designators(),
                         ['4', '3', '2', '1', '8', '7', '6', '5'])
        self.assertEqual(PinPattern(8, 'header', 'lr-tb').designators(),
                         ['1', '3', '5', '7', '2', '4', '6', '8'])
        self.assertEqual(PinPattern(8, 'header', 'lr-bt').designators(),
                         ['7', '5', '3', '1', '8', '6', '4', '2'])
        self.assertEqual(PinPattern(8, 'header', 'rl-tb').designators(),
                         ['2', '4', '6', '8', '1', '3', '5', '7'])
        self.assertEqual(PinPattern(8, 'header', 'rl-bt').designators(),
                         ['8', '6', '4', '2', '7', '5', '3', '1'])

    def test_header_type_prefixes(self):
        self.assertEqual(PinPattern(8, 'header', 'tb-lr', ['A', 'B']).designators(),
                         ['A1', 'A2', 'A3', 'A4',
                          'B1', 'B2', 'B3', 'B4'])
        self.assertEqual(PinPattern(8, 'header', 'tb-rl', ['A', 'B']).designators(),
                         ['B1', 'B2', 'B3', 'B4',
                          'A1', 'A2', 'A3', 'A4'])
        self.assertEqual(PinPattern(8, 'header', 'bt-rl', ['A', 'B']).designators(),
                         ['B4', 'B3', 'B2', 'B1',
                          'A4', 'A3', 'A2', 'A1'])
        self.assertEqual(PinPattern(8, 'header', 'bt-lr', ['A', 'B']).designators(),
                         ['A4', 'A3', 'A2', 'A1',
                          'B4', 'B3', 'B2', 'B1'])

    def test_dsub_type(self):
        self.assertEqual(PinPattern(9, 'dsub', 'tb-lr').designators(),
                         ['1', '2', '3', '4', '5',
                          '6', '7', '8', '9'])
        self.assertEqual(PinPattern(15, 'dsub', 'tb-lr').designators(),
                         ['1', '2', '3', '4', '5', '6', '7', '8',
                          '9', '10', '11', '12', '13', '14', '15'])

        self.assertEqual(PinPattern(9, 'dsub', 'bt-rl').designators(),
                         ['9', '8', '7', '6',
                          '5', '4', '3', '2', '1'])
        self.assertEqual(PinPattern(15, 'dsub', 'bt-rl').designators(),
                         ['15', '14', '13', '12', '11', '10', '9', 
                          '8', '7', '6', '5', '4', '3', '2', '1'])

        self.assertEqual(PinPattern(9, 'dsub', 'bt-lr').designators(),
                         ['5', '4', '3', '2', '1',
                          '9', '8', '7', '6'])
        self.assertEqual(PinPattern(15, 'dsub', 'bt-lr').designators(),
                         ['8', '7', '6', '5', '4', '3', '2', '1',
                          '15', '14', '13', '12', '11', '10', '9'])

        self.assertEqual(PinPattern(9, 'dsub', 'tb-rl').designators(),
                         ['6', '7', '8', '9',
                          '1', '2', '3', '4', '5'])
        self.assertEqual(PinPattern(15, 'dsub', 'tb-rl').designators(),
                         ['9', '10', '11', '12', '13', '14', '15',
                          '1', '2', '3', '4', '5', '6', '7', '8'])

    def _template_test_pin_xy(self, pin_count: int, type: str, mode: str):
        return [[pin.x, pin.y] for pin in PinPattern(pin_count, type, mode)._pins]

    def test_pin_xy(self):
        header_1row = [[-20, 0], [-20, 20], [-20, 40], [-20, 60], [-20, 80], [-20, 100], [-20, 120], [-20, 140]]
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'tb'), header_1row)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'bt'), header_1row)

        header_2rows = [[-20, 0], [-20, 20], [-20, 40], [-20, 60],
                        [0, 0], [0, 20], [0, 40], [0, 60]]
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'tb-lr'), header_2rows)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'tb-rl'), header_2rows)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'bt-rl'), header_2rows)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'bt-lr'), header_2rows)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'lr-tb'), header_2rows)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'lr-bt'), header_2rows)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'rl-tb'), header_2rows)
        self.assertEqual(self._template_test_pin_xy(8, 'header', 'rl-bt'), header_2rows)

        dsub_1left = [[-20, 0], [-20, 20], [-20, 40], [-20, 60], [-20, 80],
                          [0, 10.0], [0, 30.0], [0, 50.0], [0, 70.0]]
        self.assertEqual(self._template_test_pin_xy(9, 'dsub', 'tb-lr'), dsub_1left)
        self.assertEqual(self._template_test_pin_xy(9, 'dsub', 'bt-lr'), dsub_1left)

        dsub_1right = [[-20, 10], [-20, 30], [-20, 50], [-20, 70], 
                  [0, 0], [0, 20.0], [0, 40.0], [0, 60.0], [0, 80.0]]
        self.assertEqual(self._template_test_pin_xy(9, 'dsub', 'bt-rl'), dsub_1right)
        self.assertEqual(self._template_test_pin_xy(9, 'dsub', 'tb-rl'), dsub_1right)

    def test_svg_drawing_elements(self):
        colors = {'#ff0000': ['3.3'],
                  '#00ff00': ['can'],
                  '#0000ff': ['gnd']}
        drawing = PinoutDrawing(4, 'header', 'tb', colors)
        drawing.update_net('1', 'GND')
        drawing.update_net('2', 'CAN_H')
        drawing.update_net('3', 'CAN_L')
        drawing.update_net('4', '+3.3V')

        elements = drawing.svg_drawing().elements

        self.assertEqual(str(type(elements[0])), "<class 'drawsvg.elements.Rectangle'>")
        self.assertEqual(elements[0].args,
                         {'fill': '#0000ff','height': 20, 'stroke': 'black', 'width': 20, 'x': -20, 'y': 0})
        self.assertEqual(str(type(elements[1])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[1].args,
                         {'fill': '#ffffff','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'middle', 'x': -10.0, 'y': 13.33})
        self.assertEqual(str(type(elements[2])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[2].args,
                         {'fill': '#000000','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'end', 'x': -25.0, 'y': 13.33})

        self.assertEqual(str(type(elements[3])), "<class 'drawsvg.elements.Rectangle'>")
        self.assertEqual(elements[3].args,
                         {'fill': '#00ff00','height': 20, 'stroke': 'black', 'width': 20, 'x': -20, 'y': 20})
        self.assertEqual(str(type(elements[4])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[4].args,
                         {'fill': '#000000','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'middle', 'x': -10.0, 'y': 33.33})
        self.assertEqual(str(type(elements[5])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[5].args,
                         {'fill': '#000000','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'end', 'x': -25.0, 'y': 33.33})

        self.assertEqual(str(type(elements[6])), "<class 'drawsvg.elements.Rectangle'>")
        self.assertEqual(elements[6].args,
                         {'fill': '#00ff00','height': 20, 'stroke': 'black', 'width': 20, 'x': -20, 'y': 40})
        self.assertEqual(str(type(elements[7])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[7].args,
                         {'fill': '#000000','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'middle', 'x': -10.0, 'y': 53.33})
        self.assertEqual(str(type(elements[8])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[8].args,
                         {'fill': '#000000','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'end', 'x': -25.0, 'y': 53.33})

        self.assertEqual(str(type(elements[9])), "<class 'drawsvg.elements.Rectangle'>")
        self.assertEqual(elements[9].args,
                         {'fill': '#ff0000','height': 20, 'stroke': 'black', 'width': 20, 'x': -20, 'y': 60})
        self.assertEqual(str(type(elements[10])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[10].args,
                         {'fill': '#ffffff','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'middle', 'x': -10.0, 'y': 73.33})
        self.assertEqual(str(type(elements[11])), "<class 'drawsvg.elements.Text'>")
        self.assertEqual(elements[11].args,
                         {'fill': '#000000','font-family': 'Arial', 'font-size': '10.0px', 'text-anchor': 'end', 'x': -25.0, 'y': 73.33})

    def _template_save_svg(self, pin_count, type, mode):
        drawing = PinoutDrawing(pin_count, type, mode)
        for i in range(1, pin_count + 1, 1):
            drawing.update_net(str(i), 'net' + str(i))
            drawing.update_color(str(i), '#' + hex(round(1118481 * i)).replace('0x', ''))
        drawing.to_svg(type + '_' + str(pin_count)+'pin_'+ mode + '.svg')

    def test_save_svg(self):
        self._template_save_svg(12, 'header', 'tb')
        self._template_save_svg(12, 'header', 'bt')
        self._template_save_svg(12, 'header', 'tb-lr')
        self._template_save_svg(12, 'header', 'tb-rl')
        self._template_save_svg(12, 'header', 'bt-rl')
        self._template_save_svg(12, 'header', 'bt-lr')
        self._template_save_svg(12, 'header', 'lr-tb')
        self._template_save_svg(12, 'header', 'lr-bt')
        self._template_save_svg(12, 'header', 'rl-tb')
        self._template_save_svg(12, 'header', 'rl-bt')
        
        self._template_save_svg(9, 'dsub', 'tb-lr')
        self._template_save_svg(9, 'dsub', 'bt-rl')
        self._template_save_svg(9, 'dsub', 'bt-lr')
        self._template_save_svg(9, 'dsub', 'tb-rl')

        self._template_save_svg(15, 'dsub', 'tb-lr')
        self._template_save_svg(15, 'dsub', 'bt-rl')
        self._template_save_svg(15, 'dsub', 'bt-lr')
        self._template_save_svg(15, 'dsub', 'tb-rl')

    def test_shield(self):
        drawing = PinoutDrawing(12, 'header', 'tb-lr', shield_designator='shld')
        for i in range(1, 13, 1):
            drawing.update_net(str(i), 'net' + str(i))
            drawing.update_color(str(i), '#' + hex(round(1118481 * i)).replace('0x', ''))
        drawing.update_net('shld', 'netSHLD')
        drawing.update_color('shld', '#0000cc')
        drawing.to_svg('header_12pin_tb-lr_shield.svg')

        drawing = PinoutDrawing(15, 'dsub', 'tb-rl', shield_designator='shld')
        for i in range(1, 16, 1):
            drawing.update_net(str(i), 'net' + str(i))
            drawing.update_color(str(i), '#' + hex(round(1118481 * i)).replace('0x', ''))
        drawing.update_net('shld', 'netSHLD')
        drawing.update_color('shld', '#0000cc')
        drawing.to_svg('dsub_15pin_tb-rl_shield.svg')
    
    def test_add_drawings(self):
        colors = {'#ff0000': ['3.3'],
                  '#00ff00': ['I2C'],
                  '#0000ff': ['gnd']}
        drawing_1 = PinoutDrawing(6, 'header', 'tb-lr', colors, ['A'])
        drawing_1.update_net('A1', '+3.3V')
        drawing_1.update_net('A2', 'I2C_SCL')
        drawing_1.update_net('A3', 'I2C_SDA')
        drawing_1.update_net('A4', 'GND')
        drawing_1.update_net('A5', 'TRIG2')
        drawing_1.update_net('A6', 'GND')

        drawing = PinoutDrawing(colors={})
        drawing += drawing_1

        colors = {'#ff3333': ['3.3'],
                  '#ffff33': ['can', 'trig'],
                  '#0000ff': ['gnd'],}
        drawing_2 = PinoutDrawing(6, 'header', 'tb-lr', colors, ['B'])
        drawing_2.update_net('B1', '+5V')
        drawing_2.update_net('B2', 'CAN_H')
        drawing_2.update_net('B3', 'CAN_L')
        drawing_2.update_net('B4', 'TRIG1')
        drawing_2.update_net('B5', 'TRIG2')
        drawing_2.update_net('B6', 'GND')
        drawing += drawing_2

        self.assertEqual(drawing._colors,
                         {'#ff0000': ['3.3'],
                          '#00ff00': ['I2C'],
                          '#0000ff': ['gnd'],
                          '#ff3333': ['3.3'],
                          '#ffff33': ['can', 'trig'],})
        
        drawing.to_svg('add.svg')


if __name__ == '__main__':
    unittest.main()
