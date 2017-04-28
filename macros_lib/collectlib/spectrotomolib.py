import numpy as np

from txmcommands import GenericTXMcommands

NAME = 0
SAMPLE_REGIONS = 1
THETA_REGIONS = 2
ENERGY_REGIONS = 3
N_IMAGES = 4
FF_POS_X = 5
FF_POS_Y = 6

POS_X = 0
POS_Y = 1
POS_Z = 2

THETA_START = 0
THETA_END = 1
THETA_STEP = 2
EXPTIME = 3

ENERGY = 0
DET_Z = 1
ZP_Z = 2
ZP_STEP = 3
EXPTIME_FF = 4

FILE_NAME = 'spectrotomo.txt'

samples = [
    [
        'sample1',  # name

        [  # Regions in sample to be imaged
            [
                -596.60,  # pos x
                606.40,  # pos y
                18.80,  # pos z
            ],
        ],
        [  # angular regions
            [
                -10,  # start
                10,  # end
                10,  # theta step
                2,  # exposure time
            ],
        ],
        [  # energies and zoneplates
            [
                100,    # energy
                20000,  # detector Z position
                50,     # ZP Z central position
                3,       # ZP step
                2  # FF exposure time
            ]
        ],
        2,   # num images
        20,  # FlatField position X
        30,  # FlatField position x

    ],

]


class SpectroTomo(GenericTXMcommands):

    def __init__(self, samples=None, file_name=None):
        GenericTXMcommands.__init__(self, file_name=file_name)
        self.samples = samples


if __name__ == '__main__':
    spectrotomo_obj = SpectroTomo(samples, FILE_NAME)
    spectrotomo_obj.generate()