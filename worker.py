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


def to_can(lat, lon, alt):
    pass


context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect('ipc:///tmp/earth.pipe')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 10110))
sock.listen(1)
conn, addr = sock.accept()

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

        data = (str(timestamp),'A', *calc_lat(lat), *calc_lon(lon), "10.0", f"{head:.2f}", date, "1.2", "E","S")

        nmea_pos = nm.GGA('GP', 'RMC', data)
        nmea_alt = nm.GGA('PG', 'RMZ', (calc_alt(alt)))

        df = (str(nmea_pos) + '\n').encode()

        print(df)
        print(nmea_pos)
        print(nmea_alt)
        conn.send(df)

        df = (str(nmea_alt) + '\n').encode()

        conn.send(df)

    except KeyboardInterrupt:
        conn.close()
        exit()
