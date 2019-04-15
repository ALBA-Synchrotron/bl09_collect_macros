##############################################################################
##
# synchronize macro is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# synchronize macro is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with synchronize.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

import os
from PyTango import DeviceProxy, DevState
from sardana.macroserver.macro import Macro, Type


class synchronize(Macro):
    """Set position to synchronize motor and tango attributes in case of
    inconsistencies in target (or select) motors linked to the action
    of TXMAutoPreprocessing TangoDS.

    Value 6 corresponds to the synchronize Action from TXM DS
    TXMAutoPreprocessing
    
    Reset the symbolic link used for data collection, at the 
    default folder. This macro is thought to be used when the 
    symlink is broken, or if it has to be reset to the default"""

    def run(self):

        select_motor = DeviceProxy("bl09/ct/txm-select")
        target_motor = DeviceProxy("bl09/ct/txm-target")

        state_select = select_motor.state()
        state_target = target_motor.state()
        if state_select == DevState.ALARM or state_target == DevState.ALARM:
            select_motor.Position = 6
            target_motor.Position = 6

        all_files_link = "/beamlines/bl09/controls/BL09_RAWDATA"
        os.system("rm %s" % all_files_link)
        
        root_folder = "/beamlines/bl09/controls/DEFAULT_USER_FOLDER"
        root_folder_relative_path = root_folder.replace(
             "/beamlines/bl09", "..")
        os.system("ln -s %s %s" % (root_folder_relative_path, all_files_link))            


class link(Macro):
    """Reset the symbolic link used for data collection, at the 
    default folder. This macro is thought to be used when the 
    symlink is broken, or if it has to be reset to the default"""

    def run(self):
        all_files_link = "/beamlines/bl09/controls/BL09_RAWDATA"
        os.system("rm %s" % all_files_link)
        
        root_folder = "/beamlines/bl09/controls/DEFAULT_USER_FOLDER"
        root_folder_relative_path = root_folder.replace(
             "/beamlines/bl09", "..")
        os.system("ln -s %s %s" % (root_folder_relative_path, all_files_link))

