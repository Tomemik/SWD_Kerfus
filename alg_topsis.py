#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from a_star import astar_search


def naiwny_filtracja(X):
    P = []
    n = X.shape[0]

    for i in range(n):
        if np.isnan(X[i]).any():  # skip iterations with deleted/broken elements
            continue
        Y = X[i]
        y_index = i  # save Y index for possible deletion
        for j in range(i + 1, n):
            if np.isnan(X[j]).any():  # skip iterations with deleted/broken elements
                continue
            # noinspection PyTypeChecker
            if all(Y <= X[j]):
                X[j] = np.NaN
            # noinspection PyTypeChecker
            elif all(X[j] <= Y):
                Y = X[j]
                X[y_index] = np.NaN
                y_index = j  # save Y index for possible deletion
        if not np.isnan(Y).any():
            P.append(Y.tolist())  # append new find
            for k in range(n):
                if np.isnan(X[k]).any():
                    continue
                else:
                    # noinspection PyTypeChecker
                    if all(Y <= X[k]):
                        X[k] = np.NaN
            X[y_index] = np.NaN
            eli = 0
            P0 = []
            for el in X:  # count not-deleted items
                if (~np.isnan(el)).any():
                    eli = eli + 1
                    P0 = el
            if eli == 1:  # if one element left
                P.append(P0.tolist())  # append last element
                break
    return np.asarray(P)


# main algorithm
def find_best(A, W, search_for_min, points):
    A_shape = A.shape
    M_norm = np.zeros(A_shape)

    for j in range(A_shape[1]):  # iterate over columns
        abs_dj = np.linalg.norm(A[:, j])
        for i in range(A_shape[0]):  # iterate over elements in column
            if search_for_min[j]:  # if row flip flag is on
                M_norm[i, j] = (1 - (A[i, j] / abs_dj)) * W[j]  # calculate normalized el with flip
            else:  # default
                M_norm[i, j] = A[i, j] / abs_dj * W[j]
    #print("Macierz znormalizowana z wagami")
    #print(M_norm)

    v_ideal = np.min(M_norm, axis=0)

    not_dominated = naiwny_filtracja(M_norm.copy())

    v_not_ideal = np.max(not_dominated, axis=0)  # nadir
    #v_not_ideal = np.min(M_norm, axis=0)  # basic algorithm

    #print("v* : \n", v_ideal)
    #print("v- : \n", v_not_ideal)

    di_ideal = np.zeros((A_shape[0], 1))
    di_not_ideal = np.zeros((A_shape[0], 1))
    ci = np.zeros((A_shape[0], 1))
    for i in range(A_shape[0]):
        di_ideal[i] = np.sqrt(sum(np.power(M_norm[i, :] - v_ideal, 2)))
        di_not_ideal[i] = np.sqrt(sum(np.power(M_norm[i, :] - v_not_ideal, 2)))
        ci[i] = di_not_ideal[i] / (di_ideal[i] + di_not_ideal[i])

    #print("di+ : \n", di_ideal)
    #print("di- : \n", di_not_ideal)
    #print("ci : \n", ci)

    A = np.hstack((points, ci, A))  # add record number column, add calculated ci

    A = A[A[:, 2].argsort()[::-1]]  # sort matrix by ci, make it descending order
    A[:, 2] = np.around(A[:, 2], decimals=3)  # round ci to make it display better

    np.set_printoptions(suppress=True)  # display results in non-scientific formatting
    #print("Top 5: ")
    names = [["x", "y", "ci", "popularność", "szerokość przejazdu", "przeszkadzanie", "odległość"]]
    ranking = np.append(names, A, axis=0)
    #print(tabulate(ranking[:6], headers='firstrow'))
    # wynik metody zmodyfikowanej - punkt antyidealny to nadir
    # wyswietlam orginalne dane z dodatkowym numerem (kolumna id = numer wiersza w wejściowej tabeli liczony od 1)
    # i obliczoną wagą
    return A[0], ranking[:6]


def change_distance(table, distances, point, points_ref):
    for idx, el in enumerate(table[:, :2]):
        if (el == point).all():
            idx_to_del = idx

    table[:, -1] = distances[idx_to_del]
    table = np.delete(table, idx_to_del, 0)
    distances = np.delete(distances, idx_to_del, 0)
    distances = np.delete(distances, idx_to_del, 1)
    points_ref = np.delete(points_ref, idx_to_del, 0)

    return table, distances, points_ref


def topsis_n_points(table_original, weights, search_min, points_ref, distance_each_other, n):
    table_current = np.copy(table_original)
    distances_current = np.copy(distance_each_other)
    points_ref_current = np.copy(points_ref)
    path = np.array([[0, 0, 0, 0, 0, 0, 0]])
    choices = [np.zeros((6, 7))]

    for _ in range(n):
        res, choice = find_best(table_current[:, 2:], weights, search_min, list(zip(table_current[:, 0], table_current[:, 1])))
        path = np.concatenate((path, [res]), axis=0)
        choices = np.concatenate((choices, [choice]), axis=0)
        table_current, distances_current, points_ref_current = change_distance(table_current, distances_current, res[:2], points_ref_current)

    return path[1:], choices[1:]

def topsis_results(points, weights, points_ref, shop_map, distance_each_other, base_coords):
    kerfus, choices = topsis_n_points(points, weights, [1, 1, 0, 0], points_ref, distance_each_other, 10)
    kerfus_tab = [["lp", "x", "y", "ci", "popularność", "szerokość przejazdu", "przeszkadzanie", "odległość"]]

    for i, el in enumerate(kerfus):
        kerfus_tab = np.append(kerfus_tab, [np.append(i + 1, el)], axis=0)

    #print(tabulate(kerfus_tab, headers="firstrow"))

    kerfus = np.append([[base_coords[0], base_coords[1], 0, 0, 0, 0, 0]], kerfus, axis=0)

    shelves = np.argwhere(shop_map == 1)
    entrance = np.argwhere(shop_map == 2)
    exit = np.argwhere(shop_map == 3)
    bread = np.argwhere(shop_map == 4)
    meat = np.argwhere(shop_map == 5)

    fig, ax = plt.subplots()

    ax.scatter(points[:, 0], points[:, 1], c='red', s=5)
    for ix in range(kerfus.shape[0] - 1):
        path = astar_search(shop_map, tuple(map(int, kerfus[ix, :2])), tuple(map(int, kerfus[ix + 1, :2])))
        path = np.array(path)
        plt.plot(path[:, 0], path[:, 1], '--', c='#1f77b4')
    ax.scatter(kerfus[:, 0], kerfus[:, 1])
    ax.scatter(shelves[:, 0], shelves[:, 1], c='lightblue', marker='s', s=26)
    ax.scatter(entrance[:, 0], entrance[:, 1], c='green', marker='s', s=26)
    ax.scatter(exit[:, 0], exit[:, 1], c='red', marker='s', s=26)
    ax.scatter(bread[:, 0], bread[:, 1], c='grey', marker='s', s=26)
    ax.scatter(meat[:, 0], meat[:, 1], c='orange', marker='s', s=26)

    for i in range(kerfus.shape[0]):
        plt.annotate(i, tuple(kerfus[i, :2]))

    ax.set_axisbelow(True)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim((-0.5, 55.5))
    ax.set_ylim((28.5, -0.5))
    ax.grid(which='both', linewidth=0.25)
    plt.xticks([])
    plt.yticks([])
    ax.tick_params(which='both', length=0)

    return kerfus_tab, choices, fig
