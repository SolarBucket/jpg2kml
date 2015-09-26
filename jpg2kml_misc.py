############################################################
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################

############################################################
#
# Misc. function(s) created in the development of jpg2kml
#
############################################################

# Standard Libraries

import struct

def IfdList(lstIfd):

    ########################################################
    #
    # Prints a list of the entries in an IFD which are:
    #
    # Tag ID (e.g 0x0001 Lat Ref from GPS IFD
    # format (e.g. string, integer, rational etc.
    # Number of components (e.g. lat/lngs typically have 3 rationals)
    # Data or Offset to data
    #
    ########################################################

    for i in range(len(lstIfd)):

        strEnt = lstIfd[i]

        # Tag

        intTag = struct.unpack(strBof+'H',strEnt[0:2])[0]

        # Type/Format

        intFmt = struct.unpack(strBof+'H',strEnt[2:4])[0]

        # Number of components

        intCmp = struct.unpack(strBof+'L',strEnt[4:8])[0]

        # Data/Offset

        intOff = struct.unpack(strBof+'L',strEnt[8:12])[0]

        # Dump

        print str.format('{0:#0x}',intTag), \
              str.format('{0:#0x}',intFmt), \
              str.format('{0:#0x}',intCmp), \
              str.format('{0:#0x}',intOff)
