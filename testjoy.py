#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import joystick

J = joystick.Joystick()
J.open("/dev/input/js0")
print(J)
time.sleep(2)
J.start()

J.onButtonClick('trigger', lambda x: print('trigger', x))
J.onButtonClick('thumb', lambda x: print('thumb', x))
J.onButtonClick("thumb2", lambda x: print("thumb2", x))
J.onButtonClick("top", lambda x: print("top", x))
J.onButtonClick("top2", lambda x: print("top2", x))


while True:
    print(J.axis['z'])
    time.sleep(0.05)





