#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import RTCJoystick

J = RTCJoystick.Joystick()
J.connect("/dev/input/js0")
print(J)
time.sleep(2)
J.start()


def hand(w):
    print(w, "IT'S ALIVE!!!")


def hand2(w):
    print(w, "REALY!!!")


def hand3(w):
    print(w, "I'm NOT BELIVE")


J.connectButton('top2', hand2)
J.connectButton('pinkie', hand3)


while True:
    #print(J.Axis.get('z'))
    time.sleep(0.05)





