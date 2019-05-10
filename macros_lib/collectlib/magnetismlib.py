import time
import numpy as np
from txmcommands import GenericTXMcommands


DATE = 0
NAME = 1
ENERGY = 2
POS_X = 3
POS_Y = 4
POS_Z = 5
JJ_DOWN_1 = 6
JJ_UP_1 = 7
JJ_DOWN_2 = 8
JJ_UP_2 = 9
ANGULAR_REGIONS = 10
FF_THETA = 11
FF_POS_X = 12
FF_POS_Y = 13
FF_POS_Z = 14
FF_ZP_1 = 15
FF_ZP_2 = 16
FF_EXPTIME = 17
FF_N_IMAGES = 18

THETA_START = 0
THETA_END = 1
THETA_STEP = 2
ZP_1 = 3
ZP_2 = 4
EXPTIME = 5
N_IMAGES = 6


FILE_NAME = 'magnetism.txt'

samples = [
    [
        '20180531',  # date
        'sample1',  # name
        520.0,  # energy
        -838.00,  # pos x
        -881.00,  # pos y
        -349.30,  # pos z
        -2.2,  # jj_down_1
        0.9,  # jj_up_1
        -6.2,  # jj_down_2
        -3.1,  # jj_up_2
        [  # angular regions
            [
                -10,  # start
                10,  # end
                10,  # theta step
                111,  # zp_for_jjs_polarization_1
                222,  # zp_for_jjs_polarization_2
                1,  # exposure time
                3  # Num Images
            ],
            [
                15,  # start
                21,  # end
                2,  # theta step
                333,  # zp_for_jjs_polarization_1
                444,  # zp_for_jjs_polarization_2
                3,  # exposure time
                4  # Num Images
            ],
        ],
        -45,  # FlatField theta
        12,  # FlatField position x
        12,  # FlatField position y
        12,  # FlatField position z
        -11000,  # FlatField ZP position for JJ 1
        -11040,  # FlatField ZP position for JJ 2
        2,  # Exposure time FF
        10,  # Num FF images
    ],
]


