import numpy as np

from txmcommands import GenericTXMcommands

DATE = 0
NAME = 1
POS_X = 2
POS_Y = 3
POS_Z = 4
ENERGIES_ZP = 5
FF_POS_X = 6
FF_POS_Y = 7
EXP_TIME_FF = 8
N_FF_IMAGES = 9
N_IMAGES = 10

ENERGY = 0
DET_Z = 1
ANGULAR_REGIONS = 2

REGION_START = 0
REGION_END = 1
REGION_STEP = 2
REGION_EXPTIME = 3
ZP_Z = 4
ZP_STEP = 5
NUM_ZPS = 6

FILE_NAME = 'manytomos.txt'

samples = [
    [
        '20171124'  # date
        'sample1',  # name
        0,  # pos x
        0,  # pos y
        0,  # pos z
        [  # energies and zoneplates
            [
                100,  # energy
                20000,  # detector Z position
                [  # angular regions
                    [
                        -10,  # start
                        10,  # end
                        10,  # theta step
                        1,  # integration time
                        50,  # ZP Z central position
                        0.2,  # ZP step
                        3,  # number of ZP positions
                    ],
                ],
            ],
        ],
        2,  # flat field position x
        2,  # flat field position y
        1,  # flat field exposure time
        4,  # num images
    ],

]


class ManyTomos_vdos(GenericTXMcommands):

    def __init__(self, samples=None, file_name=None):
        GenericTXMcommands.__init__(self, file_name=file_name)
        self.samples = samples

    def collect(self, sample_date="20171124"):
        sample_date = sample_date
        sample_name = self.current_sample_name
        zone_plate = self.current_zone_plate
        theta = self.current_theta
        energy = self.current_energy
        base_name = ('%s_%s_%.1f_%.1f_%.1f' % (sample_date, sample_name,
                                               energy, theta, zone_plate))
        extension = 'xrm'
        if self._repetitions == 1 or self._repetitions is None:
            file_name = '%s.%s' % (base_name, extension)
            self.destination.write('collect %s\n' % file_name)
        else:
            for repetition in range(self._repetitions):
                file_name = '%s_%d.%s' % (base_name, repetition, extension)
                self.destination.write('collect %s\n' % file_name)

    def collect_sample(self, sample):
        for e_zp_zone in sample[ENERGIES_ZP]:
            current_date = sample[DATE]
            self.current_sample_name = sample[NAME]

            energy = e_zp_zone[ENERGY]
            self.go_to_energy(energy)

            det_z = e_zp_zone[DET_Z]
            self.moveDetector(det_z)

            self.go_to_sample_xyz_pos(sample[POS_X],
                                      sample[POS_Y],
                                      sample[POS_Z])

            # move theta to the min angle, in order to avoid backlash
            self.moveTheta(-70.1)
            self.wait(10)

            angular_regions = e_zp_zone[ANGULAR_REGIONS]
            print(angular_regions)
            self._repetitions = sample[N_IMAGES]

            for angular_region in angular_regions:
                start = angular_region[REGION_START]
                end = angular_region[REGION_END]
                angle_step = angular_region[REGION_STEP]
                exp_time = angular_region[REGION_EXPTIME]
                if end - start < 1:
                    angle_step *= -1
                if start == end:
                    positions = np.array([start])
                else:
                    positions = np.arange(start, end, angle_step)
                    positions = np.append(positions, end)

                self.setExpTime(exp_time)

                zp_central_pos = angular_region[ZP_Z]
                zp_step = angular_region[ZP_STEP]

                # Acquisition of an image for each ZP, at each angle,
                # at each Energy.
                if zp_step == 0:
                    self.moveZonePlateZ(zp_central_pos)
                    num_zps = 1
                else:
                    num_zps = angular_region[NUM_ZPS]

                for theta in positions:
                    self.moveTheta(theta)
                    # Single-focus
                    if zp_step == 0:
                        self.collect(sample_date=current_date)
                    # Multi-focus: Three ZP positions used.
                    else:
                        start = zp_central_pos - zp_step*(num_zps - 1)/2.0
                        stop = zp_central_pos + zp_step*(num_zps - 1)/2.0
                        zone_plates = np.linspace(start, stop, num_zps)
                        for zone_plate in zone_plates:
                            self.moveZonePlateZ(zone_plate)
                            self.collect(sample_date=current_date)

            # Execute flat field acquisitions #
            # move theta to 0 degrees - necessary for flat field measurement
            self.moveTheta(0)
            self.go_to_sample_xy_pos(sample[FF_POS_X],
                                     sample[FF_POS_Y])
            self.setExpTime(sample[EXP_TIME_FF])
            sample_name = '%s_%s_%.1f' % (current_date,
                                          self.current_sample_name,
                                          energy)
            for i in range(sample[N_FF_IMAGES]):
                self.destination.write('collect %s_FF_%d.xrm\n' %
                                       (sample_name, i))

    def collect_data(self):
        self.setBinning()
        for sample in self.samples:
            self.collect_sample(sample)
            # wait 5 minutes between samples
            self.wait(300)


if __name__ == '__main__':
    tomos_obj = ManyTomos_vdos(samples, FILE_NAME)
    tomos_obj.generate()

