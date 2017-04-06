import numpy as np

from txmcommands import GenericTXMcommands

NAME = 0
POS_X = 1
POS_Y = 2
POS_Z = 3
ZONE_PLATES = 4
REGIONS = 5
FF_POS_X = 6
FF_POS_Y = 7
EXP_TIME_FF = 8
N_IMAGES = 9

REGION_START = 0
REGION_END = 1
REGION_STEP = 2
REGION_EXPTIME = 3

ENERGY = 0
ENERGY_ZONE_PLATES = 1

FILE_NAME = 'manytomos.txt'

samples = [
    [
        'sample1', # name
        2, # pos x
        3, # pos y
        4, # pos z
        [ # pairs of energies and zone plate position
            [
                #800, # energy
                50, # central zone_plate
                2 # zone_plate step
            ],
        ],
        [# angular regions
            [
                -10, # start
                10, # end
                10, # theta step
                1 #  integration time
            ],
        ],
        2, # flatfield position x
        2, # flat field position y
        1, # flat field exposure time
        4, # num images
    ],

]


class ManyTomos(GenericTXMcommands):

    def __init__(self, samples=None, file_name=None):
        GenericTXMcommands.__init__(self, file_name=file_name)
        self.samples = samples

    def collect(self, sample_name=None, zone_plate=None,
                theta=None, energy=None):
        if sample_name is None:
            sample_name = self.current_sample_name
        if zone_plate is None:
            zone_plate = self.current_zone_plate
        if theta is None:
            theta = self.current_theta
        if energy is None:
            energy = self.current_energy
        base_name = ('%s_%.1f_%.1f' % (sample_name, theta, zone_plate))
        if not energy is None:
            base_name = '%s_%.1f' % (base_name, energy)
        extension = 'xrm'
        if self._repetitions == 1 or self._repetitions is None:
            file_name = '%s.%s' % (base_name, extension)
            self.destination.write('collect %s\n' % file_name)
        else:
            for repetition in range(1, self._repetitions+1):
                file_name = '%s_%d.%s' % (base_name, repetition, extension)
                self.destination.write('collect %s\n' % file_name)

    def collectZonePlates(self, zone_plates):
        for zone_plate in zone_plates:
            self.moveZonePlateZ(zone_plate)
            self.collect()

    def collectRegion(self, zone_plates, start, end, step, exp_time):
        assert start != end, "Region start must be different than end"
        if end - start < 1:
            step *= -1
        positions = np.arange(start, end, step)
        positions = np.append(positions, end)
        self.setExpTime(exp_time)

        # only zone plates
        if len(zone_plates[0]) == 2:
            for theta in positions:
                self.moveTheta(theta)
                zp_central_pos = zone_plates[0][0]
                zp_step = zone_plates[0][1]
                # Only one zp position used if zp_step is equal 0
                if zp_step == 0:
                    zp_single_pos_list = [zp_central_pos]
                    self.collectZonePlates(zp_single_pos_list)
                # Three zp positions used if zp_step is different than 0
                else:
                    zp_pos1 = zp_central_pos - zp_step
                    zp_pos2 = zp_central_pos
                    zp_pos3 = zp_central_pos + zp_step
                    inner_zone_plates = [zp_pos1, zp_pos2, zp_pos3]
                    self.collectZonePlates(inner_zone_plates)
        # energies and zone plates
        else:
            energy_zp_pairs = zone_plates
            for zp_central_pos, zp_step, energy in energy_zp_pairs:
                self.moveEnergy(energy)
                # wait until energy reaches its position
                # (collect does not wait for the external moveables)
                self.wait(60)
                # repeat the move many times to correct backlash
                self.moveEnergy(energy)
                self.wait(10)
                self.moveEnergy(energy)
                self.wait(5)
                self.moveEnergy(energy)
                self.wait(5)
                for theta in positions:
                    self.moveTheta(theta)
                    # Only one zp position used if zp_step is equal 0
                    if zp_step == 0:
                        zp_single_pos_list = [zp_central_pos]
                        self.collectZonePlates(zp_single_pos_list)
                    # Three zp positions used if zp_step is different than 0
                    else:
                        zp_pos1 = zp_central_pos - zp_step
                        zp_pos2 = zp_central_pos
                        zp_pos3 = zp_central_pos + zp_step
                        inner_zone_plates = [zp_pos1, zp_pos2, zp_pos3]
                        self.collectZonePlates(inner_zone_plates)

    def collectSample(self, sample):
        self.current_sample_name = sample[NAME]
        zone_plates = sample[ZONE_PLATES]
        pos_x = sample[POS_X]
        self.moveX(pos_x)
        pos_y = sample[POS_Y]
        self.moveY(pos_y)
        pos_z = sample[POS_Z]
        self.moveZ(pos_z)
        # move theta to the min angle, in order to avoid backlash
        self.moveTheta(-71.0)
        # wait 10 s so the theta movement has time to execute
        self.wait(10)
        regions = sample[REGIONS]
        try:
            self._repetitions = sample[N_IMAGES]
        except IndexError:
            self._repetitions = None
        for region in regions:
            self.collectRegion(zone_plates, *region)

    def collectFF(self, sample):
        """Execute flat field acquisitions
        """
        # move theta to 0 - it is necessary for flat field measurement
        self.moveTheta(0)
        # wait 10 s so the theta movement has time to execute
        self.wait(10)
        ff_pos_x = sample[FF_POS_X]
        self.moveX(ff_pos_x)
        ff_pos_y = sample[FF_POS_Y]
        self.moveY(ff_pos_y)
        exp_time_ff = sample[EXP_TIME_FF]
        self.setExpTime(exp_time_ff)
        sample_name = sample[NAME]
        for i in xrange(1,11):
            self.destination.write('collect %s_FF_%d.xrm\n' % (sample_name, i))

    def collectData(self):
        self.setBinning()
        for sample in self.samples:
            self.collectSample(sample)
            self.collectFF(sample)
            # wait 5 minutes between samples
            self.wait(300)


if __name__ == '__main__':
    tomos_obj = ManyTomos(samples, FILE_NAME)
    tomos_obj.generate()

