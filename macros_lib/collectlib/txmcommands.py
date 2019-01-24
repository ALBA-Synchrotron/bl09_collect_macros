# -*- coding: utf-8 -*-

import sys


"""
This module is used as a library for BL09 macros used for creating TXM scripts.

"""


class GenericTXMcommands(object):
    """Generic TXM commands.

    The methods in this class will allow to create generic TXM commands,
    which will be included in the scripts generated by the macros using this
    library. The macros using this library creates scripts in .txt format,
    which are entered in TXM-XMController software in order to perform the
    data collection of ALBA BL09 TXM microscope.

    Coordinate system of the TXM (transmission X-ray Microscope) is:
    - Z in the direction of the beam
    - Y in the vertical direction
    - X perpendicular to Y and Z.
    """

    def __init__(self, file_name=None, current_sample_date=None,
                 current_sample_name=None, current_zone_plate=None,
                 current_theta=None, current_energy=None, repetitions=None):
        self.file_name = file_name
        self.current_sample_date = current_sample_date
        self.current_sample_name = current_sample_name
        self.current_zone_plate = current_zone_plate
        self.current_theta = current_theta
        self.current_energy = current_energy
        self._repetitions = repetitions

    def setBinning(self, binning=1):
        self.destination.write('setbinning %d\n' % binning)

    def moveX(self, x):
        self.destination.write('moveto X %6.2f\n' % x)

    def moveY(self, y):
        self.destination.write('moveto Y %6.2f\n' % y)

    def moveZ(self, z):
        self.destination.write('moveto Z %6.2f\n' % z)

    def move_select_workflow(self, prx):
        self.destination.write('moveto prx %6.2f\n' % prx)

    def move_target_angle(self, pry):
        self.destination.write('moveto pry %6.2f\n' % pry)

    def move_target_record_id(self, pry):
        self.destination.write('moveto pry %6.2f\n' % pry)

    def go_to_sample_xyz_pos(self, pos_x, pos_y, pos_z):
        self.moveX(pos_x)
        self.moveY(pos_y)
        self.moveZ(pos_z)

    def go_to_sample_xy_pos(self, pos_x, pos_y):
        self.moveX(pos_x)
        self.moveY(pos_y)

    def moveZonePlateZ(self, zone_plate):
        self.current_zone_plate = zone_plate
        self.destination.write('moveto ZPz %6.2f\n' % zone_plate)

    def moveTheta(self, theta):
        self.current_theta = theta
        self.destination.write('moveto T %6.2f\n' % theta)

    def moveDetector(self, detector):
        self.destination.write('moveto detz %6.2f\n' % detector)

    def moveEnergy(self, energy):
        self.current_energy = energy
        self.destination.write('moveto energy %6.2f\n' % energy)

    def go_to_energy(self, energy):
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
        self.moveEnergy(energy)

    def go_to_energy_zp_det(self, energy, zp_z, det_z):
        self.go_to_energy(energy)
        self.moveZonePlateZ(zp_z)
        self.moveDetector(det_z)

    def setExpTime(self, exp_time):
        self.destination.write('setexp %6.1f\n' % exp_time)

    def wait(self, wait_time):
        self.destination.write('wait %s\n' % wait_time)

    def collect_data(self):
        pass

    def generate(self):
        if self.file_name is None:
            destination = sys.stdout
        else:
            destination = open(self.file_name, 'w')
        with destination as self.destination:
            self.collect_data()
