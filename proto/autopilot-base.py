#! /usr/bin/python

# File: autopilot-base.py

# Author: Marc Feeley


from collections import deque
import socket
import struct
import sys
import copy
import time
from flightinfo import DashBoard


AUTOPILOT_IP   = '0.0.0.0'
AUTOPILOT_PORT = 50000
XPLANE_PORT    = 49000


class Instruments:

    def __init__(self):
        self.kias       = 0
        self.keas       = 0
        self.ktas       = 0
        self.ktgs       = 0
        self.mph        = 0
        self.mphas      = 0
        self.mphgs      = 0
        self.pitch      = 0
        self.roll       = 0
        self.hding_true = 0
        self.hding_mag  = 0
        self.lat        = 0
        self.lon        = 0
        self.alt_msl    = 0
        self.alt_agl    = 0
        self.on_rwy     = 0
        self.alt_ind    = 0


class Controls:

    def __init__(self):
        self.gear       = 1
        self.wbrak      = 0
        self.lbrak      = 0
        self.rbrak      = 0
        self.elev       = 0
        self.ailrn      = 0
        self.ruddr      = 0
        self.nose       = 0
        self.thro1      = 0
        self.thro2      = 0
        self.thro3      = 0
        self.thro4      = 0


instruments = Instruments()
controls = Controls()

DASH_TITLES = deque(['KIAS', 'ALT_AGL', 'PITCH', 'ROLL'])
DASH_YLIMS = deque([[0,400], [0, 3000], [-90, 90], [-90, 90]])
dash_elems = []
test = []
creation_time = ''


def platform_time():
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        return time.clock()
    else:
        return time.time()

def build_ui():
    global dash_elems, creation_time
    start = platform_time()
    strs = DASH_TITLES
    lims= DASH_YLIMS
    dash = DashBoard(strs.popleft(), ylims=lims.popleft())
    dash_elems.append(dash)
    for x in range(len(strs)):
        dash_elems.append(dash.add(strs.popleft(), ylims=lims.popleft()))
    creation_time += ('\nOperating system: {0}.\n'.format(sys.platform))
    creation_time += ('UI creation time: {0} seconds.\n'
                      .format(platform_time()-start))

def update_ui(data):
    global dash_elems, test, creation_time
    start = platform_time()
    if len(dash_elems) > 0:
        try:
            dash_elems[0].update_all(data)
        except:
            print 'GUI error.'
            dash_elems = []
        end = platform_time()-start
        #Performance test.
        if len(test) == 0:
            print 'Running UI performance test, do not resize or move the UI.'
        if end > 0.001 and len(test) < 30:
            test.append(end)
        elif len(test) == 30:
            tar = open('benchmark.txt', 'a')
            sep = ['-']*40
            tar.write(''.join(sep))
            tar.write(creation_time)
            tar.write('Average update time: {0}.\n'
                      .format(sum(test)/float(len(test))))
            tar.write(''.join(sep))
            tar.write('\n')
            tar.close()
            print 'Performance test completed. Results in \'benchmark.txt\''
            test.append(0)

msg_label_struct = struct.Struct('=5s')
data_packet_struct = struct.Struct('I8f')


receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

receive_sock.bind((AUTOPILOT_IP, AUTOPILOT_PORT))

xplane_ip = ''


def receive():

    global instruments, xplane_ip
    
    msg, addr = receive_sock.recvfrom(4096)
    (xplane_ip, port) = addr

    instr = copy.copy(instruments)

    n = len(msg)

    (label,) = msg_label_struct.unpack_from(msg, 0)

    if label == 'DATA@':
        i = msg_label_struct.size;
        while i < n:
            data = data_packet_struct.unpack_from(msg, i)
            process_xplane_data(data, instr)
            i += data_packet_struct.size

    instruments = instr
    dash_inst = deque([instr.mph, instr.alt_agl, instr.pitch, instr.roll])
    update_ui(dash_inst)
    

def process_xplane_data(data, instr):

    (id, v0, v1, v2, v3, v4, v5, v6, v7) = data

    if id == 3: # speeds

        instr.kias       = v0
        instr.keas       = v1
        instr.ktas       = v2
        instr.ktgs       = v3
        instr.mph        = v5
        instr.mphas      = v6
        instr.mphgs      = v7

    elif id == 17: # pitch/roll/heading

        instr.pitch      = v0
        instr.roll       = v1
        instr.hding_true = v2
        instr.hding_mag  = v3

    elif id == 20: # lat/long/alt

        instr.lat        = v0
        instr.lon        = v1
        instr.alt_msl    = v2
        instr.alt_agl    = v3
        instr.on_rwy     = v4
        instr.alt_ind    = v5


def pilot():

    c = controls

    c.gear  = 1
    c.thro1 = 0


controls_struct = struct.Struct('=5sI8fI8fI8fI8f')

send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class SimulationStart(Exception):

    def __init__(self):
        pass


def send():

    c = controls

    packet = controls_struct.pack(
                 'DATA@',
                 14, c.gear, c.wbrak, c.lbrak, c.rbrak, 0, 0, 0, 0,
                  8, c.elev, c.ailrn, c.ruddr, -999, c.nose, -999, -999, -999,
                 11, -999, -999, -999, -999, c.nose, -999, -999, -999,
                 25, c.thro1, c.thro2, c.thro3, c.thro4, 0, 0, 0, 0);

    send_sock.sendto(packet, (xplane_ip, XPLANE_PORT))


def maintain_norestart():
    receive()  # get data from X-plane
    send()     # send commands to X-plane


def maintain():
    maintain_norestart()
    if instruments.mph < 1 and instruments.alt_agl < 50:
        raise SimulationStart()  # detect when plane crashes and is reset


def autopilot():

    global controls
    
    while True:

        print '*** start of simulation ***'

        controls = Controls()

        if len(dash_elems) > 0:
            dash_elems[0].re_init()

        try:
            fly()
        except SimulationStart, socket.error:
            pass


def fly():

    print 'applying full throttle'

    controls.thro1 = 1 # full throttle
    controls.thro2 = 1
    controls.thro3 = 1
    controls.thro4 = 1

    controls.ruddr = -0.0045 # left rudder
    controls.ailrn = -0.015 # slight left roll

    while instruments.kias < 160: # wait to reach rotate speed
        maintain_norestart()

    print 'starting takeoff rotation'

    controls.elev = 0.5 # up elevator

    while instruments.kias < 180:
        maintain()

    print 'end of takeoff rotation'

    controls.elev = 0.3 # ease off on elevator

    while instruments.alt_agl < 100:
        maintain()

    print 'raising landing gear'

    controls.gear = 0 # raise landing gear

    controls.elev = 0 # neutral elevator

    while instruments.alt_agl < 1000:
        maintain()

    print 'reduce throttle and wait until 2000 feet'

    controls.thro1 = 0.4 # ease off on throttle
    controls.thro2 = 0.4
    controls.thro3 = 0.4
    controls.thro4 = 0.4

    while instruments.alt_agl < 2000:
        maintain()

    print 'leveling off'

    controls.elev = -0.2 # push on elevator to level off

    while instruments.pitch > 0:
        maintain()

    print 'keep flying'

    controls.elev = 0 # neutral elevator

    while True:
        maintain()

    
if __name__ == '__main__':
    #Uncomment the next line if you want to run with the UI
    #build_ui()
    autopilot()
