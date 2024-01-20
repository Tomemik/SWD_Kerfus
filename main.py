import pandas as pd
import numpy as np
import openpyxl
import alg_topsis as top
from tabulate import tabulate
from a_star import astar_search


def get_point_from_xlsx(file):
    df1 = pd.read_excel(file, sheet_name='mapa', usecols='B:BE', skiprows=0, nrows=29)
    arr = df1.values.T

    df2 = pd.read_excel(file, sheet_name='punkty', usecols='B:F', skiprows=0, nrows=80, keep_default_na=False)
    points = df2.values

    points_ref = [(x, y) for x, y in points[:, :2]]

    distance_each_other = np.zeros((points.shape[0], points.shape[0]))
    distance_base = np.zeros(points.shape[0])

    base_coords = np.argwhere(arr == 6)
    base_coords = tuple(base_coords[0])
    arr[base_coords] = 0

    for idx1 in range(points.shape[0]):
        path = astar_search(arr, tuple(points[idx1, :2]), base_coords)
        if path:
            distance_base[idx1] = len(path) - 1

        for idx2 in range(idx1, points.shape[0]):
            path = astar_search(arr, tuple(points[idx1, :2]), tuple(points[idx2, :2]))
            if path:
                distance_each_other[idx1, idx2] = len(path) - 1

    distance_each_other = distance_each_other + distance_each_other.T
    distance_base = np.resize(distance_base, (points.shape[0], 1))

    points = np.concatenate((points, distance_base), axis=1)

    return arr, points, points_ref, distance_each_other, base_coords


#print(points)

arr, points, points_ref, distance_each_other, base_coords = get_point_from_xlsx('sklep_4.xlsx')
weights = np.array([0.25, 0.2, 0.3, 0.25])

kerfus_tab, choices, figure = top.topsis_results(points, weights, points_ref, arr, distance_each_other, base_coords)

for i, choice in enumerate(choices):
    print(f"Krok {i+1}:\n", tabulate(choice, headers="firstrow"))
print(tabulate(kerfus_tab, headers="firstrow"))
figure.show()
