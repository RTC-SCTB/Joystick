#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
import array
from fcntl import ioctl
import threading
import eventmaster


class JoyCrashError(Exception):
    """ Исключение поломки джойстика """
    pass


class JoyNotFoundError(Exception):
    """ Исключение отсутствия джойстика """
    pass


class InternalError(Exception):
    """ Внутренняя ошибка """
    pass


class ButtonError(Exception):
    """ Ошибка кнопки """
    pass


# Взято из какого-то системного файла
_JSIOCGAXES = 0x80016a11  # Адресс осей джойстика
_JSIOCGBUTTONS = 0x80016a12  # Адресс кнопок джойстика
_JSIOCGNAME = 0x81006a13  # Адресс названия джойстика
_JSIOCGAXMAP = 0x80406a32  # Адресс карты осей
_JSIOCGBTNMAP = 0x80406a34  # Адресс карты кнопок

# карты осей и кнопок, взяты из стандартных джойстиков(возможно не все)
_axisNames = {
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

_buttonNames = {
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
    """ Класс джойстика """
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self._path = None  # Путь к Джойстику
        self.__axisMap = []  # Доступные оси на данном джойстике
        self.__buttonMap = []  # Доступные кнопки на данном Джойстике
        self._axisStates = {}  # Словарь, хранящий текущие состояния осей
        self._buttonStates = {}  # Словарь, хранящий текущие состояния кнопок(нажата, отжата)
        self._jsdev = None  # Файл джойстика(грубо говоря)
        self._name = None  # Имя джойстика
        self.__exit = False  # Метка выхода из потока
        self._eventMaster = eventmaster.EventMaster()
        self._eventMaster.start()

    def info(self):
        """ Вывод информации о всех найденных параметрах """
        print(self)

    def __repr__(self):
        """ Специальный метод, выдающий информацию о джойстике """
        return 'Device name: %s' % self._name + "\n" + \
               'Device path: %s' % self._path + "\n" + \
               '%d axis found: %s' % (len(self._axisStates), ', '.join(self._axisStates.keys())) + "\n" + \
               '%d buttons found: %s' % (len(self._buttonStates), ', '.join(self._buttonStates.keys()))

    def open(self, path):
        """ Подключается к джойстику по path """
        self._path = path
        buf = b' '  # Временный буфер
        try:
            self._jsdev = open(path, 'rb')  # Открываем джойстик
        except FileNotFoundError:
            raise JoyNotFoundError("Joystick not found")  # Вызов исключения
        else:
            buf = array.array('b', buf * 50)  # Cоздаем массив с 50ю итерируемыми объектами
            ioctl(self._jsdev, _JSIOCGNAME, buf)  # Записываем в buf имя джойстика
            self._name = buf.tostring()  # переводим в строку и записываем в jname

            buf = array.array('B', [0])  # Создаем массив с 1 итерируемым объектом
            ioctl(self._jsdev, _JSIOCGBUTTONS, buf)  # Записываем в buf количество доступных кнопок
            buttonsNum = buf[0]  # Записываем в buttonNum количество доступных кнопок

            buf = array.array('B', [0])  # Создаем массив с 1 итерируемым объектом
            ioctl(self._jsdev, _JSIOCGAXES, buf)  # Записываем в buf количество доступных осей
            axisNum = buf[0]  # Записываем в axisNum количество доступных осей

            buf = array.array('B', [0] * 40)  # Cоздаем массив с 40ю итерируемыми объектами
            ioctl(self._jsdev, _JSIOCGAXMAP, buf)  # Записываем в buf карту осей

            for axis in buf[:axisNum]:  # По каждой найденной оси
                axisName = _axisNames.get(axis, 'unknown(0x%02x)' % axis)  # Присваиваем имя этой оси
                self.__axisMap.append(axisName)
                self._axisStates[axisName] = 0.0
                # обработчиков

            buf = array.array('H', [0] * 200)  # Создаем 2х байтовый массив с 200/2 итерируемыми объектами
            ioctl(self._jsdev, _JSIOCGBTNMAP, buf)  # Записываем в buf карту кнопок

            for btn in buf[:buttonsNum]:  # По каждой найденной кнопке
                btnName = _buttonNames.get(btn, 'unknown(0x%03x)' % btn)  # Присваиваем имя этой кнопке
                self.__buttonMap.append(btnName)
                self._buttonStates[btnName] = False

    def _read(self):
        """ ф-ия чтения данных с джойстика """
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
                    button = self.__buttonMap[number]  # берем кнопку из карты кнопок по принятому номеру
                    if button:
                        self._buttonStateChange(button, value)
                        self._buttonStates[button] = value  # присвоить значению словаря по
                        # текущей кнопке принятое значение

                if stype & 0x02:  # если на выходе 0x02
                    axis = self.__axisMap[number]  # берем ось из карты кнопок по принятому номеру
                    if axis:
                        self._axisStateChange(axis, value)
                        self._axisStates[axis] = value / 32767.0  # присвоить значению словаря по текущей оси
                        # принятое значение + нормализуем ось

    def _buttonStateChange(self, name, value):
        """ ф-ия, которая вызывается, когда изменяется состояние какой-либо кнопки """
        if self._buttonStates[name] != value:
            event = self._eventMaster.getEventByName(str(name) + "ButtonClick")
            if event:
                event.push(value)

    def _axisStateChange(self, name, value):
        """ ф-ия, которая вызывается, когда изменяется состояние оси """
        pass

    def run(self):
        """ потоковая ф-ия """
        while not self.__exit:
            self._read()

    def exit(self):
        """ ф-ия выхода """
        self.__exit = True
        self._eventMaster.exit()

    @property
    def axis(self):
        """ свойство, доступ к осям: возвращает словарь со всеми осями и их значениями """
        return self._axisStates

    @property
    def buttons(self):
        """ свойство, доступ к кнопкам: возвращает словарь со всеми кнопками и их значениями """
        return self._buttonStates

    def onButtonClick(self, buttonName, handler):
        """ подключение handler-обработчика события к событию Click, к кнопке с именем buttonName  """
        button = self._buttonStates.get(buttonName)
        if button is None:
            raise ButtonError("Такой кнопки нет")  # вызвать исключение
        event = eventmaster.Event(str(buttonName) + "ButtonClick")     # создаем событие
        event.connect(handler)  # привязать обработчик события к событию
        self._eventMaster.append(event)     # добавить событие в обработчик событий
