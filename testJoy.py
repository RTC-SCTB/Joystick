#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import RTCJoystick


J = RTCJoystick.Joystick()
J.connect("/dev/input/js0")
print(J)
time.sleep(2)
J.start()


def hand():
    print("IT'S ALIVE!!!")


def hand2():
    print("REALY!!!")


def hand3():
    print("I'm NOT BELIVE")


J.connectButton('base2', hand2)
J.connectButton('base3', hand3)


while True:
    print(J.Axis.get('z'))
    time.sleep(0.05)





