#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import RTCJoystick

J = RTCJoystick.Joystick()
J.connect("/dev/input/js0")
J.info()
print(J)
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

#
try:
    while True:
        print(J.Axis.get('x'))
        #print(J.Buttons.get('base2'))
        time.sleep(0.1)
except(KeyboardInterrupt, SystemExit):
    J.exit()
    print(10101)
#print(J.Axis.get('x'))
#time.sleep(10)


