############################################################
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################

############################################################
#
# This code access the functionality of two modules:
#
# jpg2kml_jpg
#
# Extract the lat,lng and elv data from the jpg header
#
# jpg2kml_kml
#
# formats the lat, lng and elv data into a kml file
# with a point for each image.
#
############################################################

# Standard Libraries

import os

# jpg2kml modules

import jpg2kml_jpg
import jpg2kml_kml

# jpg Paths

strJpgPath = 'c:\\users\\david\\onedrive\\exif\\test_images\\'
# strJpgFile = 'gherkin.jpg'

# KML Paths

strKmlPath = 'c:\\users\\david\\onedrive\\exif\\'
strKmlFile = 'exif.kml'

# List to hold points

lstPoints = []

# Directory listing

lstJpgFiles = os.listdir(strJpgPath)

# Filter out directories etc.

for strJpgFile in lstJpgFiles:
    
    if strJpgFile.lower().endswith(('.jpg','jpeg')):
        
        dicPoint = jpg2kml_jpg.GetGps(strJpgPath,strJpgFile)

        if len(dicPoint) is not 0:
            lstPoints.append(dicPoint)
        else:
            print 'No GPS data for '+ strJpgFile

# Make the kml file

jpg2kml_kml.Placemarks(lstPoints,strKmlPath,strKmlFile)

print 'done...'


