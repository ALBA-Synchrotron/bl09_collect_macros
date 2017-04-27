import numpy as np

from txmcommands import GenericTXMcommands

NAME = 0
POS_X = 1
POS_Y = 2
POS_Z = 3
ENERGIES_ZP = 4
ANGULAR_REGIONS = 5
FF_POS_X = 6
FF_POS_Y = 7
EXP_TIME_FF = 8
N_IMAGES = 9

REGION_START = 0
REGION_END = 1
REGION_STEP = 2
REGION_EXPTIME = 3

ENERGY = 0
DET_Z = 1
ZP_Z = 2
ZP_STEP = 3

FILE_NAME = 'manytomos.txt'

samples = [
    [
        'sample1', # name
        0, # pos x
        0, # pos y
        0, # pos z
        [#energies and zoneplates
            [
                100, # energy
                20000, # detector Z position
                50, # ZP Z central position
                2 # ZP step
            ]
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


class SpectroTomo(GenericTXMcommands):

    def __init__(self, samples=None, file_name=None):
        GenericTXMcommands.__init__(self, file_name=file_name)
        self.samples = samples


if __name__ == '__main__':
    spectrotomo_obj = SpectroTomo(samples, FILE_NAME)
    spectrotomo_obj.generate()