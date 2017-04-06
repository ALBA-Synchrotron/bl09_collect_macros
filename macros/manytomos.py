from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.tomoslib import ManyTomos

energy_def = [['energy', Type.Float, None, 'Beam energy'],
              {'min': 1}]

regions_def = [['start', Type.Float, None, 'Theta start position'],
               ['end', Type.Float, None, 'Theta end position'],
               ['theta_step', Type.Integer, 1, 'Theta step'],
               ['exp_time', Type.Float, None, 'Exposure time'],
               {'min': 1, 'max': 10}]

# name position in sample
NAME = 0

# ZP_Z position in sample
ZP_central_pos = 5
ZP_step = 6

class manytomosbase(object):
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """

    def _verify_samples(self, samples, zp_limit_neg, zp_limit_pos):
        for sample in samples:
            zp_central_pos = sample[ZP_central_pos]
            zp_step = sample[ZP_step]
            zp_pos_1 = zp_central_pos - zp_step
            zp_pos_2 = zp_central_pos
            zp_pos_3 = zp_central_pos + zp_step
            zp_positions = [zp_pos_1, zp_pos_2, zp_pos_3]
            counter = 0
            for zp_position in zp_positions:
                if zp_position < zp_limit_neg or zp_position > zp_limit_pos:
                    counter += 1
                    msg = ("The sample {0} has the zone_plate {1} out of"
                           " range. The accepted range is from %s to"
                           " %s um.") % (zp_limit_neg, zp_limit_pos)
                    raise ValueError(msg.format(sample[NAME], counter))

    def run(self, samples, filename):
        try:
            zp_limit_neg = self.getEnv("ZP_Z_limit_neg")
        except UnknownEnv:
            zp_limit_neg = float("-Inf")
        try:
            zp_limit_pos = self.getEnv("ZP_Z_limit_pos")
        except UnknownEnv:
            zp_limit_pos = float("Inf")
        self._verify_samples(samples, zp_limit_neg, zp_limit_pos)
        tomos_obj = ManyTomos(samples, filename)
        tomos_obj.generate()


class manytomos(manytomosbase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['energies', energy_def, None, 'Beam energies'],
                     ['ZP_central_pos', Type.Float, None, 'Central ZP '
                                                          'z position'],
                     ['ZP_step', Type.Float, None, 'Zone plate z step'],
                     ['sample_theta', regions_def, None, ('Regions of the'
                                                          ' theta motor')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['exp_time_ff', Type.Float, None, 'FF exposure time'],
                     ['n_images', Type.Integer, 1, ('Number of images'
                                                    ' per angle')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]

