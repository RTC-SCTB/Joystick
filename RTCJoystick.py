#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
import array
from fcntl import ioctl
import threading
import RTCEventMaster


class JoyCrashError(Exception):  # Исключение поломки джойстика
    pass


class JoyNotFoundError(Exception):  # Исключение отсутствия джойстика
    pass


class InternalError(Exception):  # Внутренняя ошибка
    pass


class ButtonError(Exception):  # Ошибка кнопки
    pass


# Взято из какого-то системного файла
JSIOCGAXES = 0x80016a11  # Адресс осей джойстика
JSIOCGBUTTONS = 0x80016a12  # Адресс кнопок джойстика
JSIOCGNAME = 0x81006a13  # Адресс названия джойстика
JSIOCGAXMAP = 0x80406a32  # Адресс карты осей
JSIOCGBTNMAP = 0x80406a34  # Адресс карты кнопок

# карты осей и кнопок, взяты из стандартных джойстиков(возможно не все)
axisNames = {
    0x00: 'x',
    0x01: 'y',
    0x02: 'z',
    0x03: 'rx',
    0x04: 'ry',
    0x05: 'rz',
    0x06: 'trottle',
    0x07: 'rudder',
    0x08: 'wheel',
    0x09: 'gas',
    0x0a: 'brake',
    0x10: 'hat0x',
    0x11: 'hat0y',
    0x12: 'hat1x',
    0x13: 'hat1y',
    0x14: 'hat2x',
    0x15: 'hat2y',
    0x16: 'hat3x',
    0x17: 'hat3y',
    0x18: 'pressure',
    0x19: 'distance',
    0x1a: 'tilt_x',
    0x1b: 'tilt_y',
    0x1c: 'tool_width',
    0x20: 'volume',
    0x28: 'misc',
}

buttonNames = {
    0x120: 'trigger',
    0x121: 'thumb',
    0x122: 'thumb2',
    0x123: 'top',
    0x124: 'top2',
    0x125: 'pinkie',
    0x126: 'base',
    0x127: 'base2',
    0x128: 'base3',
    0x129: 'base4',
    0x12a: 'base5',
    0x12b: 'base6',
    0x12f: 'dead',
    0x130: 'a',
    0x131: 'b',
    0x132: 'c',
    0x133: 'x',
    0x134: 'y',
    0x135: 'z',
    0x136: 'tl',
    0x137: 'tr',
    0x138: 'tl2',
    0x139: 'tr2',
    0x13a: 'select',
    0x13b: 'start',
    0x13c: 'mode',
    0x13d: 'thumbl',
    0x13e: 'thumbr',

    0x220: 'dpad_up',
    0x221: 'dpad_down',
    0x222: 'dpad_left',
    0x223: 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0: 'dpad_left',
    0x2c1: 'dpad_right',
    0x2c2: 'dpad_up',
    0x2c3: 'dpad_down',
}


