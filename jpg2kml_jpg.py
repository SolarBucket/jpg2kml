############################################################
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################

############################################################
#
# Crude programme to extract Date and Location from the
# Exif section of a .jpg.
#
# Notes
#
# This is not a genralized Exif reader
#
# It is assumed that the Exif and GPS data is contained in the
# Tiff header within the APP1 section
#
# The procedure terminates when it has the data is wants
# and does not read until the End of Image marker.
#
# There is no error handling
#
# Markers processed are:
#
#   ff d8 SOI  Start of image
#   ff da SOS  Start of scan
#   ff e1 APP1
#
# Main References:
#
# http://www.media.mit.edu/pia/Research/deepview/exif.html
# http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
# https://en.wikipedia.org/wiki/JPEG
#
############################################################

# Standard Libraries

import struct

def ReadIfd(stmSrc,intTifOff,intIfdOff,strBof):

    ########################################################
    #
    # Reads IFD Table
    #
    # Inputs:
    #
    # Src - file opened as 'rb'
    # TifOff - Offset of the Tiff header from start of file
    # IfdOff - Offset of IFD from start of Tiff header
    # Bof - Format char. '<' Little Endian, '>' Big Endian
    #
    # Return
    #
    # List of IFD entries
    #
    ########################################################

    # Empty list for Entries

    lstIfd = []

    # Move File Pointer

    stmSrc.seek(intTifOff+intIfdOff,0)

    # Number of entries in table

    intEnt = struct.unpack(strBof+'H',stmSrc.read(2))[0]

    # Build list of Entries

    for j in range(intEnt):
        strEnt = stmSrc.read(12)
        lstIfd.append(strEnt)

    # Return

    return lstIfd

def GetTagData(intReqTag,lstIfd,stmSrc,intTifOff,strBof):

    ########################################################
    #
    # Attemps to get the data associated with a given tak
    # in an IFD (a 12 byte structure).  If the tag exists
    # the function returns a tuple of the appropriate length (e.g.
    # DMS for lat/lng or a single string for model name.  If
    # the required tag is not found, then an empty tuple is
    # returned.
    #
    # If the length of data is less than or equal to four byte,
    # it is contained in the last four bytes of the IFD entry,
    # if it is longer, the last four bytes will be an offset
    # to the data relative to the start of the Tiff header.
    #
    # Inputs
    #
    # ReqTag - the tag id of the required data.  each IFD has
    # its own tag ids.  For example in the Exif section, 0x02
    # returns a different parameter than 0x02 in the GPS section.
    #
    # IFD - A list of 12 byte IFD entries.
    #
    # Src - an open file.
    #
    # TifOff - Offset from the start of the file of the
    # Tiff header.
    #
    # BoF - Byte order of the data, either Motorola or Intel
    #
    # Output
    #
    # A tuple containing the data associated with the tag
    # the contents of the tuple is tag specific, e.g.
    # Lat is returned as DMS.
    #
    # Notes
    #
    # Not all possible formats have been implimented, so
    # the function fail.
    #
    # ToDo
    #
    # Complete the list of formats
    #
    ########################################################

    # Empty tuple

    tupRet = ()

    # Look for the required tag

    for i in range(len(lstIfd)):

        # Convenience variable

        strEnt = lstIfd[i]

        # Tag

        intTag = struct.unpack(strBof+'H',strEnt[0:2])[0]

        # Find the required tag

        if intTag == intReqTag:

            # format of entry (e.g. string etc.)

            intFmt = struct.unpack(strBof+'H',strEnt[2:4])[0]

            # Number of components

            intCmp = struct.unpack(strBof+'L',strEnt[4:8])[0]

            # Compute Size of data block

            if intFmt == 0x01:

                # Unsigned byte has length of 1

                intSiz = intCmp

            elif intFmt == 0x02:

                # For a string, the number of components is
                # the number of chars including the null terminator

                intSiz = intCmp

            elif intFmt == 0x03:

                # An unsigned short is two bytes long

                intSiz = 2 * intCmp

            elif intFmt == 0x04:

                # An unsigned long is four bytes long

                intSiz = 4 * intCmp

            elif intFmt == 0x05:

                # An unsigned rational constist of an 8 byte block,
                # which contains two unsigned longs, the first is
                # the numerator and the second is the denominator

                intSiz = 8 * intCmp

            # Find the bytes that contain the data.
            # If the size of the data bloc is <=4 it will be in
            # the last 4 bytes of the directory entry, if it is
            # longer, the last four bytes will be an offset relative
            # to the tiff header of where it can be found.

            if intSiz <= 4:
                
                strDat = strEnt[8:12]

            else:

                # Get the offset

                intOff = struct.unpack(strBof+'L',strEnt[8:12])[0]

                # Move the file pointer (Relative to start of file)

                stmSrc.seek(intTifOff+intOff,0)

                # Read the data

                strDat = stmSrc.read(intSiz)

            # Build a tuple to return

            if intFmt == 0x01:

                for i in range(intCmp):
                    tupRet += (struct.unpack('B',strDat[i]),)
                    
            elif intFmt == 0x02:

                tupRet += (strDat[0:intSiz-1],)

            elif intFmt == 0x03:

                for i in range(intCmp):
                    tupRet += (struct.unpack(strBof+'H',strDat[i*2:i*2+2])[0],)

            elif intFmt == 0x04:

                for i in range(intCmp):
                    tupRet += (struct.unpack(strBof+'L',strDat[i*4:i*4+4])[0],)

            elif intFmt == 0x05:

                # A rational can be a way of storing floats as
                # longs.  The application that this code was written
                # for wants to work with floats, so the results are
                # returned that way.  This may not be appropriate
                # for other applications

                for i in range(intCmp):
                    
                    intNum = struct.unpack(strBof+'L',strDat[i*8:i*8+4])[0]
                    intDen = struct.unpack(strBof+'L',strDat[i*8+4:i*8+8])[0]

                    fltRet = float(intNum)/float(intDen)

                    tupRet += (fltRet,)

    # return
    
    return tupRet

