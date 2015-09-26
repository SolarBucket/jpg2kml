############################################################
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################

############################################################
#
# jpg2kml_kml
#
#
############################################################

# Standard Libraries

from xml.dom.minidom import Document

def Placemarks(lstPoints,strKmlPath,strKmlFile):

    ########################################################
    #
    # Notes
    #
    # The gx namespace is not used in this module
    #
    # ToDo
    #
    # Put CData section in description
    #
    ########################################################

    # KML - Root and Headers

    xmlDoc = Document()

    # KML Root Node

    kml = xmlDoc.createElement('kml')

    kml.setAttribute('xmlns','http://www.opengis.net/kml/2.2')
    kml.setAttribute('xmlns:gx','http://www.google.com/kml/ext/2.2')

    # Document Node

    document = xmlDoc.createElement('Document')

    # Placemarks

    for dic in lstPoints:

    # Extract Data

        fltLat=dic['lat']
        fltLng=dic['lng']
        fltElv=dic['elv']
        strDat=dic['date']
        strTim=dic['time']
        strFil=dic['file']

        # String for description

        strDesc = strDat + '<br />' + \
                  strTim

        # Placemark

        placemark = xmlDoc.createElement('Placemark')

        # Name of placemark

        name = xmlDoc.createElement('name')
        name.appendChild(xmlDoc.createTextNode(strFil))

        placemark.appendChild(name)

        # Description

        description = xmlDoc.createElement('description')
        description.appendChild(xmlDoc.createTextNode(strDesc))

        placemark.appendChild(description)

        # Point

        point = xmlDoc.createElement('Point')

        # Coordinates

        strLng = str.format('{0:.6f}',fltLng)
        strLat = str.format('{0:.6f}',fltLat)

        coords = xmlDoc.createElement('coordinates')
        coords.appendChild(xmlDoc.createTextNode(strLng+','+strLat))

        point.appendChild(coords)

        # Add point to placemark

        placemark.appendChild(point)

        # Add placemark to the document

        document.appendChild(placemark)

    # Append document node to kml node

    kml.appendChild(document)

    # Add the root node to the document

    xmlDoc.appendChild(kml)

    # Save to file

    stmDst = file(strKmlPath+strKmlFile,'w')
    stmDst.write(xmlDoc.toprettyxml(encoding='UTF-8'))
    stmDst.close()

