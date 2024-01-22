import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tabulate
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

import excel
import a_star

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
            if all(Y[2:] <= X[j][2:]):  # modify indices to exclude the first two columns
                X[j] = np.NaN
            # noinspection PyTypeChecker
            elif all(X[j][2:] <= Y[2:]):  # modify indices to exclude the first two columns
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
                    if all(Y[2:] <= X[k][2:]):  # modify indices to exclude the first two columns
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

    if len(P) == 0:
        print("Brak punktow niezdominowanych!")
    return np.asarray(P)


def deleteSpecificRecords(A, wrongEl):  # function to delete records, as specified in wrongEl mask
    n_deleted = sum(wrongEl)
    Aret = np.array(
        [[0.0] * A.shape[1]] * (A.shape[0] - n_deleted))  # creates specific size return matrix
    i = 0
    for it, el in enumerate(A):
        if not wrongEl[it]:
            Aret[i] = A[it]
            i = i + 1
    return Aret


def mutualContradiction(A1, A2):  # function to find and delete mutual contradictions
    # PL: 1. dla każdego a2 e A2 istnieje takie a1 e A1 że a1 <= a2
    wrongElA2 = np.zeros(A2.shape[0]).astype(int)
    for index, a2 in enumerate(A2[:, 2:]):  # Only consider columns starting from the third one
        flag = 0
        for a1 in A1[:, 2:]:  # Only consider columns starting from the third one
            # noinspection PyTypeChecker
            if all(a1 <= a2):
                flag = 1
                break
        if not flag:
            print("sprzecznosc wzajemna 2 wejscia oflagowana i usunieta")
            wrongElA2[index] = 1  # flag wrong element
    A2 = deleteSpecificRecords(A2, wrongElA2)

    # PL: 2. dla każdego a1 e A1 istnieje takie a2 e A2 że a1 <= a2
    wrongElA1 = np.zeros(A1.shape[0]).astype(int)
    for index, a1 in enumerate(A1[:, 2:]):  # Only consider columns starting from the third one
        flag = 0
        for a2 in A2[:, 2:]:  # Only consider columns starting from the third one
            # noinspection PyTypeChecker
            if all(a1 <= a2):
                flag = 1
                break
        if not flag:
            print("sprzecznosc wzajemna 1 wejscia oflagowana i usunieta")
            wrongElA1[index] = 1  # flag wrong element
    A1 = deleteSpecificRecords(A1, wrongElA1)
    # operations on input matrixes, nothing to return



def deleteSpecificRows(A, V):  # function to find delete rows equal to any row in V
    mask = np.zeros(A.shape[0]).astype(int)
    for it, row in enumerate(A[:, 2:]):  # Only consider columns starting from the third one
        for el in V[:, 2:]:  # Only consider columns starting from the third one in V
            if np.array_equal(row, el):  # Use np.array_equal for comparison
                mask[it] = 1  # mark them
                break
    n_deleted = sum(mask)
    Aout = np.zeros((A.shape[0] - n_deleted, A.shape[1]))  # create new matrix, shape = A \ V
    i = 0
    for it, el in enumerate(A):  # rewrite non-deleted rows
        if not mask[it]:
            Aout[i] = el
            i = i + 1
    return Aout


def getRanking(Aa, Ab, uVec):  # main ranking algorithm
    P = np.zeros((Aa.shape[0] * Ab.shape[0], 1))  # create "volume" vector
    it = 0
    for elA in Aa:
        for elB in Ab:
            P[it] = np.prod(np.abs(elB[2:] - elA[2:]))  # calculate "volume", modify indices
            it = it + 1

    sumP = P.sum()
    w = np.zeros((P.shape[0], 1))
    for it, Pit in enumerate(P):
        w[it] = Pit / sumP  # get weights from P

    result = np.zeros((uVec.shape[0], 1))
    for iter, u in enumerate(uVec):
        i = 0
        f = np.zeros((Aa.shape[0] * Ab.shape[0], 1))
        for elA in Aa:
            for elB in Ab:
                skipFlag = 0
                for id, elX in enumerate(u[2:]):  # modify indices
                    if not (elA[id + 2] <= elX <= elB[id + 2] or elB[id + 2] <= elX <= elA[id + 2]):  # modify indices
                        skipFlag = 1
                        break
                f[i] = 0
                if not skipFlag:
                    d1 = np.sqrt(sum(np.power(elA[2:] - u[2:], 2)))  # modify indices
                    d2 = np.sqrt(sum(np.power(elB[2:] - u[2:], 2)))  # modify indices
                    f[i] = w[i] * d2/(d1 + d2)

                i = i + 1
        result[iter] = f.sum()
    return result


