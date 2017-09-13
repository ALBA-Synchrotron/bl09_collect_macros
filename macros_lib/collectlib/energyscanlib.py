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
        "20170913_toto", # name
        [# Regions in sample to be imaged
            [ 
            0, # pos x
            0, # pos y
            0, # pos z
            ],
        ],
        [ # energy regions
            [
                515.0,  
                525.0, 
                0.2, 
                1,
                1,
            ],
            [
                525.4, 
                534.3, 
                0.1, 
                1,
                1,
            ],
            [
                534.5, 
                544.7, 
                0.2, 
                1,
                1,
            ],
            [
                545.0, 
                580.0, 
                1.0, 
                1,
                1,
            ],
        ],
        -10143.1,
        -9827.8,
        -1103.0,
        -787.8,
        1.0, # flatfield position x
        1.0, # flat field position y
        1 # flat field position y
    ]
]

class EnergyScan(GenericTXMcommands):

    def __init__(self, samples, file_name=None):
        self.samples = samples
        self.file_name = file_name
        self._repetitions = None
        self.resolution = 0.1

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
        num_small_steps = round((last_energy - first_energy) / self.resolution)

        # Counter of steps of 0.1 electronvolts in Energy
        counter_small_steps = 0

        # zp start and end positions
        zp_start_global = zp_start = sample[ZP_START]
        zp_end = sample[ZP_END]

        # detector start and end positions
        det_start_global = det_start = sample[DET_START]
        det_end = sample[DET_END]

        # zp and detector small steps: 
        # the step if the energy was increased by the resolution factor.
        zp_step_resolution = (zp_end - zp_start) / num_small_steps
        det_step_resolution = (det_end - det_start) / num_small_steps
        
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
        
        
            n_small_step_in_Eregion = (e_end - e_start) / self.resolution
            # Number of steps of 0.1eV in a single Energy step
            num_small_steps_in_energy_step = round(e_step / self.resolution)
                                
            zp_step = zp_step_resolution * num_small_steps_in_energy_step
            det_step = det_step_resolution * num_small_steps_in_energy_step
      
            energies = np.linspace(e_start, e_end,
                                   round((e_end - e_start) / e_step) +1)

            if e_region_num != 0:
                zp_start = zp_end_previous_Eregion + zp_step_resolution * (
                    e_start - e_end_prevous_Eregion) / self.resolution
                det_start = det_end_previous_Eregion + det_step_resolution * (
                    e_start - e_end_prevous_Eregion) / self.resolution

            zp_pos = zp_start
            det_pos = det_start
            
            for count in range(len(energies)):

                # Collect sample image
                self.setExpTime(energy_region[EXP_TIME])
                self.moveEnergy(energies[count])
                self.moveZonePlateZ(zp_pos)
                self.moveDetector(det_pos)

                num_sample_positions = len(sample[SAMPLE_REGIONS])
                for sample_pos_num in range (num_sample_positions):
                    sample_region = sample[SAMPLE_REGIONS][sample_pos_num]
                    self.moveX(sample_region[POS_X])
                    self.moveY(sample_region[POS_Y])
                    self.moveZ(sample_region[POS_Z])

                base_name = sample[NAME]
                if self._repetitions == 1:
                    command = 'collect %s_0_%6.2f_0.xrm\n'
                    self.destination.write(command % (base_name, 
                                                      energies[count]))
                else:
                    for repetition in range(self._repetitions):
                        command = 'collect %s_0_%6.2f_0_%s.xrm\n'
                        rep_str = str(repetition).zfill(3)
                        self.destination.write(command % (base_name, 
                                                          energies[count], 
                                                          rep_str))

                # Collect flatfield image
                self.setExpTime(energy_region[EXP_TIME_FF])
                self.moveX(sample[FF_POS_X])
                self.moveY(sample[FF_POS_Y])

                base_name = sample[NAME]
                self.destination.write('collect %s_0_FF_%6.2f.xrm\n' % 
                                       (base_name, energies[count]))

                zp_pos += zp_step
                det_pos += det_step
                
            zp_end_previous_Eregion = zp_start + (n_small_step_in_Eregion * 
                                                  zp_step_resolution)
            det_end_previous_Eregion = det_start + (n_small_step_in_Eregion * 
                                                    det_step_resolution)
            e_end_prevous_Eregion = e_end
            

        ## Come back to initial positions
        self.moveX(start_x)
        self.moveY(start_y)
        self.moveZ(start_z)
        self.setExpTime(energy_region[EXP_TIME])
        self.moveEnergy(first_energy)
        self.moveZonePlateZ(zp_start_global)      
        self.moveDetector(det_start_global)

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


