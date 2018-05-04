import time
import RTCJoystick

J = RTCJoystick.Joystick()
J.connect("/dev/input/js0")
J.info()
time.sleep(2)
J.start()


def hand():
    print("IT'S ALIVE!!!")


def hand2():
    print("REALY!!!")


def hand3():
    print("Im NOT BELIVE")


#J.connectButton('unknown(0x12d)', hand)
J.connectButton('base2', hand2)
J.connectButton('base3', hand3)

while False: #True:
    #print(J.Axis.get('ry'))
    #print(J.Buttons.get('trigger'))
    time.sleep(0.1)
J.exit()
