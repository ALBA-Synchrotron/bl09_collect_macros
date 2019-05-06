from datetime import datetime

from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.magnetismlib import Magnetism


# name position in sample
DATE = 0
NAME = 1

# angular regions position
ANGULAR_REGIONS = 10

# ZP for FFs (for both jj offset positions)
FF_ZP_1 = 15
FF_ZP_2 = 16

# ZP parameter position inside angular region group
ZP_1 = 3
ZP_2 = 4

class magnetismbase(object):
    """Generate TXM input file for image data collection, to perform
    magnetism tomography measurements, using the dichroism.
    Taking images at different JJ offset positions at each individual angle.
    Many repetitions for each angle are allowed.
    This allows to keep the same sample position, while changing
    the light polarization by means of moving the JJ slit positions.
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
            zp_positions = []
            for angular_region in sample[ANGULAR_REGIONS]:
                zp_jj_offset_1 = angular_region[ZP_1]
                zp_jj_offset_2 = angular_region[ZP_2]
                zp_positions.append(zp_jj_offset_1)
                zp_positions.append(zp_jj_offset_2)
            zp_positions.append(sample[FF_ZP_1])
            zp_positions.append(sample[FF_ZP_2])
            for zp_position in zp_positions:
                if (zp_position < zp_limit_neg or
                        zp_position > zp_limit_pos):
                    msg = ("The sample {0} has the zone_plate position {1} "
                           "out of range. The accepted range is "
                           "from %s to %s um.") % (zp_limit_neg,
                                                   zp_limit_pos)
                    date_name = sample[DATE] + "_" + sample[NAME]
                    raise ValueError(msg.format(date_name, zp_position))

    def run(self, samples, filename, start):
        try:
            zp_limit_neg = self.getEnv("ZP_Z_limit_neg")
            # print(zp_limit_neg)
        except UnknownEnv:
            zp_limit_neg = float("-Inf")
            # print(zp_limit_neg)
        try:
            zp_limit_pos = self.getEnv("ZP_Z_limit_pos")
            # print(zp_limit_pos)
        except UnknownEnv:
            zp_limit_pos = float("Inf")
            # print(zp_limit_pos)

        self._verify_dates_names(samples)
        self._verify_samples(samples, zp_limit_neg, zp_limit_pos)

        magnetism_obj = Magnetism(samples, filename)
        magnetism_obj.generate()

        if start:
            #automagnetism_ds = PyTango.DeviceProxy(
            #    "testbl09/ct/TXMAutoPreprocessing")
            import PyTango
            automagnetism_ds = PyTango.DeviceProxy("BL09/CT/TXMAutoPreprocessing")
            if automagnetism_ds.State() not in [PyTango.DevState.STANDBY]:
                raise Exception("Device must be in Standby mode "
                                "to set TXM_file")
            else:
                automagnetism_ds.txm_file = filename
                automagnetism_ds.start()


class magnetism(magnetismbase, Macro):

    theta_def = [['theta_start', Type.Float, None, 'Theta start position'],
                 ['theta_end', Type.Float, None, 'Theta end position'],
                 ['theta_step', Type.Integer, 1, 'Theta step'],
                 ['zp_1', Type.Float, None, 'ZP for polarization 1'],
                 ['zp_2', Type.Float, None, 'ZP for polarization 2'],
                 ['exptime', Type.Float, 1, 'Exposure time'],
                 ['n_images', Type.Integer, 1, ('Number of images'
                                                ' per angle')],
                 {'min': 1}]

    param_def = [
        ['samples', [['date', Type.String, magnetismbase.today,
                      'Sample date: YYYYMMDD'],
                     ['name', Type.String, None, 'Sample name'],
                     ['energy', Type.Float, None, 'Initial Energy'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['jj_down_1', Type.Float, None, 'JJ down polarization 1'],
                     ['jj_up_1', Type.Float, None, 'JJ up polarization 1'],
                     ['jj_down_2', Type.Float, None, 'JJ down polarization 2'],
                     ['jj_up_2', Type.Float, None, 'JJ up polarization 2'],
                     ['angular_regions', theta_def, None, 'Angular regions'],
                     ['ff_theta', Type.Float, None, ('Position of tilt angle'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_z', Type.Float, None, ('Position of the Z motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_zp_1', Type.Float, None, 'ZPz position for JJ '
                                                   'offset position 1'],
                     ['ff_zp_2', Type.Float, None, 'ZPz position for JJ '
                                                   'offset position 2'],
                     ['ff_exptime', Type.Float, 1, 'FF Exposure time'],
                     ['ff_n_images', Type.Integer, 10, 'Number of FF images']],
         None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
        ['start', Type.Boolean, True, 'Start the Device for acquisition']
    ]
