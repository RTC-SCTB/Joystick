#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import joystick

J = joystick.Joystick()
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


#J.connectButton('top2', hand2)
#J.connectButton('pinkie', hand3)

J.connectButton('trigger', lambda x: print(1))
J.connectButton('thumb', lambda x: print(2))
J.connectButton("thumb2", lambda x: print(3))
J.connectButton("top", lambda x: print(5))
J.connectButton("top2", lambda x: print(6))


while True:
    #print(J.Axis['z'])
    time.sleep(0.05)





