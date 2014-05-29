#! /usr/bin/python

# File: autopilot-pid-test.py


from collections import deque
import socket
import struct
import sys
import copy
import time
#from flightinfo import DashBoard
from geodetic import Location, LatLon
from airports import runway_heading, runway_length, runway_location, closest_runway


AUTOPILOT_IP   = '0.0.0.0'
AUTOPILOT_PORT = 50000
XPLANE_PORT    = 49000


def platform_time():
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        return time.clock()
    else:
        return time.time()


class Instruments:

    def __init__(self):
        self.time       = platform_time()
        self.time_delta = 0
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
        self.trim_elev  = 0
        self.trim_ailrn = 0
        self.trim_ruddr = 0
        self.flap_handl = 0
        self.flap_postn = 0
        self.slat_ratio = 0
        self.sbrak_handl= 0
        self.sbrak_postn= 0


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
        self.trim_elev  = 0
        self.trim_ailrn = 0
        self.trim_ruddr = 0
        self.flap       = 0
        self.sbrak      = 0


instruments = Instruments()
controls = Controls()

DASH_TITLES = deque(['KIAS', 'ALT_AGL', 'PITCH', 'ROLL'])
DASH_YLIMS = deque([[0,400], [0, 3000], [-90, 90], [-90, 90]])
dash_elems = []
test = []
creation_time = ''


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

    instr.time = platform_time()
    instr.time_delta = instr.time - instruments.time

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

    elif id == 13: # trim/flap/speed brakes

        instr.trim_elev  = v0
        instr.trim_ailrn = v1
        instr.trim_ruddr = v2
        instr.flap_handl = v3
        instr.flap_postn = v4
        instr.slat_ratio = v5
        instr.sbrak_handl= v6
        instr.sbrak_postn= v7

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


controls_struct = struct.Struct('=5sI8fI8fI8fI8fI8f')

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
                 13, c.trim_elev, c.trim_ailrn, c.trim_ruddr, c.flap, -999, -999, c.sbrak, -999,
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

class PID:

    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0
        self.previous_err = 0

    def run(self, process, setpoint):
        dt = instruments.time_delta
        err = setpoint - process
        self.integral = self.integral + err*dt
        derivative = (err - self.previous_err)/dt
        self.previous_err = err
        return self.Kp*err + self.Ki*self.integral + self.Kd*derivative

def takeoffheading_PID(): # rudder 
    Pu = instruments.time_delta*100  #set constants here
    Ku = 0.026                       #set constants here
    Kp = 1.25*Ku 
    Kd = (Kp*Pu)/8
    return PID(Kp,0,Kd) 

def steer_PID(): # rudder 
    Pu = instruments.time_delta*3000  #set constants here
    Ku = 0.026                        #set constants here
    Kp = (0.6*Ku)
    Ki = (2*Kp)/Pu 
    Kd = (Kp*Pu)/8
    return PID(Kp,Ki,Kd) # Zeigler-Nichols method

    
def roll_PID(): # ailrn
    Pu = instruments.time_delta*300 #set constants here # close of a perfect tuning
    Ku = 0.02                       #set constants here # close of a perfect tuning
    Kp = (0.6*Ku)
    Ki = (2*Kp)/Pu
    Kd = (Kp*Pu)/8
    
    return PID(Kp,Ki,Kd)# Zeigler-Nichols method
    
def alt_PID(): # throttle
    Pu = instruments.time_delta  #set constants here
    Ku = 0.00015                 #set constants here
    Kp = (0.60*Ku)
    Ki = (2*Kp)/Pu
    Kd = (Kp*Pu)/8

    return PID(0.00004,0.000003, Kd*8) # Not optimal : V_i = 240 Alt_i = 5000 ft




def lim_m11(x):
    return max(-1, min(1, x))


def lim_01(x):
    return max(0, min(1, x))


def turn(roll, elev):
    err = roll - instruments.roll
    elev_coord = abs(instruments.roll) * 0.009
    ruddr_coord = instruments.roll * 0.002
    controls.ailrn = err * 0.02
    controls.elev = elev + elev_coord
    controls.ruddr = ruddr_coord


def throttle(x):
    controls.thro1 = x
    controls.thro2 = x
    controls.thro3 = x
    controls.thro4 = x


def hding_diff(hding1, hding2):
    return (hding1 - hding2 + 180) % 360 - 180


def pos():
    return LatLon(instruments.lat, instruments.lon)


def fly():

    maintain_norestart() # get current location

    rw = closest_runway(pos())

    if runway_location(rw).latlon.distance(pos()) > 300:
        print 'not on a known runway... exiting'
        return

    rw_hding = runway_heading(rw)

    print '*** starting at airport', rw[0], 'on runway', rw[1], 'with heading', rw_hding
    print 'apply full throttle and lower flaps partially'

    throttle(1) # full throttle
    controls.flap = 0.25 # partial flaps
    controls.sbrak = 0 # no speed brakes
    
    # Kp, Ki, Kd
    steer = takeoffheading_PID() # Takeoff
    maintain_norestart()

    while instruments.kias < 180:
        controls.ruddr = lim_m11(steer.run(instruments.hding_true, 180))
        # print ' Heading Error =', instruments.hding_true-rw_hding'     
        maintain_norestart()
        
    controls.flap = 0 # partial flaps 
    while instruments.alt_agl < 100:
        controls.ruddr = lim_m11(steer.run(instruments.hding_true, 180))
        # print ' Heading Error =', instruments.hding_true-rw_hding'     
        maintain_norestart()
    
    throttle(0.4)
    controls.gear=0
    while instruments.alt_msl < 2000:
        controls.ruddr = lim_m11(steer.run(instruments.hding_true, 180))
        # print ' Heading Error =', instruments.hding_true-rw_hding'     
        maintain_norestart()
   

    # Kp , Ki , Kd 
    steer = steer_PID()
    roll  = roll_PID()      
    altitude = alt_PID()

    # Setpoint
    Hding_Setpoint=180
    print ' SetPoint - Heading = ', Hding_Setpoint 
    print ' SetPoint - Altitude = 5000  (Default)'
    print ' SetPoint - Roll     = 0     (Default)'
    
    
    while True: 
        # Becareful : 2 PID 
        #print ' SetPoint - Heading = ', Hding_Setpoint
        controls.ruddr = lim_m11(steer.run(instruments.hding_true, Hding_Setpoint))

        throttle(lim_m11(altitude.run(instruments.alt_msl, 5000)))
        #print 'Setpoint at : 5000', '  (e) =', instruments.alt_msl-altitude

        controls.ailrn = lim_m11(roll.run(instruments.roll, 0))
        # print ' Roll Error =', instruments.roll'

        maintain_norestart()

    
if __name__ == '__main__':
    #Uncomment the next line if you want to run with the UI
    #build_ui()
    autopilot()
