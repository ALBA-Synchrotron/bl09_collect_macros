from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.spectrotomolib import SpectroTomo


sample_pos_def = [['pos_x', Type.Float, None, 'Position of the X motor'],
                  ['pos_y', Type.Float, None, 'Position of the Y motor'],
                  ['pos_z', Type.Float, None, 'Position of the Z motor'],
                  {'min': 1}]

energy_zp_def = [['energy', Type.Float, None, 'Beam energy'],
                 ['det_z', Type.Float, None, 'Detector Z position'],
                 ['zp_z', Type.Float, None, 'ZonePlate Z position'],
                 ['zp_step', Type.Float, 0, 'ZonePlate step'],
                 ['exptime_FF', Type.Float, 1, 'FF Exposure time'],
                 {'min': 1}]

theta_def = [['theta_start', Type.Float, None, 'Theta start position'],
             ['theta_end', Type.Float, None, 'Theta end position'],
             ['theta_step', Type.Integer, 1, 'Theta step'],
             ['exptime', Type.Float, 1, 'Exposure time'],
             {'min': 1}]

# name position in sample
NAME = 0

# energy_zp position in the macro parameters
E_ZP_ZONES = 4


class spectrotomobase(object):
    """Generate TXM input file for image data collection, to perform
    spectral tomography measurements. Taking images at different energies
    at each individual angle. This allows to keep the same sample position,
    while changing energies.
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
                        raise ValueError(msg.format(sample[NAME], zp_position))

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
        tomos_obj = SpectroTomo(samples, filename)
        tomos_obj.generate()


class spectrotomo(spectrotomobase, Macro):

    param_def = [
        ['samples', [['name', Type.String, None, 'Sample name'],
                     ['sample_regions',  sample_pos_def, None, ('Regions of the'
                                                                ' sample to be'
                                                                ' imaged')],
                     ['theta_regions', theta_def, None, ('Regions for the'
                                                         'tilt sample '
                                                         'rotation')],

                     ['energy_regions', energy_zp_def, None, ('energy ZP '
                                                              'regions')],

                     ['n_images', Type.Integer, 1, ('Number of images'
                                                    ' per angle')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                                                     ' for the flat field'
                                                     ' acquisition')]],
         None, 'List of samples'],

        ['out_file', Type.Filename, None, 'Output file'],
    ]