class Joystick(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self._path = None  # Путь к Джойстику
        self._axisMap = []  # Доступные оси на данном джойстике
        self._buttonMap = []  # Доступные кнопки на данном Джойстике
        self._axisStates = {}  # Словарь, хранящий текущие состояния осей
        self._buttonStates = {}  # Словарь, хранящий текущие состояния кнопок(нажата, отжата)
        self._jsdev = None  # Файл джойстика(грубо говоря)
        self._name = None  # Имя джойстика
        self._axisNum = 0  # Количество доступных осей
        self._buttonsNum = 0  # Количество доступных кнопок
        self._EXIT = False  # Метка выхода из потока
        self._buttonHandler = {}  # Словарь, хранящий обработчики событий нажатия кнопок
        self._EV = RTCEventMaster.EventMaster()
        self._EV.start()

    def info(self):  # Вывод информации о всех найденных параметрах
        print(self)

    def __repr__(self):
        return 'Device name: %s' % self._name + "\n" + \
               'Device path: %s' % self._path + "\n" + \
               '%d axis found: %s' % (self._axisNum, ', '.join(self._axisMap)) + "\n" + \
               '%d buttons found: %s' % (self._buttonsNum, ', '.join(self._buttonMap))

    def connect(self, path):  # Подключается к джойстику по path
        self._path = path
        buf = b' '  # Временный буфер
        try:
            self._jsdev = open(path, 'rb')  # Открываем джойстик
        except FileNotFoundError:
            raise JoyNotFoundError("Joystick not found")  # Вызов исключения
        else:
            buf = array.array('b', buf * 50)  # Cоздаем массив с 50ю итерируемыми объектами
            ioctl(self._jsdev, JSIOCGNAME, buf)  # Записываем в buf имя джойстика
            self._name = buf.tostring()  # переводим в строку и записываем в jname

            buf = array.array('B', [0])  # Создаем массив с 1 итерируемым объектом
            ioctl(self._jsdev, JSIOCGBUTTONS, buf)  # Записываем в buf количество доступных кнопок
            self._buttonsNum = buf[0]  # Записываем в buttonNum количество доступных кнопок

            buf = array.array('B', [0])  # Создаем массив с 1 итерируемым объектом
            ioctl(self._jsdev, JSIOCGAXES, buf)  # Записываем в buf количество доступных осей
            self._axisNum = buf[0]  # Записываем в axisNum количество доступных осей

            buf = array.array('B', [0] * 40)  # Cоздаем массив с 40ю итерируемыми объектами
            ioctl(self._jsdev, JSIOCGAXMAP, buf)  # Записываем в buf карту осей

            for axis in buf[:self._axisNum]:  # По каждой найденной оси
                axisName = axisNames.get(axis, 'unknown(0x%02x)' % axis)  # Присваиваем имя этой оси
                self._axisMap.append(axisName)  # Добавить ось в карту
                self._axisStates[axisName] = 0.0  # Присвоить данной оси начальное значение 0

            buf = array.array('H', [0] * 200)  # Создаем 2х байтовый массив с 200/2 итерируемыми объектами
            ioctl(self._jsdev, JSIOCGBTNMAP, buf)  # Записываем в buf карту кнопок

            for btn in buf[:self._buttonsNum]:  # По каждой найденной кнопке
                btnName = buttonNames.get(btn, 'unknown(0x%03x)' % btn)  # Присваиваем имя этой кнопке
                self._buttonMap.append(btnName)  # Добавить кнопку в карту
                self._buttonStates[btnName] = False  # Присвоить данной кнопке начальное значение False

    def _read(self):
        try:
            evbuf = self._jsdev.read(8)  # Прочитать из буфера событий данные
        except TimeoutError:
            pass
        except OSError:
            raise JoyCrashError("Joystick crash")
        except AttributeError:
            raise InternalError("Joystick not open")
        else:
            if evbuf:
                _, value, stype, number = struct.unpack('IhBB',
                                                        evbuf)  # Распаковка прочитанных данных
                if stype & 0x80:  # если на выходе 0x80, джойстик еще инициализируется
                    pass

                if stype & 0x01:  # если 0x01, то пришедшие данные с кнопки
                    button = self._buttonMap[number]  # берем кнопку из карты кнопок по принятому номеру
                    if button:
                        if self._buttonStates[button] != value:
                            if value:
                                # print("Кнопка нажата")
                                handler = self._buttonHandler.get(
                                    button)  # берем обработчик нажатия кнопки, который мы скинули в список
                                if handler:  # если он существует
                                    handler.push()  # вызвать его
                            else:
                                pass
                                # print("Кнопка отжата")
                        self._buttonStates[
                            button] = value  # присвоить значению словаря по текущей кнопке принятое значение

                if stype & 0x02:  # если на выходе 0x02
                    axis = self._axisMap[number]  # берем ось из карты кнопок по принятому номеру
                    if axis:
                        self._axisStates[axis] = value / 32767.0  # присвоить значению словаря по текущей оси
                        # принятое значение + нормализуем ось

    def run(self):  # потоковая ф-ия
        while not self._EXIT:
            self._read()

    def exit(self):  # ф-ия выхода
        self._EXIT = True
        self._EV.exit()

    @property  # свойство, доступ к осям
    def Axis(self):  # возвращает словарь со всеми осями и их значениями
        return self._axisStates

    @property  # свойство, доступ к кнопкам
    def Buttons(self):  # возвращает словарь со всеми кнопками и их значениями
        return self._buttonStates

    def connectButton(self, buttonName, handler):  # подключает handler к кнопке с именем buttonName
        for but in self._buttonMap:  # пробегает по всем доступным кнопкам
            if but == buttonName:  # если такая кнопка есть
                ev = RTCEventMaster.EventBlock()  # создать блок события
                ev.setfun(handler)  # дать ему функцию
                self._EV.append(ev)  # добавить его в EVENT_MASTER
                self._buttonHandler.update({but: ev})  # добавить блок в словарь
                return
        raise ButtonError("Такой кнопки нет")  # вызвать исключение
