from sardana.macroserver.macro import Macro, Type
from sardana.macroserver.msexception import UnknownEnv
from collectlib.tomoslib import Validator
from collectlib.tomoslib import HDF5_ManyTomos_Factory
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


class manytomosbase(object):
    """Generates TXM input file with commands to perform multi-sample tomo
    measurements.
    """

    def run(self, samples, filename):
        try:
            zp_limit_neg = self.getEnv("ZP_Z_limit_neg")
        except UnknownEnv:
            zp_limit_neg = float("-Inf")
        try:
            zp_limit_pos = self.getEnv("ZP_Z_limit_pos")
        except UnknownEnv:
            zp_limit_pos = float("Inf")

        validator_obj = Validator()
        validator_obj.verify_samples(samples, zp_limit_neg, zp_limit_pos)
        hdf5_files_factory = HDF5_ManyTomos_Factory(samples)
        hdf5_files_factory.create_hdf5_files()
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
                     ['n_FF_images', Type.Integer, 10, 'Number of FF images'],
                     ['n_images', Type.Integer, 1, ('Number of images'
                                                    ' per angle')]],
            None, 'List of samples'],
        ['out_file', Type.Filename, None, 'Output file'],
    ]

