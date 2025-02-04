#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 08:25:39 2020

@author: err
"""

import random
import matplotlib.pyplot as plt
import numpy as np
import collections
from tqdm import tqdm
import gudhi as gd
from scipy.optimize import curve_fit

"""GROWING"""


def grow_eden(t):
    process = [(0, 0, 0, 0, 0)]
    perimeter_len = [10]
    eden, perimeter = start_eden()

    holes = {}
    total_holes = 0
    barcode = {}
    tags = []
    created_holes = []

    betti_4_total = 0
    betti_4_vector = [0]
    betti_4_total_vector = [0]

    pbar = tqdm(total=t)
    pbar.update(1)

    for i in range(1, t):
        pbar.update(1)

        l = len(perimeter)
        x = random.randint(0, l - 1)
        tile_selected = perimeter[x]
        perimeter.pop(x)

        eden[tile_selected][0] = 1
        process = process + [tile_selected]

        eden, perimeter, nearest_n, nearest_n_tiles = actualize_neighbors(tile_selected, eden, perimeter)
        betti_4, total_holes, eden, barcode, holes, created_holes, tags = increment_betti_4(eden, tile_selected,
                                                                                            nearest_n, nearest_n_tiles,
                                                                                            barcode, i, holes,
                                                                                            total_holes, created_holes,
                                                                                            tags)
        betti_4_total = betti_4_total + betti_4
        betti_4_vector = betti_4_vector + [betti_4]
        betti_4_total_vector = betti_4_total_vector + [betti_4_total]

        l = len(perimeter)
        perimeter_len = perimeter_len + [l]
    pbar.close()
    final_barcode = barcode_forest(barcode, tags)

    return eden, perimeter, betti_4_total_vector, barcode, holes, created_holes, process, perimeter_len, final_barcode


"""GUDHI"""


def convert_gudhi(process, folder_name):
    min_x = min(process, key=lambda x: x[0])
    max_x = max(process, key=lambda x: x[0])
    min_y = min(process, key=lambda x: x[1])
    max_y = max(process, key=lambda x: x[1])
    min_z = min(process, key=lambda x: x[2])
    max_z = max(process, key=lambda x: x[2])
    min_w = min(process, key=lambda x: x[3])
    max_w = max(process, key=lambda x: x[3])
    min_v = min(process, key=lambda x: x[4])
    max_v = max(process, key=lambda x: x[4])
    dimension = 5
    long = max_x[0] + ((-1) * (min_x[0])) + 1
    wide = max_y[1] + ((-1) * (min_y[1])) + 1
    deep = max_z[2] + ((-1) * (min_z[2])) + 1
    blup = max_w[3] + ((-1) * (min_w[3])) + 1
    clop = max_v[4] + ((-1) * (min_v[4])) + 1

    time = len(process)
    filename = folder_name + '/gudhi.txt'

    total = long * wide * deep * blup * clop
    pbar = tqdm(total=total, position=0, leave=True)

    with open(filename, 'w+') as f:
        f.writelines('%d\n' % dimension)
        f.writelines('%d\n' % long)
        f.writelines('%d\n' % wide)
        f.writelines('%d\n' % deep)
        f.writelines('%d\n' % blup)
        f.writelines('%d\n' % clop)

        for v in range(min_v[4], max_v[4] + 1):
            for w in range(min_w[3], max_w[3] + 1):
                for z in range(min_z[2], max_z[2] + 1):
                    for i in range(min_y[1], max_y[1] + 1):
                        for j in range(min_x[0], max_x[0] + 1):
                            pbar.update(1)
                            if (j, i, z, w, v) in process:
                                f.writelines('%d\n' % process.index((j, i, z, w, v)))
                            else:
                                f.writelines('inf\n')
    pbar.close()
    return filename


def convert_perseus_2(Process):
    dimension = 4
    with open('500000_1_5D.txt', 'w') as f:
        f.writelines('%d\n' % dimension)
        i = 0
        for x in Process:
            i = i + 1
            y = (x[0], x[1], x[2], x[3], x[4], i)
            f.writelines('%s %s %s %s %s %s\n' % y)


def gudhi_analysis(filename, final_barcode, folder_name, length):
    print('\nCreating Cubical Complex...')
    eden_model = gd.CubicalComplex(perseus_file=filename)
    print('Computing Persistence...')
    eden_model.persistence()
    barcode_gudhi = eden_model.persistence_intervals_in_dimension(4)
    final = np.array(final_barcode)
    barcode_gudhi_sorted = barcode_gudhi.sort()
    final_sorted = final.sort()
    if barcode_gudhi_sorted == final_sorted:
        print("Gudhi Barcode agrees with our Barcode!")
    else:
        print("!!!!")

    print("\nDrawing Barcode for Betti_1...")
    pers_1 = [x for x in eden_model.persistence(min_persistence=length[0]) if x[0] == 1]
    fig, ax = plt.subplots()
    gd.plot_persistence_barcode(persistence=pers_1, max_barcodes=1000)
    ax.set_title(r'Persistence Barcode $\beta_1$')
    plt.savefig(folder_name + '/barcode_1.png', dpi=1200)

    print("\nDrawing Barcode for Betti_2...")
    pers_2 = [x for x in eden_model.persistence(min_persistence=length[1]) if x[0] == 2]
    fig, ax = plt.subplots()
    gd.plot_persistence_barcode(pers_2, max_barcodes=1000)
    ax.set_title(r'Persistence Barcode $\beta_2$')
    plt.savefig(folder_name + '/barcode_2.png', dpi=1200)

    print("\nDrawing Barcode for Betti_3...")
    pers_3 = [x for x in eden_model.persistence(min_persistence=length[2]) if x[0] == 3]
    fig, ax = plt.subplots()
    gd.plot_persistence_barcode(pers_3, max_barcodes=1000)
    ax.set_title(r'Persistence Barcode $\beta_3$')
    plt.savefig(folder_name + '/barcode_3.png', dpi=1200)

    try:
        print("\nDrawing Barcode for Betti_4...")
        pers_4 = [x for x in eden_model.persistence(length[3]) if x[0] == 4]
        fig, ax = plt.subplots()
        gd.plot_persistence_barcode(pers_4, max_barcodes=1000)
        ax.set_title(r'Persistence Barcode $\beta_3$')
        plt.savefig(folder_name + '/barcode_4.png', dpi=1200)
    except IndexError:
        print("No Betti_4 => No Barcode")
    plt.close()

"""PLOTTING"""


def draw_frequencies_4(dict, changes, folder_name):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    l = len(dict[0])

    ch_5 = [i for i, j in enumerate(changes) if j == 5]
    y_5 = []
    for x in ch_5:
        y_5 += [dict[5][x + 1]]

    sh = []
    for j in np.arange(-1, 2):
        sh.append(next((i for i, x in enumerate(dict[j]) if x), 0))
    shift = max(sh)

    if next((i for i, x in enumerate(dict[-1]) if x), 0) != 0:
        ax.plot(range(shift, l), dict[-1][shift:], color='tab:olive', label='-1', linewidth=0.75)
    ax.plot(range(shift, l), dict[0][shift:], color='tab:blue', label='0', linewidth=0.75)
    if next((i for i, x in enumerate(dict[1]) if x), 0) != 0:
        ax.plot(range(shift, l), dict[1][shift:], color='tab:red', label='+1', linewidth=0.75)
    if next((i for i, x in enumerate(dict[2]) if x), 0) != 0:
        ax.plot(range(shift, l), dict[2][shift:], color='tab:orange', label='+2', linewidth=0.75)
    if next((i for i, x in enumerate(dict[3]) if x), 0) != 0:
        ax.plot(range(shift, l), dict[3][shift:], color='tab:green', label='+3', linewidth=0.75)
    if next((i for i, x in enumerate(dict[4]) if x), 0) != 0:
        ax.plot(range(shift, l), dict[4][shift:], color='black', label='+4', linewidth=0.75)

    if next((i for i, x in enumerate(dict[5]) if x), 0) != 0:
        plt.scatter(ch_5, y_5, s=5, marker='o', color="tab:brown", label='+5')

    plt.yscale('log')

    ax.set_ylabel(r'Frequency of Change in $\beta_4$')
    ax.set_xlabel('t')
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax.legend(loc=1, prop={'size': 6})
    fig.savefig(folder_name + '/fr_b_4.png', format='png', dpi=1200)
    plt.close()


def plot_b_per(Betti_4_total_vector, Per, time, N, folder_name):
    n = int(time / 10)

    def func(x, a, b):
        return a * x ** b

    ydata_f = Betti_4_total_vector
    xdata_f = range(len(ydata_f))
    ydata = ydata_f[N:]
    xdata = xdata_f[N:]
    plt.xscale('log')
    plt.yscale('log')
    plt.plot(xdata_f[n:], ydata_f[n:], 'm-', label=r'$\beta_4(t)$ data', linewidth=0.75)
    popt, pcov = curve_fit(func, xdata, ydata)

    plt.plot(xdata_f[n:], func(xdata_f[n:], *popt), 'm--', label=r'fit: $y=%5.2f x^{%5.3f}$' % tuple(popt),
             linewidth=0.75)

    ydata = Per
    xdata = range(len(ydata))
    plt.plot(xdata[n:], ydata[n:], color='orange', linestyle='solid', label=r'$P(t)$ data', linewidth=0.75)
    popt, pcov = curve_fit(func, xdata, ydata)
    plt.plot(xdata[n:], func(xdata[n:], *popt), color='orange', linestyle='dashed',
             label=r'fit: $y=%5.2f x^{%5.3f}$' % tuple(popt), linewidth=0.75)

    plt.xlabel('t')
    plt.ylabel('data')
    plt.legend(prop={'size': 6}, loc=2)
    plt.tight_layout()

    plt.savefig(folder_name + '/per-b-time.png', dpi=1200)
    plt.close()


"""SUPPLEMENTARY FUNCTIONS"""


def read_eden_txt(filename):
    eden = []
    for t in open(filename).read().split('), ('):
        a, b, c, d, e, t = t.strip('()[]').split(',')
        a = a.strip()
        b = b.strip()
        c = c.strip()
        d = d.strip()
        e = e.strip(')')
        t = t.strip(")]\n")
        eden.append(((int(a), int(b), int(c), int(d), int(e)), float(t)))
    return eden


def return_frequencies_4(vect, time):
    changes = [vect[i + 1] - vect[i] for i in range(len(vect) - 1)]
    values = list(set(changes))
    values.sort()
    values = [-1, 0, 1, 2, 3, 4, 5]
    freq = {i: [0] for i in values}

    for i in tqdm(range(1, time + 1), position=0, leave=True):
        counter = collections.Counter(changes[:i])
        for k in values:
            freq[k].append(counter[k] / i)
    return freq, changes


def hamming2(s1, s2):
    """Calculate the Hamming distance between two bit strings"""
    assert len(s1) == len(s2)
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


def start_eden():
    eden = {(0, 0, 0, 0, 0): [1, 0, 0],
            (0, 0, 1, 0, 0): [0, 1, 0],
            (0, 0, -1, 0, 0): [0, 1, 0],
            (1, 0, 0, 0, 0): [0, 1, 0],
            (-1, 0, 0, 0, 0): [0, 1, 0],
            (0, 1, 0, 0, 0): [0, 1, 0],
            (0, -1, 0, 0, 0): [0, 1, 0],
            (0, 0, 0, 1, 0): [0, 1, 0],
            (0, 0, 0, -1, 0): [0, 1, 0],
            (0, 0, 0, 0, 1): [0, 1, 0],
            (0, 0, 0, 0, -1): [0, 1, 0]
            }
    perimeter = [(0, 0, 1, 0, 0), (0, 0, -1, 0, 0), (1, 0, 0, 0, 0), (-1, 0, 0, 0, 0), (0, 1, 0, 0, 0),
                 (0, -1, 0, 0, 0), (0, 0, 0, 1, 0), (0, 0, 0, -1, 0), (0, 0, 0, 0, 1), (0, 0, 0, 0, -1)]
    return eden, perimeter


def actualize_neighbors(tile_selected, Eden, Perimeter):
    n3 = [tile_selected[0] + 1, tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4]]
    n4 = [tile_selected[0] - 1, tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4]]
    n5 = [tile_selected[0], tile_selected[1] + 1, tile_selected[2], tile_selected[3], tile_selected[4]]
    n6 = [tile_selected[0], tile_selected[1] - 1, tile_selected[2], tile_selected[3], tile_selected[4]]
    n1 = [tile_selected[0], tile_selected[1], tile_selected[2] + 1, tile_selected[3], tile_selected[4]]
    n2 = [tile_selected[0], tile_selected[1], tile_selected[2] - 1, tile_selected[3], tile_selected[4]]
    n7 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3] + 1, tile_selected[4]]
    n8 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3] - 1, tile_selected[4]]
    n9 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4] + 1]
    n10 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4] - 1]

    n1 = tuple(n1)
    n2 = tuple(n2)
    n3 = tuple(n3)
    n4 = tuple(n4)
    n5 = tuple(n5)
    n6 = tuple(n6)
    n7 = tuple(n7)
    n8 = tuple(n8)
    n9 = tuple(n9)
    n10 = tuple(n10)

    nearest_n_tiles = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10]

    nearest_n = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    if n1 in Eden:
        Eden[n1][1] = Eden[n1][1] + 1
        if Eden[n1][0] == 1:
            nearest_n[0] = 1
    else:
        Eden[n1] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n1]

    if n2 in Eden:
        Eden[n2][1] = Eden[n2][1] + 1
        if Eden[n2][0] == 1:
            nearest_n[1] = 1
    else:
        Eden[n2] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n2]

    if n3 in Eden:
        Eden[n3][1] = Eden[n3][1] + 1
        if Eden[n3][0] == 1:
            nearest_n[2] = 1
    else:
        Eden[n3] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n3]

    if n4 in Eden:
        Eden[n4][1] = Eden[n4][1] + 1
        if Eden[n4][0] == 1:
            nearest_n[3] = 1
    else:
        Eden[n4] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n4]

    if n5 in Eden:
        Eden[n5][1] = Eden[n5][1] + 1
        if Eden[n5][0] == 1:
            nearest_n[4] = 1
    else:
        Eden[n5] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n5]

    if n6 in Eden:
        Eden[n6][1] = Eden[n6][1] + 1
        if Eden[n6][0] == 1:
            nearest_n[5] = 1
    else:
        Eden[n6] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n6]

    if n7 in Eden:
        Eden[n7][1] = Eden[n7][1] + 1
        if Eden[n7][0] == 1:
            nearest_n[6] = 1
    else:
        Eden[n7] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n7]

    if n8 in Eden:
        Eden[n8][1] = Eden[n8][1] + 1
        if Eden[n8][0] == 1:
            nearest_n[7] = 1
    else:
        Eden[n8] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n8]

    if n9 in Eden:
        Eden[n9][1] = Eden[n9][1] + 1
        if Eden[n9][0] == 1:
            nearest_n[8] = 1
    else:
        Eden[n9] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n9]

    if n10 in Eden:
        Eden[n10][1] = Eden[n10][1] + 1
        if Eden[n10][0] == 1:
            nearest_n[9] = 1
    else:
        Eden[n10] = [0, 1, Eden[tile_selected][2]]
        Perimeter = Perimeter + [n10]

    return Eden, Perimeter, nearest_n, nearest_n_tiles


def add_neighbours_bds(bds, j, iterations, num_possible_components, merged, finished, Eden):
    tile_selected = bds[j][iterations]

    n3 = [tile_selected[0] + 1, tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4]]
    n4 = [tile_selected[0] - 1, tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4]]
    n5 = [tile_selected[0], tile_selected[1] + 1, tile_selected[2], tile_selected[3], tile_selected[4]]
    n6 = [tile_selected[0], tile_selected[1] - 1, tile_selected[2], tile_selected[3], tile_selected[4]]
    n1 = [tile_selected[0], tile_selected[1], tile_selected[2] + 1, tile_selected[3], tile_selected[4]]
    n2 = [tile_selected[0], tile_selected[1], tile_selected[2] - 1, tile_selected[3], tile_selected[4]]
    n7 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3] + 1, tile_selected[4]]
    n8 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3] - 1, tile_selected[4]]
    n9 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4] + 1]
    n10 = [tile_selected[0], tile_selected[1], tile_selected[2], tile_selected[3], tile_selected[4] - 1]

    n1 = tuple(n1)
    n2 = tuple(n2)
    n3 = tuple(n3)
    n4 = tuple(n4)
    n5 = tuple(n5)
    n6 = tuple(n6)
    n7 = tuple(n7)
    n8 = tuple(n8)
    n9 = tuple(n9)
    n10 = tuple(n10)

    nearest_n_tiles = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10]

    nearest_n = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    if n1 in Eden:
        if Eden[n1][0] == 0:
            nearest_n[0] = 1
    else:
        nearest_n[0] = 1

    if n2 in Eden:
        if Eden[n2][0] == 0:
            nearest_n[1] = 1
    else:
        nearest_n[1] = 1

    if n3 in Eden:
        if Eden[n3][0] == 0:
            nearest_n[2] = 1
    else:
        nearest_n[2] = 1

    if n4 in Eden:
        if Eden[n4][0] == 0:
            nearest_n[3] = 1
    else:
        nearest_n[3] = 1

    if n5 in Eden:
        if Eden[n5][0] == 0:
            nearest_n[4] = 1
    else:
        nearest_n[4] = 1

    if n6 in Eden:
        if Eden[n6][0] == 0:
            nearest_n[5] = 1
    else:
        nearest_n[5] = 1

    if n7 in Eden:
        if Eden[n7][0] == 0:
            nearest_n[6] = 1
    else:
        nearest_n[6] = 1

    if n8 in Eden:
        if Eden[n8][0] == 0:
            nearest_n[7] = 1
    else:
        nearest_n[7] = 1

    if n9 in Eden:
        if Eden[n9][0] == 0:
            nearest_n[8] = 1
    else:
        nearest_n[8] = 1

    if n10 in Eden:
        if Eden[n10][0] == 0:
            nearest_n[9] = 1
    else:
        nearest_n[9] = 1

    for i in range(0, 10):
        if nearest_n[i] == 1:
            if nearest_n_tiles[i] not in bds[j]:
                bds[j] = bds[j] + [nearest_n_tiles[i]]
            for t in range(0, num_possible_components):
                if nearest_n_tiles[i] in bds[t]:
                    if t < j:
                        merged[j] = 1
                        finished[j] = 1
                    if t > j:
                        merged[t] = 1
                        finished[t] = 1
    return bds, merged, finished


def increment_betti_4(Eden, tile_selected, nearest_n, nearest_n_tiles, barcode, time, holes, total_holes, created_holes,
                      tags):
    if Eden[tile_selected][2] == 0:
        per = 1  # This is 1 if the tile added was in the out perimeter
    else:
        num_hole = Eden[tile_selected][2]
        per = 0
    # In this case the tile added was in a hole

    betti_4 = 0

    if sum(nearest_n) == 10:
        betti_4 = - 1
        barcode[num_hole][1][1] = float(time + 2)  # Are we covering a hole that was never divided?
        holes[num_hole].remove(tile_selected)
        if holes[num_hole] == []:
            holes.pop(num_hole)

    if sum(nearest_n) == 9:
        betti_4 = 0
        if per == 0:
            holes[num_hole].remove(tile_selected)

    if sum(nearest_n) != 10 and sum(nearest_n) != 9:
        num_possible_components = 0
        bds = []
        iterations = 0
        for i in range(0, 10):
            if nearest_n[i] == 0:
                num_possible_components = num_possible_components + 1
                bds = bds + [[nearest_n_tiles[i]]]

        finished = [0] * num_possible_components
        merged = finished.copy()

        while sum(finished) < num_possible_components - per:
            for j in range(0, num_possible_components):
                if finished[j] == 0:
                    bds, merged, finished = add_neighbours_bds(bds, j, iterations, num_possible_components, merged,
                                                               finished, Eden)
                    if (iterations + 1) == len(bds[j]):
                        finished[j] = 1
            iterations = iterations + 1

        betti_4 = (num_possible_components - 1) - sum(merged)
        # At this point we have the bds components and the ones that were not merged will become the holes.
        # Here we actualize the holes and we actualize Hole No in Eden.
        if betti_4 == 0:
            if per == 0:
                holes[num_hole].remove(tile_selected)

        else:
            if per == 1:
                for i in range(0, num_possible_components):
                    if finished[i] == 1 and merged[i] == 0:
                        total_holes = total_holes + 1
                        holes[total_holes] = bds[i].copy()

                        for x in bds[i]:
                            if x in Eden:
                                Eden[x][2] = total_holes

                        barcode[total_holes] = [0, [float(time + 2), float(0)], [total_holes]]
                        created_holes = created_holes + [[barcode[total_holes][2], bds[i].copy(), len(bds[i])]]

            else:
                if barcode[num_hole][0] == 0:
                    tags = tags + [num_hole]
                    barcode[num_hole][0] = 1

                holes.pop(num_hole)

                for i in range(0, num_possible_components):
                    if finished[i] == 1 and merged[i] == 0:
                        total_holes = total_holes + 1
                        holes[total_holes] = bds[i].copy()
                        for x in bds[i]:
                            if x in Eden:
                                Eden[x][2] = total_holes
                        barcode[total_holes] = [1, [float(time + 2), float(0)], barcode[num_hole][2] + [total_holes]]
                        created_holes = created_holes + [[barcode[total_holes][2], bds[i].copy(), len(bds[i])]]
    return betti_4, total_holes, Eden, barcode, holes, created_holes, tags


def barcode_forest(barcode, tags):
    bars_pure = []
    bars_hole = []
    for x in barcode:
        if barcode[x][0] == 0:
            bars_pure = bars_pure + [barcode[x][1]]

    for x in tags:
        b = {}
        for elem in barcode:
            if barcode[elem][2][0] == x:
                b[tuple(barcode[elem][2])] = barcode[elem][1]
        bars_hole = bars_hole + bars_from_tree(b, x)
    return bars_pure + bars_hole


def bars_from_tree(b, tag):
    n = max(len(x) for x in b)
    bars = []
    while n > 0:
        leaves_parent = [x for x in b if len(x) == n - 1]

        possible_leaves = [x for x in b if len(x) == n]
        for j in leaves_parent:
            leaves = []
            for x in possible_leaves:
                root = list(x)
                del root[-1]
                root = tuple(root)
                if hamming2(j, root) == 0:
                    leaves = leaves + [x]
            if len(leaves) > 0:
                times = []
                for x in leaves:
                    times = times + [b[x][1]]
                if 0 in times:
                    ind = times.index(0)
                    for i in range(0, len(leaves)):
                        if i != ind:
                            bars = bars + [b[leaves[i]]]
                else:
                    ind = times.index(max(times))
                    for i in range(0, len(leaves)):
                        if i != ind:
                            bars = bars + [b[leaves[i]]]
                    b[j][1] = max(times)
        n = n - 1
    bars = bars + [b[(tag,)]]
    return bars
