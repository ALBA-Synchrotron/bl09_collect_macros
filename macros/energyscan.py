from sardana.macroserver.macro import Macro, Type
from collectlib.energyscanlib import EnergyScan

energy_def = [['E_start', Type.Float, None, 'Energy start position'],
              ['E_end', Type.Float, None, 'Energy end position'],
              ['E_step', Type.Float, None, 'Energy step'],
              ['exp_time', Type.Float, None, 'Sample exposure time'],
              ['exp_time_FF', Type.Float, None, 'FF exposure time'],
              {'min': 1, 'max': 50 }]

sample_pos_def = [['pos_x', Type.Float, None, 'Position of the X motor'],
                  ['pos_y', Type.Float, None, 'Position of the Y motor'],
                  ['pos_z', Type.Float, None, 'Position of the Z motor'],
                  {'min': 1, 'max': 80 }]



class energyscanbase(object):
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """

    def run(self, samples, out_file):
        energy_scan = EnergyScan(samples, out_file)
        energy_scan.generate()


class energyscan(energyscanbase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['sample_regions',  sample_pos_def, None, ('Regions of the'
                                                                ' sample to be'
                                                                ' imaged')],
                     ['energy_regions', energy_def, None, ('Regions of the'
                         ' energy motor')],
                     ['ZP_start', Type.Float, None, 'ZP start position'],
                     ['ZP_end', Type.Float, None, 'ZP end position'],
                     ['Det_start', Type.Float, None, 'Detector start position'],
                     ['Det_end', Type.Float, None, 'Detector end position'],  
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['n_images', Type.Integer, 1, ('Number of images per '
                      'energy')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file name'],
    ]




