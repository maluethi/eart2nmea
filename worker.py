import zmq
import math as m
import socket
import pynmea2 as nm


from datetime import datetime as dt


def to_gm(val):
    hh = m.floor(val)
    mm = (val - hh) * 60
    return hh, mm


def calc_lat(decimal):
    sign = m.copysign(1, decimal)
    direction = 'N' if sign == 1 else 'S'
    hh, mm = to_gm(abs(decimal))
    return f'{hh}{mm:.4f}', direction


def calc_lon(decimal):
    sign = m.copysign(1, decimal)
    direction = 'E' if sign == 1 else 'W'
    hh, mm = to_gm(abs(decimal))
    return f'{hh:0>3}{mm:.4f}', direction


def calc_alt(alt):
    return f'{alt:.2f}', 'M'


def calc_head(head):
    if head > 0:
        return f'{head:.2f}'
    elif head < 0:
        return f'{360 + head:.2f}'


def to_can(lat, lon, alt):
    pass

print("Opening connection to google earth")
context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect('ipc:///tmp/earth.pipe')

print("Opening connection to xcsoar")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', 10110)

while True:
    try:
        s = receiver.recv()
        s = s.decode('utf-8')
        df = s.split(',')
        lat = float(df[1])
        lon = float(df[0])
        alt = float(df[2])
        head = float(df[3])

        timestamp = dt.now().strftime("%H%M%S")
        date = dt.now().strftime("%d%m%y")

        data = (str(timestamp),'A', *calc_lat(lat), *calc_lon(lon), "40.0", calc_head(head), date, "1.2", "E","S")

        nmea_pos = nm.GGA('GP', 'RMC', data)
        nmea_alt = nm.GGA('PG', 'RMZ', (calc_alt(alt)))

        try:
            print(nmea_pos)
            print(nmea_alt)
            df_pos = (str(nmea_pos) + '\n').encode()
            df_alt = (str(nmea_alt) + '\n').encode()
        except Exception as e:
            print(Exception("Skipping this record"))
            continue

        try:
            sock.sendto(df_pos, addr)
            sock.sendto(df_alt, addr)
        except Exception as e:
            print(Exception("Unable to send record"))
            continue

    except KeyboardInterrupt:
        sock.close()
        exit()
