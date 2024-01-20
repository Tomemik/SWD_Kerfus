#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from tabulate import tabulate
# Dane z pliku excel Metoda Topsis, kod zmieniony dla obliczania v- z nadir.

# Input matrix
# A = np.array([[700,  2, 6, 8],
#              [250,  2, 4, 8],
#              [1200, 6, 9, 16],
#              [880,  4, 9, 12],
#              [450,  3, 8, 12]]).astype(float)


#W = np.array([0.35, 0.3, 0.1, 0.25])  # weights for columns

#search_for_min = [0, 1, 1, 1]  # True column values will search for maximum



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

# code execution
#find_best(A, W, search_for_min)
