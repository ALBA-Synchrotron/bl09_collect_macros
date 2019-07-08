import numpy as np
from datetime import datetime

from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.autotomolib import AutoTomosClass


regions_def = [['start', Type.Float, None, 'Theta start position'],
               ['end', Type.Float, None, 'Theta end position'],
               ['theta_step', Type.Integer, 1, 'Theta step'],
               ['exp_time', Type.Float, None, 'Exposure time'],
               ['zp_z', Type.Float, None, 'ZonePlate Z position'],
               ['zp_step', Type.Float, 0, 'ZonePlate step'],
               ['num_zps', Type.Float, 1, 'Number of ZonePlate positions'],
               ['n_images', Type.Integer, 1, 'Number of images per angle'],
               {'min': 1, 'max': 200}]

energy_zp_def = [['energy', Type.Float, None, 'Beam energy'],
                 ['det_z', Type.Float, None, 'Detector Z position'],
                 ['sample_theta', regions_def, None, ('Regions of the'
                                                      ' theta motor')],
                 {'min': 1}]

# name position in sample
DATE = 0
NAME = 1

# energy-ZP regions
ENERGIES_ZP = 5

# angular regions position in the macro parameters
ENERGY = 0
DET_Z = 1
ANGULAR_REGIONS = 2


class autotomobase(object):
    """Generates a TXM input file with commands to perform multi-sample tomo
    data collection using the XMController Microscope Software.
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
            for counter, energy_region in enumerate(sample[ENERGIES_ZP]):
                for cnt, angular_region in enumerate(
                        energy_region[ANGULAR_REGIONS]):
                    zp_central_pos = angular_region[4]
                    zp_step = angular_region[5]
                    num_zps = angular_region[6]
                    if zp_step == 0:
                        zp_positions = [zp_central_pos]
                    else:
                        start = zp_central_pos - zp_step * (num_zps - 1) / 2.0
                        stop = zp_central_pos + zp_step * (num_zps - 1) / 2.0
                        zp_positions = np.linspace(start, stop, num_zps)
                    for zp_position in zp_positions:
                        if (zp_position < zp_limit_neg or
                                zp_position > zp_limit_pos):
                            msg = ("The sample {0} has the zone_plate {1} "
                                   "out of range. The accepted range is "
                                   "from %s to %s um.") % (zp_limit_neg,
                                                           zp_limit_pos)
                            date_name = sample[DATE] + sample[NAME]
                            raise ValueError(msg.format(date_name, cnt+1))

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

        tomos_obj = AutoTomosClass(samples, filename)
        tomos_obj.generate()

        if start:
            import PyTango
            # autotomods = PyTango.DeviceProxy(
            #   "testbl09/ct/TXMAutoPreprocessing")
            autotomods = PyTango.DeviceProxy("BL09/CT/TXMAutoPreprocessing")
            if autotomods.State() not in [PyTango.DevState.STANDBY]:
                raise Exception("Device must be in Standby mode "
                                "to set TXM_file")
            else:
                autotomods.txm_file = filename
                autotomods.start()


class autotomo(autotomobase, Macro):

    param_def = [
        ['samples', [['date', Type.String, autotomobase.today, 
                      'Sample date: YYYYMMDD'],
                     ['name', Type.String, None, 'Sample name'],
                     ['pos_x', Type.Float, None, 'Position of the X motor'],
                     ['pos_y', Type.Float, None, 'Position of the Y motor'],
                     ['pos_z', Type.Float, None, 'Position of the Z motor'],
                     ['energy_zp', energy_zp_def, None, 'energy ZP zones'],
                     ['ff_pos_x', Type.Float, None, ('Position of the X motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['ff_pos_y', Type.Float, None, ('Position of the Y motor'
                                                     ' for the flat field'
                                                     ' acquisition')],
                     ['exp_time_ff', Type.Float, None, 'FF exposure time'],
                     ['n_FF_images', Type.Integer, 10, 'Number of FF images']
                     ],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
        ['start', Type.Boolean, True, 'Start the Device for acquisition']
    ]

