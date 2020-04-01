#!/home/maluethi/bin/miniconda3/envs/erth2nmea/bin/python

import cgi
import math as m

import socket
from datetime import datetime as dt
import logging

from functools import reduce
import operator


def to_gm(val):
    val = abs(val)
    hh = m.floor(val)
    mm = (val - hh) * 60
    val = 100 * hh + mm
    return f'{val:>08.4f}'


def calc_lat(decimal):
    sign = m.copysign(1, decimal)
    direction = 'N' if sign == 1 else 'S'
    return f"{to_gm(decimal)},{direction}"


def calc_lon(decimal):
    sign = m.copysign(1, decimal)
    direction = 'E' if sign == 1 else 'W'
    return f"{to_gm(decimal)},{direction}"


def calc_alt(alt):
    return f'{alt:.2f},M'


def calc_head(head):
    if head > 0:
        return f'{head:.2f}'
    elif head < 0:
        return f'{360 + head:.2f}'


def checksum(nmea_string):
    return reduce(operator.xor, map(ord, nmea_string), 0)


url = cgi.FieldStorage()

# put the level to DEBUG for output
logging.basicConfig(filename='cgi.log', level=logging.CRITICAL)

camera = url['CAMERA'].value
camera = camera.split(',')
lat = float(camera[1])
lon = float(camera[0])
alt = float(camera[2])

view = url['VIEW'].value
view = view.split(',')
tilt = float(view[0])
head = float(view[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', 10110)

timestamp = dt.now().strftime("%H%M%S")
date = dt.now().strftime("%d%m%y")

nmea_pos = f"GPRMC,{timestamp},A,{calc_lat(lat)},{calc_lon(lon)},40.0,{calc_head(head)},{date},1.2,E,S"
nmea_pos_string = f"${nmea_pos}*{checksum(nmea_pos):>02x}\n"

nmea_altt = f"PGRMZ,{calc_alt(alt)}"
nmea_alt_string = f"${nmea_altt}*{checksum(nmea_altt):>02x}\n"

logging.debug(f"pos  : {nmea_pos}")
logging.debug(f'       {nmea_alt_string}')

try:
    df_pos = nmea_pos_string.encode()
    df_alt = nmea_alt_string.encode()
except Exception as e:
    logging.debug(f"unable to encode alt/pos")
    raise Exception("encoding issue")
try:
    sock.sendto(df_pos, addr)
    sock.sendto(df_alt, addr)
except Exception as e:
    logging.debug(f"unable to send alt/pos")
    raise Exception("sending issue")

kml = (
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
          '</kml>'
    )

print("Content-Type: application/vnd.google-earth.kml+xml\n")
print(kml)
