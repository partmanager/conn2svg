import unittest
from conn2svg import PinPattern, PinoutDrawing


class TestPinPattern(unittest.TestCase):
    def test__generate_pins(self):
        pattern = PinPattern(8, 'header', 'tb-lr')
        self.assertEqual(pattern.designators(), ['1', '2', '3', '4', '5', '6', '7', '8'])

        pattern = PinPattern(8, 'header', 'tb-lr', ['A'])
        self.assertEqual(pattern.designators(), ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'])

        pattern = PinPattern(8, 'header', 'tb-lr', ['A', 'B'])
        self.assertEqual(pattern.designators(), ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'])

    def test_header_type(self):
        pattern = PinPattern(8, 'header', 'tb')
        self.assertEqual(pattern.designators(), ['1', '2', '3', '4', '5', '6', '7', '8'])

        pattern = PinPattern(8, 'header', 'bt')
        self.assertEqual(pattern.designators(), ['8', '7', '6', '5', '4', '3', '2', '1'])

        pattern = PinPattern(8, 'header', 'tb-lr')
        self.assertEqual(pattern.designators(), ['1', '2', '3', '4', '5', '6', '7', '8'])

        pattern = PinPattern(8, 'header', 'tb-rl')
        self.assertEqual(pattern.designators(), ['5', '6', '7', '8', '1', '2', '3', '4'])

        pattern = PinPattern(8, 'header', 'bt-rl')
        self.assertEqual(pattern.designators(), ['8', '7', '6', '5', '4', '3', '2', '1'])

        pattern = PinPattern(8, 'header', 'bt-lr')
        self.assertEqual(pattern.designators(), ['4', '3', '2', '1', '8', '7', '6', '5'])

        pattern = PinPattern(8, 'header', 'lr-tb')
        self.assertEqual(pattern.designators(), ['1', '3', '5', '7', '2', '4', '6', '8'])

        pattern = PinPattern(8, 'header', 'lr-bt')
        self.assertEqual(pattern.designators(), ['7', '5', '3', '1', '8', '6', '4', '2'])

        pattern = PinPattern(8, 'header', 'rl-tb')
        self.assertEqual(pattern.designators(), ['2', '4', '6', '8', '1', '3', '5', '7'])

        pattern = PinPattern(8, 'header', 'rl-bt')
        self.assertEqual(pattern.designators(), ['8', '6', '4', '2', '7', '5', '3', '1'])

    def test_header_type_prefixes(self):
        pattern = PinPattern(8, 'header', 'tb-lr', ['A', 'B'])
        self.assertEqual(pattern.designators(), ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'])

        pattern = PinPattern(8, 'header', 'tb-rl', ['A', 'B'])
        self.assertEqual(pattern.designators(), ['B1', 'B2', 'B3', 'B4', 'A1', 'A2', 'A3', 'A4'])

        pattern = PinPattern(8, 'header', 'bt-rl', ['A', 'B'])
        self.assertEqual(pattern.designators(), ['B4', 'B3', 'B2', 'B1', 'A4', 'A3', 'A2', 'A1'])

        pattern = PinPattern(8, 'header', 'bt-lr', ['A', 'B'])
        self.assertEqual(pattern.designators(), ['A4', 'A3', 'A2', 'A1', 'B4', 'B3', 'B2', 'B1'])

    def test_dsub_type(self):
        pattern = PinPattern(9, 'dsub', 'tb-lr')
        self.assertEqual(pattern.designators(), ['1', '2', '3', '4', '5', '6', '7', '8', '9'])

        pattern = PinPattern(9, 'dsub', 'bt-rl')
        self.assertEqual(pattern.designators(), ['9', '8', '7', '6', '5', '4', '3', '2', '1'])

        pattern = PinPattern(9, 'dsub', 'bt-lr')
        self.assertEqual(pattern.designators(), ['5', '4', '3', '2', '1', '9', '8', '7', '6', ])

        pattern = PinPattern(9, 'dsub', 'tb-rl')
        self.assertEqual(pattern.designators(), ['6', '7', '8', '9', '1', '2', '3', '4', '5'])

    def _template(self, pin_count, type, mode):
        drawing = PinoutDrawing(pin_count, type, mode)
        for i in range(1, pin_count + 1, 1):
            drawing.update_net(str(i), 'net' + str(i))
            drawing.update_color(str(i), '#' + hex(round(1118481 * i)).replace('0x', ''))
        drawing.to_svg(type + '_' + str(pin_count)+'pin_'+ mode + '.svg')

    def test_save_svg(self):
        self._template(12, 'header', 'tb')
        self._template(12, 'header', 'bt')
        self._template(12, 'header', 'tb-lr')
        self._template(12, 'header', 'tb-rl')
        self._template(12, 'header', 'bt-rl')
        self._template(12, 'header', 'bt-lr')
        self._template(12, 'header', 'lr-tb')
        self._template(12, 'header', 'lr-bt')
        self._template(12, 'header', 'rl-tb')
        self._template(12, 'header', 'rl-bt')
        
        # self._template(15, 'dsub', 'tb-lr')
        # self._template(15, 'dsub', 'bt-rl')
        # self._template(15, 'dsub', 'bt-lr')
        # self._template(15, 'dsub', 'tb-rl')

    def test_shield(self):
        drawing = PinoutDrawing(12, 'header', 'tb-lr', shield_designator='shld')
        for i in range(1, 13, 1):
            drawing.update_net(str(i), 'net' + str(i))
            drawing.update_color(str(i), '#' + hex(round(1118481 * i)).replace('0x', ''))
        drawing.update_net('shld', 'netSHLD')
        drawing.update_color('shld', '#0000cc')
        drawing.to_svg('header_12pin_tb-lr_shield.svg')


if __name__ == '__main__':
    unittest.main()