def GetGps(strPath,strFile):

    ########################################################
    #
    # Attempts to find GPS data in Tiff header, if some is found
    # returns a dictionary containing lat, lng etc. if not, then
    # an empty dictionary is returned.
    #
    # This code can be adapted to obtain other information from
    # the Tiff header, but the project for which this was written
    # was only interested in location.
    #
    # Inputs
    #
    # Path - the folder/directory where the file is located
    #        including trailing //
    #
    # File - a jpeg file
    #
    # Output
    #
    # Dictionary contain lat, lng etc.
    #
    # Notes
    #
    # It's assumed that the file exists.
    #
    # Its assumed that if there is a GPS section, that it contains
    # at least a lat/lng pair.
    #
    # The contents of the GPS section varies with the device used
    # to capture the image.  For example, the GPS section can contain
    # the date and time, however, if this is important, it may be
    # prefereable to obtain it from the IFD section.
    #
    # ToDo
    #
    # Impliment with block
    #
    ########################################################

    # default to an empty dictionary

    dicPoint = {}

    # Source file (opened in read binary mode)

    stmSrc = open(strPath+strFile,'rb')

    # Get length of file and reset pointer

    stmSrc.seek(0,2)
    intLoF = stmSrc.tell()
    stmSrc.seek(0,0)
    
    # Loop through the file and avoid reading past the end

    while stmSrc.tell() < intLof:

        # Read Marker

        tupMkr = struct.unpack('BB',stmSrc.read(2))

        # Make some decisions

        if tupMkr[0] == 0xff and tupMkr[1] == 0xd8:

            # Start of image - nothing to do

            pass

        elif tupMkr[0] == 0xff and tupMkr[1] == 0xda:

            # Start of scan - lost interest

            break

        elif  tupMkr[0] == 0xff and tupMkr[1] == 0xe1:

            # App1 - Read the Size of the section (effectively skipping over it)

            intSiz = struct.unpack('>H',stmSrc.read(2))[0]

            # Exif header (6 bytes should be EXIF00)

            strExf = stmSrc.read(6)

            # Offset to tiff header (this is the reference for all offsets)

            intTifOff = stmSrc.tell()
   
            # Tiff Header

            strTif = stmSrc.read(8)

            # Byte order format

            if strTif[0:2] == 'II':
                strBof='<'
            else:
                strBof='>'

            # A number of deep philosophical significance
            # (this should be 0x2a (42 to base 10))

            intDPS = struct.unpack(strBof+'H',strTif[2:4])[0]

            # Offset to first IFD (from start of TIFF header)
  
            intOff = struct.unpack(strBof+'L',strTif[4:])[0]

            # IFD0

            lstIfd0 = ReadIfd(stmSrc,intTifOff,intOff,strBof)

            # Go get the offset to the Exif and GPS IFDs

            tupGpsOff = GetTagData(0x8825,lstIfd0,stmSrc,intTifOff,strBof)

            # if there is no GPS section, the tuple will be empty
            # and we can stop reading the file and quit

            if len(tupGpsOff) == 0:
                break
            else:
                intGpsOff = tupGpsOff[0]
                
            # Read the Exif and GPS IFDs

            lstGps = ReadIfd(stmSrc,intTifOff,intGpsOff,strBof)
        
            # lat/lng and elv from GPS

            tupLatRef = GetTagData(0x0001,lstGps,stmSrc,intTifOff,strBof)
            tupLat = GetTagData(0x0002,lstGps,stmSrc,intTifOff,strBof)

            tupLngRef = GetTagData(0x0003,lstGps,stmSrc,intTifOff,strBof)
            tupLng = GetTagData(0x0004,lstGps,stmSrc,intTifOff,strBof)

            tupElvRef = GetTagData(0x0005,lstGps,stmSrc,intTifOff,strBof)
            tupElv = GetTagData(0x0006,lstGps,stmSrc,intTifOff,strBof)

            # Date and time from GPS section

            tupDat = GetTagData(0x001d,lstGps,stmSrc,intTifOff,strBof)
            tupTim = GetTagData(0x0007,lstGps,stmSrc,intTifOff,strBof)

            # Convert lat to decimal degrees

            fltLat = float(tupLat[0])+ float(tupLat[1])/60.0+float(tupLat[2])/3600.0

            if tupLatRef[0] == 'S' or tupLatRef[0] == '-':
                fltLat *= -1.0

            # Convert lng to decimal degrees

            fltLng = float(tupLng[0])+ float(tupLng[1])/60.0+float(tupLng[2])/3600.0

            if tupLngRef[0]=='W' or tupLngRef[0]== '-':
                fltLng *= -1.0

            # Elevation is a float relative to sea level

            fltElv = float(tupElv[0])

            if tupElvRef[0] == 1:
                fltElv *= -1.0

            # Date as string

            if len(tupDat) is not 0:
                strDat = tupDat[0]
            else:
                strDat = 'Date na'

            # Time as string

            if len(tupTim) == 3:

                strTim = str.format('{0:>2}',tupTim[0])+':'+ \
                         str.format('{0:>2}',tupTim[1])+':'+ \
                         str.format('{0:>2}',tupTim[2])

            else:

                strTim = 'Time na'

            # Assemble dictionary

            dicPoint = {'lat':fltLat, \
                        'lng':fltLng, \
                        'elv':fltElv, \
                        'date':strDat, \
                        'time':strTim, \
                        'file':strFile}

            # We have all the data, so let's get out of here

            break
   
        else:

            # If the first two bytes where not ff d8 then
            # is is not a jpeg and there is nothing to do

            if stmSrc.tell() == 2:
                break

            # Read the Size of the section

            intSiz = struct.unpack('>H',stmSrc.read(2))[0]

            # Poistion pointer for next read

            stmSrc.seek(intSiz-2,1)

    # Hygeine

    stmSrc.close()

    # Return
 
    return dicPoint

                   

        


