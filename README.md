# jpg2kml
jpg2kml conmprises three modules:
jpg2kml_jpg.py.  This is the main module it extracts the GPS infomation from Tiff header (if there is any).
jpg2kml_kml.py.  This takes the GPS information retrieved by the GetGPS function in jpg2kml_jpg and creates placemarks in a kml file.
jpg2kml.py.  This reads a list of files and passes them to routines in jpg2kml_jpg and jpg2kml_kml.

The modules do not form a complete programme and are work in progress.  Some evolution will take place a testing progresses.
