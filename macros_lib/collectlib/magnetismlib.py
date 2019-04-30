import numpy as np

from txmcommands import GenericTXMcommands

DATE = 0
NAME = 1
POS_X = 2
POS_Y = 3
POS_Z = 4
THETA_REGIONS = 5
ENERGY_REGIONS = 6
N_IMAGES = 7
FF_POS_X = 8
FF_POS_Y = 9
N_FF_IMAGES = 10

THETA_START = 0
THETA_END = 1
THETA_STEP = 2
EXPTIME = 3

ENERGY = 0
DET_Z = 1
ZP_Z = 2
ZP_STEP = 3
EXPTIME_FF = 4

FILE_NAME = 'magnetism.txt'

samples = [
    [
        '20180531'  # date
        'sample1',  # name
        -596.60,  # pos x
        606.40,  # pos y
        18.80,  # pos z
        [  # tilt regions
            [
                -10,  # start
                10,  # end
                10,  # theta step
                2,  # exposure time
            ],
        ],
        [  # jj positions
            [
                -3.3,    # jj_up
                2.2  # jj_down
            ]
        ],
        2,   # num images
        20,  # FlatField position X
        30,  # FlatField position x
        10,  # num FF images
    ],

]


class Magnetism(GenericTXMcommands):

    def __init__(self, samples=None, file_name=None):
        GenericTXMcommands.__init__(self, file_name=file_name)
        self.samples = samples

    def collect(self, jj_offset, sample_date=None, sample_name=None,
                theta=None):
        if sample_date is None:
            sample_date = self.current_sample_date
        if sample_name is None:
            sample_name = self.current_sample_name
        if theta is None:
            theta = self.current_theta
        base_name = ('%s_%s_%.1f_%.1f_%.1f' % (sample_date, sample_name,
                                               jj_offset, theta))
        extension = 'xrm'
        if (self._repetitions == 0 or self._repetitions == 1 or
                self._repetitions is None):
            file_name = '%s.%s' % (base_name, extension)
            self.destination.write('collect %s\n' % file_name)
        else:
            for repetition in range(1, self._repetitions+1):
                file_name = '%s_%d.%s' % (base_name, repetition, extension)
                self.destination.write('collect %s\n' % file_name)

    def collect_sample(self, sample):
        self.moveEnergy(self, energy)
        self.current_sample_date = sample[DATE]
        self.current_sample_name = sample[NAME]
        self.go_to_sample_xyz_pos(sample[POS_X],
                                  sample[POS_Y],
                                  sample[POS_Z])

        tilt_regions = sample[THETA_REGIONS]
        self._repetitions = sample[N_IMAGES]

        # move theta to the min angle, in order to avoid backlash
        self.moveTheta(-71.0)
        self.wait(10)

        for tilt_region in tilt_regions:
            tilt_start = tilt_region[THETA_START]
            tilt_end = tilt_region[THETA_END]
            tilt_step = tilt_region[THETA_STEP]
            exp_time = tilt_region[EXPTIME]
            msg = "Region start must be different than end"
            assert tilt_start != tilt_end, msg
            tilt_step = abs(tilt_step)
            if tilt_end - tilt_start < 1:
                tilt_step *= -1
            positions = np.arange(tilt_start, tilt_end, tilt_step)
            positions = np.append(positions, tilt_end)
            self.setExpTime(exp_time)

            # Acquisition of an image for each ZP, at each angle,
            # at each Energy.
            for theta in positions:
                self.moveTheta(theta)

                for e_zp_zone in sample[ENERGY_REGIONS]:

                    energy = e_zp_zone[ENERGY]
                    zp_central_pos = e_zp_zone[ZP_Z]
                    zp_step = e_zp_zone[ZP_STEP]
                    det_z = e_zp_zone[DET_Z]
                    self.go_to_energy_zp_det(energy, zp_central_pos, det_z)
                    self.collect()

        # Execute flat field acquisitions
        # move theta to 0 degrees - necessary for flat field measurement
        self.moveTheta(0)
        self.go_to_sample_xy_pos(sample[FF_POS_X],
                                 sample[FF_POS_Y])

        for e_zp_zone in sample[ENERGY_REGIONS]:
            energy = e_zp_zone[ENERGY]
            zp_central_pos = e_zp_zone[ZP_Z]
            det_z = e_zp_zone[DET_Z]
            self.setExpTime(e_zp_zone[EXPTIME_FF])
            self.go_to_energy_zp_det(energy, zp_central_pos, det_z)
            sample_name = '%s_%.1f' % (sample[NAME], energy)
            for i in range(sample[N_FF_IMAGES]):
                self.destination.write('collect %s_FF_%d.xrm\n' %
                                       (sample_name, i))

    def collect_data(self):
        self.setBinning()
        for sample in self.samples:
            self.collect_sample(sample)


if __name__ == '__main__':
    magnetism_obj = Magnetism(samples, FILE_NAME)
    magnetism_obj.generate()