class Magnetism(GenericTXMcommands):

    def __init__(self, samples=None, file_name=None):
        GenericTXMcommands.__init__(self, file_name=file_name)
        self.samples = samples
        self.jj_offset_1 = None
        self.jj_offset_2 = None
        self.folder_num = 1

    def collect(self, jj_offset, sample_date=None, sample_name=None,
                theta=None):
        if sample_date is None:
            sample_date = self.current_sample_date
        if sample_name is None:
            sample_name = self.current_sample_name
        if theta is None:
            theta = self.current_theta
        base_name = ('%s_%s_%.2f_%.1f' % (sample_date, sample_name,
                                          jj_offset, theta))
        extension = 'xrm'
        if (self._repetitions == 0 or self._repetitions == 1 or
                self._repetitions is None):
            file_name = '%s.%s' % (base_name, extension)
            self.destination.write('collect %s\n' % file_name)
        else:
            for repetition in range(self._repetitions):
                file_name = '%s_%d.%s' % (base_name, repetition, extension)
                self.destination.write('collect %s\n' % file_name)

    def collect_FF(self, sample, jj_offset_1, jj_offset_2):
        # Execute flat field acquisitions #
        self.moveTheta(0)

        # Select folder to store raw data images
        self.move_select_action(5)
        self.move_target_folder(self.folder_num)
        ###

        self.moveTheta(sample[FF_THETA])
        self.go_to_sample_xyz_pos(sample[FF_POS_X], sample[FF_POS_Y],
                                  sample[FF_POS_Z])
        self.setExpTime(sample[FF_EXPTIME])
        self.go_to_jj(sample[JJ_DOWN_1], sample[JJ_UP_1], sample[FF_ZP_1])
        sample_name = '%s_%s_%.2f' % (self.current_sample_date,
                                      self.current_sample_name, jj_offset_1)
        for i in range(sample[FF_N_IMAGES]):
            self.destination.write('collect %s_FF_%d.xrm\n' % (sample_name, i))
        self.go_to_jj(sample[JJ_DOWN_2], sample[JJ_UP_2], sample[FF_ZP_2])
        sample_name = '%s_%s_%.2f' % (self.current_sample_date,
                                      self.current_sample_name, jj_offset_2)
        for i in range(sample[FF_N_IMAGES]):
            self.destination.write('collect %s_FF_%d.xrm\n' % (sample_name, i))

    def collect_sample(self, sample):
        file_name_collect = '{0}_collect.{1}'.format(
            *self.file_name.rsplit('.', 1))
        file_name_ff = '{0}_ff.{1}'.format(*self.file_name.rsplit('.', 1))

        self.current_energy = sample[ENERGY]
        self.moveEnergy(self.current_energy)
        self.current_sample_date = sample[DATE]
        self.current_sample_name = sample[NAME]
        self.go_to_sample_xyz_pos(sample[POS_X],
                                  sample[POS_Y],
                                  sample[POS_Z])

        # Initialization #
        jj_offset_1 = (sample[JJ_UP_1] + sample[JJ_DOWN_1]) / 2.0
        jj_offset_2 = (sample[JJ_UP_2] + sample[JJ_DOWN_2]) / 2.0
        self.jj_offset_1 = round(jj_offset_1, 2)
        self.jj_offset_2 = round(jj_offset_2, 2)
        angular_regions = sample[ANGULAR_REGIONS]
        self.go_to_jj(sample[JJ_DOWN_1], sample[JJ_UP_1],
                      angular_regions[0][ZP_1])
        ##################

        count_jj = 0
        for angular_region in angular_regions:
            self._repetitions = angular_region[N_IMAGES]
            angle_start = angular_region[THETA_START]
            angle_end = angular_region[THETA_END]
            angle_step = angular_region[THETA_STEP]
            exp_time = angular_region[EXPTIME]
            msg = "Region start must be different than end"
            assert angle_start != angle_end, msg
            angle_step = abs(angle_step)
            if angle_end - angle_start < 1:
                angle_step *= -1
            positions = np.arange(angle_start, angle_end, angle_step)
            positions = np.append(positions, angle_end)
            self.setExpTime(exp_time)

            # Acquisition of many images at each angle an jj offset position.
            for theta in positions:
                count_jj += 1
                # Select folder to store raw data images
                self.move_select_action(5)
                self.move_target_folder(self.folder_num)
                self.folder_num += 1
                ###
                self.moveTheta(theta)
                if count_jj % 2 == 1:
                    self.collect(jj_offset_1)
                    self.go_to_jj(sample[JJ_DOWN_2], sample[JJ_UP_2],
                                  angular_region[ZP_2])
                    self.collect(jj_offset_2)
                else:
                    self.collect(jj_offset_2)
                    self.go_to_jj(sample[JJ_DOWN_1], sample[JJ_UP_1],
                                  angular_region[ZP_1])
                    self.collect(jj_offset_1)
                self.move_select_target(1, theta)

        self.collect_FF(sample, jj_offset_1, jj_offset_2)
        self.go_to_sample_xyz_pos(sample[POS_X], sample[POS_Y], sample[POS_Z])
        self.moveTheta(0)

        self.destination.close()
        # Copy file_name contents in file_name_collect
        # File to be loaded in TXM to collect raw images.
        # Second file to be loaded in TXM
        with open(file_name_collect, 'w') as img_collect_file:
            with open(self.file_name, 'r') as db_file:
                for line in db_file:
                    img_collect_file.write(line.replace('_FF_', '_FF_END_'))

        # File to be loaded in TXM and collect FF images
        # First file to be loaded in TXM
        ff_file = open(file_name_ff, 'w')
        self.destination = ff_file
        with ff_file:
            self.collect_FF(sample, jj_offset_1, jj_offset_2)
        ff_file.close()

    def collect_data(self):
        self.setBinning()
        # Select Pipeline according DS TXMAutoPreprocessing
        self.move_select_action(0)
        # Target: TOMO pipeline according DS TXMAutoPreprocessing
        self.move_target_workflow(0)
        self.wait(5)
        num = 0
        for sample in self.samples:
            num += 1
            self.collect_sample(sample)
            # wait some time between samples (don't wait for last loop)
            if num < len(self.samples):
                self.wait(180)

        # TODO: In case of magnetism, END action creates the stacks; which
        # have to be created after the preprocessing of all angles, and for
        # each of the samples. Only one sample at a time
        # can be preprocessed currently with magnetism workflow.
        # If the acquisition and preprocessing is not finished, the stacks
        # should not be done. This action has to be managed in the DS
        # txmautopreprocessing, and currently, it is most probably,
        # not managed.

        # TODO: Check numbers for magnetism END action

        # Select END action according DS TXMAutoPreprocessing:
        # self.move_select_action(4)
        # self.move_target_workflow(0)
        ####


if __name__ == '__main__':
    magnetism_obj = Magnetism(samples, FILE_NAME)
    magnetism_obj.generate()
