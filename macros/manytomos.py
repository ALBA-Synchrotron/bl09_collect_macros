from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.tomoslib import ManyTomos


zone_plate_def = [['ZP_central_pos', Type.Float, None, ('Position of the zone'
                                                        ' plate motor')],
                  ['ZP_step', Type.Float, None, 'Zone plate z step'],
                  {'min': 1, 'max': 1}]

energy_def = [['ZP_central_pos', Type.Float, None, 'Zone plate central '
               'position'],
              ['ZP_step', Type.Float, None, 'Zone plate z step'],
              ['energy', Type.Float, None, 'Beam energy'],
              {'min': 1}]

regions_def = [['start', Type.Float, None, 'Theta start position'],
               ['end', Type.Float, None, 'Theta end position'],
               ['theta_step', Type.Integer, 1, 'Theta step'],
               ['exp_time', Type.Float, None, 'Exposure time'],
               {'min': 1, 'max': 10}]

# name position in sample
NAME = 0

# ZP_Z position in sample
ZP_Z = 4


class manytomosbase(object):
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """

    def _verify_samples(self, samples, zp_limit_neg, zp_limit_pos):
        for sample in samples:
            for counter, zone_plate in enumerate(sample[ZP_Z]):
                zp_central_pos = zone_plate[0]
                zp_step = zone_plate[1]
                zp_pos_1 = zp_central_pos - zp_step
                zp_pos_2 = zp_central_pos
                zp_pos_3 = zp_central_pos + zp_step
                zp_positions = [zp_pos_1, zp_pos_2, zp_pos_3] 
                for zp_position in zp_positions:
                    if zp_position < zp_limit_neg or zp_position > zp_limit_pos:
                        msg = ("The sample {0} has the zone_plate #{1} out of"
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
                     ['ZP_Z', zone_plate_def, None, ('Zone plates'
                                                     ' positions')],
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


class manytomosE(manytomosbase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['ZP_Z', energy_def, None, ('Beam energies and ZP_Z'
                                                 ' positions')],
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
