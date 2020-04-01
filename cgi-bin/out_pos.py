#!/home/maluethi/bin/miniconda3/envs/erth2nmea/bin/python

import cgi
import math as m

import socket
import pynmea2 as nm
from datetime import datetime as dt
import logging

def to_gm(val):
   val = abs(val)
   hh = m.floor(val)
   mm = (val - hh) * 60
   val = 100 * hh + mm
   return f'{val:>08.4f}'


def calc_lat(decimal):
   sign = m.copysign(1, decimal)
   direction = 'N' if sign == 1 else 'S'
   return to_gm(decimal), direction


def calc_lon(decimal):
   sign = m.copysign(1, decimal)
   direction = 'E' if sign == 1 else 'W'
   return to_gm(decimal), direction


def calc_alt(alt):
   return f'{alt:.2f}', 'M'


def calc_head(head):
   if head > 0:
      return f'{head:.2f}'
   elif head < 0:
      return f'{360 + head:.2f}'


url = cgi.FieldStorage()

logging.basicConfig(filename='cgi.log', level=logging.DEBUG)

camera = url['CAMERA'].value
camera = camera.split(',')
lat = float(camera[1])
lon = float(camera[0])
alt = float(camera[2])

view = url['VIEW'].value
view = view.split(',')
tilt = float(view[0])
head = float(view[1])

# TODO: Remove unnecessary point that is sent back to google earth
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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', 10110)

timestamp = dt.now().strftime("%H%M%S")
date = dt.now().strftime("%d%m%y")

data = (str(timestamp), 'A', *calc_lat(lat), *calc_lon(lon), "40.0", calc_head(head), date, "1.2", "E", "S")

nmea_pos = nm.GGA('GP', 'RMC', data)
nmea_alt = nm.GGA('PG', 'RMZ', (calc_alt(alt)))

logging.debug(f"pos: {nmea_pos}")
logging.debug(f"alt: {nmea_alt}")

try:
   df_pos = (str(nmea_pos) + '\n').encode()
   df_alt = (str(nmea_alt) + '\n').encode()
except Exception as e:
   logging.debug(f"unable to encode alt/pos")
   raise Exception("encoding issue")
try:
   sock.sendto(df_pos, addr)
   sock.sendto(df_alt, addr)
except Exception as e:
   logging.debug(f"unable to send alt/pos")
   raise Exception("sending issue")


print("Content-Type: application/vnd.google-earth.kml+xml\n")
print(kml)