#!/home/maluethi/bin/miniconda3/envs/erth2nmea/bin/python

import cgi
import zmq

url = cgi.FieldStorage()

camera = url['CAMERA'].value
camera = camera.split(',')
lat = camera[0]
lon = camera[1]
alt = camera[2]

view = url['VIEW'].value
view = view.split(',')
tilt = view[0]
heading = view[1]

kml = ( 
   '<?xml version="1.0" encoding="UTF-8"?>\n'
   '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
   '<Placemark>\n'
   '<name>View-centered placemark</name>\n'
   '<Point>\n'
   '<coordinates>%.6f,%.6f</coordinates>\n'
   '</Point>\n'
   '</Placemark>\n'
   '</kml>'
   ) %(0, 0)

print("Content-Type: application/vnd.google-earth.kml+xml\n")
print(kml)

context = zmq.Context()
sender = context.socket(zmq.PUSH)

sender.bind('ipc:///tmp/earth.pipe')
sender.send_string(f'{lat},{lon},{alt},{heading}')
