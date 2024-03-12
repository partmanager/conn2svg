import unittest
from netbom.netlist_readers import RinfNetlistReader
from conn2svg import PinoutDrawing
import os

DIR =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples/netlist/")

MAP = {'J_HEADER_1x2_2.54_VERTICAL': {'pincount': 2, 'rows': 1, 'type': None, 'mode': 'tb'}}
COLORS = [{'#2f75b5': 'gnd'},
          {'#dedbee': ['3.3v']}]
OVERRIDE = {'NetxD': '+3.3V'}
bom, netlist = RinfNetlistReader().bom_and_netlist_from_file(DIR + 'Altium_LED-Resistor.FRP')

def is_net_orphaned(net):
    return len(netlist[net].connections) == 1 and len(netlist[net].connections.to_dict().values()) == 1

class TestConn2svg(unittest.TestCase):
    def test_generate_svg(self):
        parts = netlist.filter_designator('J')

        for part in parts:
            part_number = bom.rows.fetch_row_by_designator(part.designator)['Part Number']
            if part_number in MAP:
                params = MAP[part_number]
                shield_pin = None
                if 'shield_pin' in params:
                    shield_pin = params['shield_pin']
                drawing = PinoutDrawing(params['pincount'],
                                                params['rows'],
                                                params['type'],
                                                params['mode'],
                                                colors=COLORS,
                                                shield_pin=shield_pin)
                
                for pin, net in part.to_dict()[part.designator].items():
                    if not is_net_orphaned(net):
                        if net in OVERRIDE:
                            drawing.update_net(pin, OVERRIDE[net])
                        else:
                            drawing.update_net(pin, net)

                drawing.to_svg(part.designator + '.svg')

if __name__ == '__main__':
    unittest.main()
