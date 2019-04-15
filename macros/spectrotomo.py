from datetime import datetime

from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.spectrotomolib import SpectroTomo


# name position in sample
DATE = 0
NAME = 1

# energy_zp position in the macro parameters
E_ZP_ZONES = 6


class spectrotomobase(object):
    """Generate TXM input file for image data collection, to perform
    spectral tomography measurements. Taking images at different energies
    at each individual angle. This allows to keep the same sample position,
    while changing energies.
    """

    today = datetime.today().strftime("%Y%m%d")
        
    def _verify_dates_names(self, samples):
        for sample in samples:
            sample_date = sample[DATE]
            sample_name = sample[NAME]
            if "_" in sample_date:
                msg = ("Date must be given in YYYYMMDD format. "
                       "It cannot contain underscore characters ('_'). "
                       "Please modify date '{0}' by a suitably formatted "
                       "date without underscores")
                raise ValueError(msg.format(sample_date))
            if "_" in sample_name:
                msg = ("Sample name must not contain underscore "
                       "characters ('_'). Please, modify sample name '{0}' "
                       "by suitably formatted name without underscores.")
                raise ValueError(msg.format(sample_name))

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
                        date_name = sample[DATE] + sample[NAME]
                        raise ValueError(msg.format(date_name, zp_position))

    def run(self, samples, filename):
        try:
            zp_limit_neg = self.getEnv("ZP_Z_limit_neg")
        except UnknownEnv:
            zp_limit_neg = float("-Inf")
        try:
            zp_limit_pos = self.getEnv("ZP_Z_limit_pos")
        except UnknownEnv:
            zp_limit_pos = float("Inf")
        self._verify_dates_names(samples)
        self._verify_samples(samples, zp_limit_neg, zp_limit_pos)
        spectrotomo_obj = SpectroTomo(samples, filename)
        spectrotomo_obj.generate()


class spectrotomo(spectrotomobase, Macro):

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

    param_def = [
        ['samples', [['date', Type.String, spectrotomobase.today, 
                      'Sample date: YYYYMMDD'],
                     ['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
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
                                                     ' acquisition')],
                     ['n_FF_images', Type.Integer, 10, 'Number of FF images']],
         None, 'List of samples'],

        ['out_file', Type.Filename, None, 'Output file'],
    ]

