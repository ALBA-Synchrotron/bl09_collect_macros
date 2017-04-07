from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.tomoslib import ManyTomos

energy_zp_def = [['energy', Type.Float, None, 'Beam energy'],
                 ['det_z', Type.Float, None, 'Detector Z position'],
                 ['zp_z', Type.Float, None, 'ZonePlate Z position'],
                 ['zp_step', Type.Float, None, 'ZonePlate step'],
                 {'min': 1}]

regions_def = [['start', Type.Float, None, 'Theta start position'],
               ['end', Type.Float, None, 'Theta end position'],
               ['theta_step', Type.Integer, 1, 'Theta step'],
               ['exp_time', Type.Float, None, 'Exposure time'],
               {'min': 1, 'max': 10}]

# name position in sample
NAME = 0

# energy_zp position in the macro parameters
E_ZP_ZONES = 4

class manytomosbase(object):
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """

    def _verify_samples(self, samples, zp_limit_neg, zp_limit_pos):
        for sample in samples:
            for counter, e_zp_zone in enumerate(sample[E_ZP_ZONES]):
                zp_central_pos = e_zp_zone[2]
                zp_step = e_zp_zone[3]
                if zp_step == 0:
                    zp_positions = [zp_central_pos]
                else:
                    zp_pos_1 = zp_central_pos - zp_step
                    zp_pos_2 = zp_central_pos
                    zp_pos_3 = zp_central_pos + zp_step
                    zp_positions = [zp_pos_1, zp_pos_2, zp_pos_3]
                for zp_position in zp_positions:
                    if zp_position < zp_limit_neg or zp_position > zp_limit_pos:
                        msg = ("The sample {0} has the zone_plate {1} out of"
                               " range. The accepted range is from %s to"
                               " %s um.") % (zp_limit_neg, zp_limit_pos)
                        raise ValueError(msg.format(sample[NAME], counter+1))

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
                     ['energy_zp', energy_zp_def, None, 'energy ZP zones'],
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

