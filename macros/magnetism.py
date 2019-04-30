from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.magnetismlib import Magnetism


# name position in sample
DATE = 0
NAME = 1

# energy_zp position in the macro parameters
E_ZP_ZONES = 6


class magnetismbase(object):
    """Generate TXM input file for image data collection, to perform
    magnetism tomography measurements, using the dichroism.
    Taking images at different JJ offset positions at each individual angle.
    Many repetitions for each angle are allowed.
    This allows to keep the same sample position, while changing
    the light polarization by means of moving the JJ slit positions.
    """

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

    def run(self, samples, filename):
        self._verify_dates_names(samples)
        spectrotomo_obj = SpectroTomo(samples, filename)
        spectrotomo_obj.generate()


class magnetism(magnetismbase, Macro):

    energy_zp_def = [['jj_up', Type.Float, None, 'JJ up position'],
                     ['jj_down', Type.Float, None, 'JJ down position'],
                     {'min': 1}]

    theta_def = [['theta_start', Type.Float, None, 'Theta start position'],
                 ['theta_end', Type.Float, None, 'Theta end position'],
                 ['theta_step', Type.Integer, 1, 'Theta step'],
                 ['exptime', Type.Float, 1, 'Exposure time'],
                 {'min': 1}]

    param_def = [
        ['samples', [['date', Type.String, None, 'Sample date: YYYYMMDD'],
                     ['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['theta_regions', theta_def, None, ('Regions for the'
                                                         'tilt sample '
                                                         'rotation')],
                     ['jj_regions', jj_def, None, 'JJ regions'],
                     ['n_images', Type.Integer, 1, ('Number of images'
                                                    ' per angle')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['exptime_FF', Type.Float, 1, 'FF Exposure time'],
                     ['n_FF_images', Type.Integer, 10, 'Number of FF images']],
         None, 'List of samples'],

        ['out_file', Type.Filename, None, 'Output file']
    ]
