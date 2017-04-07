import sys
import numpy as np

from txmcommands import GenericTXMcommands

NAME = 0
SAMPLE_REGIONS = 1
ENERGY_REGIONS = 2
ZP_START = 3
ZP_END = 4
DET_START = 5
DET_END = 6
FF_POS_X = 7
FF_POS_Y = 8
N_IMAGES = 9

POS_X = 0
POS_Y = 1
POS_Z = 2

E_START = 0
E_END = 1
E_STEP = 2
EXP_TIME = 3
EXP_TIME_FF = 4

FILE_NAME = 'energyscan.txt'

samples = [
    [ # sample with energies and zone plates
        "20170321_toto", # name
        [# Regions in sample to be imaged
            [ 
            -596.60, # pos x
            606.40, # pos y
            18.80, # pos z
            ],
        ],
        [ # energy regions
            [
                340.0,  
                343.0, 
                1, 
                10,
                8,
            ],
            [
                343.5, 
                353.5, 
                0.5, 
                10,
                8,
            ],
            [
                354.5, 
                360.5, 
                1, 
                10,
                8,
            ],
        ],
        -11627.3,
        -11504.0,
        -1913.7,
        -1792.5,
        -91.00, # flatfield position x
        -222.00 # flat field position y
    ]
]

class EnergyScan(GenericTXMcommands):

    def __init__(self, samples, file_name=None):
        self.samples = samples
        self.file_name = file_name
        self._repetitions = None

    def collect_escan(self, sample):

        # Sample start positions 
        sample_region = sample[SAMPLE_REGIONS][0]
        start_x = sample_region[POS_X]
        start_y = sample_region[POS_Y]
        start_z = sample_region[POS_Z]

        init_energy_region = sample[ENERGY_REGIONS][0]
        end_energy_region = sample[ENERGY_REGIONS][-1]
        first_energy = init_energy_region[E_START]
        last_energy = end_energy_region[E_END]

        # Total number of steps of 0.1 electronvolts in the total energy range
        resolution = 0.1
        small_steps = int(round((last_energy - first_energy) / resolution))

        # Counter of steps of 0.1 electronvolts in Energy
        counter_small_steps = 0

        # start zp and detector positions
        zp_start = sample[ZP_START]
        det_start = sample[DET_START]

        # end zp and detector positions
        zp_end = sample[ZP_END]
        det_end = sample[DET_END]

        # zp and detector small steps. 
        # It is the step if the energy was increased by the resolution factor.
        zp_step_resolution = (zp_end - zp_start) / small_steps
        det_step_resolution = (det_end - det_start) / small_steps

        # Images to be collected for each angle position
        self._repetitions = sample[N_IMAGES]

        # Collect images
        e_regions_number = len(sample[ENERGY_REGIONS])
        for e_region_num in range(e_regions_number):

            energy_region = sample[ENERGY_REGIONS][e_region_num]

            # energy values
            e_start = energy_region[E_START]
            e_end = energy_region[E_END]
            e_step = energy_region[E_STEP]
            energies = np.arange(e_start, e_end, e_step)
            energies = np.append(energies, e_end)

            # Fixed increment of step counts in each range
            # Number of steps of 0.1eV in a single Energy step
            increment_step_counts = int(round(e_step / resolution))
            for i in range(len(energies)):

                counter_small_steps += increment_step_counts
                if i == 0 and e_region_num == 0:      
                    counter_small_steps = 0

                # Collect sample image
                self.setExpTime(energy_region[EXP_TIME])
                self.moveEnergy(energies[i])

                zp_pos = zp_start + counter_small_steps*zp_step_resolution
                self.moveZonePlateZ(zp_pos)

                det_pos = det_start + counter_small_steps*det_step_resolution
                self.moveDetector(det_pos)

                num_sample_positions = len(sample[SAMPLE_REGIONS])
                for sample_pos_num in range (num_sample_positions):
                    sample_region = sample[SAMPLE_REGIONS][sample_pos_num]
                    self.moveX(sample_region[POS_X])
                    self.moveY(sample_region[POS_Y])
                    self.moveZ(sample_region[POS_Z])

                base_name = sample[NAME]
                if self._repetitions == 1:
                    command = 'collect %s_%6.2f.xrm\n'
                    self.destination.write(command % (base_name, 
                                                      energies[i]))
                else:
                    for repetition in range(0, self._repetitions):
                        command = 'collect %s_%6.2f_%s.xrm\n'
                        rep_str = str(repetition).zfill(3)
                        self.destination.write(command % (base_name, 
                                                          energies[i], 
                                                          rep_str))

                # Collect flatfield image
                self.setExpTime(energy_region[EXP_TIME_FF])
                self.moveX(sample[FF_POS_X])
                self.moveY(sample[FF_POS_Y])

                base_name = sample[NAME]
                self.destination.write('collect %s_%6.2f_FF.xrm\n'%(base_name, 
                                                                   energies[i]))

        ## Come back to initial positions
        self.moveX(start_x)
        self.moveY(start_y)
        self.moveZ(start_z)
        self.setExpTime(energy_region[EXP_TIME])
        self.moveEnergy(first_energy)
        self.moveZonePlateZ(zp_start)      
        self.moveDetector(det_start)

    def collect_data(self):
        self.setBinning()
        for sample in self.samples:
            self.collect_escan(sample)
            # wait 5 minutes between samples
            if len(self.samples) > 1:
                self.wait(300)

if __name__ == '__main__':
    energy_scan = EnergyScan(samples, FILE_NAME)
    energy_scan.generate()


