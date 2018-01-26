import time
import RTCjoystick

J = RTCjoystick.Joystick()
J.connect("/dev/input/js0")
J.info()
time.sleep(2)
J.start()

def hand():
    print("IT'S ALIVE!!!")

def hand2():
    print("REALY!!!")

def hand3():
    print("I NOT BELIVE")

J.connectButton('unknown(0x12d)', hand)
J.connectButton('thumb', hand2)
J.connectButton('trigger', hand3)

while(True):
    #print(J.Axis.get('x'))
    #print(J.Buttons.get('trigger'))
    time.sleep(0.1)
J.exit()