def add_distances(shop, points):
    distance_each_other = np.zeros((points.shape[0], points.shape[0]))
    distance_base = np.zeros(points.shape[0])

    base_coords = np.argwhere(shop == 6)
    base_coords = tuple(base_coords[0])
    shop[base_coords] = 0

    for idx1 in range(points.shape[0]):
        path = a_star.astar_search(shop, tuple(points[idx1, :2]), base_coords)
        if path:
            distance_base[idx1] = len(path) - 1

        for idx2 in range(idx1, points.shape[0]):
            path = a_star.astar_search(shop, tuple(points[idx1, :2]), tuple(points[idx2, :2]))
            if path:
                distance_each_other[idx1, idx2] = len(path) - 1


    distance_each_other = distance_each_other + distance_each_other.T
    distance_base = np.resize(distance_base, (points.shape[0], 1))

    points = np.concatenate((points, distance_base), axis=1)
    return shop, points, distance_each_other, base_coords,

def get_classes(points):
    A = np.array(points).astype(float)

    A0 = naiwny_filtracja(A.copy())

    A1 = naiwny_filtracja(deleteSpecificRows(A, A0))
    A_temp = np.concatenate((A0, A1))

    A2 = naiwny_filtracja(deleteSpecificRows(A, A_temp))
    A_temp2 = np.concatenate((A_temp, A2))

    A3 = naiwny_filtracja(deleteSpecificRows(A, A_temp2))

    return A0, A1, A2, A3

def check_classes(class1, class2):
    class1 = naiwny_filtracja(class1.copy())
    class2 = naiwny_filtracja(class2.copy())

    mutualContradiction(class1, class2)

    return class1, class2

def get_best_point(class1, class2, points):
    ranking = getRanking(class1, class2, points)


    points = np.hstack(([[i + 1] for i in range(points.shape[0])], ranking, points))  # add record number column, add calculated rank
    points = points[points[:, 1].argsort()[::-1]]  # sort matrix by ci, make it descending order
    points[:, 1] = np.around(points[:, 1], decimals=3)  # round ci to make it display better
    np.set_printoptions(suppress=True)
    return points[0]

def run_rsm(shop, points, selection, points_ref, n, user_classes=None):
    _, points, ref_distances, _ = add_distances(shop, points)
    points_current = np.copy(points)
    distances_current = np.copy(ref_distances)
    points_ref_current = np.copy(points_ref)
    path = np.array([[0, 0, 0, 0, 0, 0, 0, 0]])
    if user_classes is not None:
        new_c1 = []
        new_c2 = []
        class1 = list(user_classes['class1'])
        class2 = list(user_classes['class2'])
        for i in class1:
            new_c1.append(points_current[i])
        for i in class2:
            new_c2.append(points_current[i])
        class1, class2 = check_classes(np.array(new_c1), np.array(new_c2))
    for i in range(n+1):
        if user_classes is None:
            classes = get_classes(points_current)
            class1, class2 = check_classes(classes[selection[0]], classes[selection[1]])
        best = get_best_point(class1, class2, points_current)
        best[0] = i
        best[1], best[3] = best[3], best[1]
        best[1], best[2] = best[2], best[1]
        path = np.concatenate((path, [best]), axis=0)
        points_current, distances_current, points_ref_current = a_star.change_distance(points_current, distances_current,
                                                                               best[1:3], points_ref_current)
    return path
