#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import threading


class EventBlock:
    def __init__(self, name=None, fun=None):  # конструктор класса EventBlock
        self.name = name  # имя события
        self.event = threading.Event()  # событие
        self.foo = fun  # функция события

    def setfun(self, f):  # установить функцию события
        self.foo = f

    def push(self):  # вызвать событие
        self.event.set()


class EventMaster(threading.Thread):
    def __init__(self, freq=20):  # конструктор класса EventMaster
        threading.Thread.__init__(self)
        self.eventList = []  # список возможных событий, с привязанными ф-ями
        self.eventQueue = []  # очередь выполнения функций событий
        self.Exit = False  # метка выхода из потока
        self.threads = []  # список потоков
        self.timeSleep = 1/(freq+1)    # частота вызова событий

    def run(self):  # функция потока EM
        while not self.Exit:  # пока нет метки выхода из потока
            for element in self.eventList:  # проход по всем элементам списка событий
                if element.event.isSet():  # если какое-то из событий произошло
                    self.eventQueue.append(element)  # заполнить очередь этим событием
                    element.event.clear()  # снять метку события

                if len(self.eventQueue) > 0:  # если очередь не пуста
                    self.threads.append(threading.Thread(target=self.eventQueue.pop(0).foo))  # добавить в список
                    #  потоков функцию, принадлежащую первому элементу очереди, при этом удаляя его из очереди
                    self.threads.pop(0).start()  # запустить первый элемент списка потоков, при этом удаляя его
            time.sleep(self.timeSleep)

    def exit(self):  # функция выхода из потока
        self.Exit = True

    def append(self, event):  # добавления нового элемента EventBlock в список возможных событий
        self.eventList.append(event)
