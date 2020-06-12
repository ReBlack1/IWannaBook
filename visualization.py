#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import matplotlib.pyplot as plt
import networkx as nx

def f_plot(*args, **kwargs):
    """
    Вернет график, который можно
    показать через .show(), сохранить через .savefig('example 142b.png', fmt='png')
    :param args: x1, y1, x2, y2... списки одинакового раззмера
    :param kwargs: параметры:
    colors - массив с цветами ['red', 'blue'], кол-во цветов равно кол-ву графиков
    linewidth - толщина линии в float 2.
    place - расположение графика задается трехзначным числом:
    111 - весь экран
    1-е число деление по горизонтали
    2-е по вертикали
    3-е в какой части будет находится график
    plot_names - массив с названием линий, размер равен кол-ву графиков
    :return: объект фигуры
    """
    # Перетаскиваем инфу из аргументов в массивы
    xlist = []
    ylist = []
    for i, arg in enumerate(args):
        if (i % 2 == 0):
            xlist.append(arg)
        else:
            ylist.append(arg)
    # Запоминаем параметры
    q_plots = len(args)//2
    colors = kwargs.pop('colors', ['k']*q_plots)  # По умолчанию - черным
    linewidth = kwargs.pop('linewidth', 1.)
    place = kwargs.pop('place', 111)  # По умолчанию - на весь экран
    plot_names = kwargs.pop('plot_names', [i for i in range(1, q_plots+1)])

    fig = plt.figure()
    ax = fig.add_subplot(place)
    i = 0
    for x, y, color in zip(xlist, ylist, colors):
        ax.plot(x, y, color=color, linewidth=linewidth, label=plot_names[i])
        i += 1

    ax.grid(True)
    ax.legend()
    return plt


