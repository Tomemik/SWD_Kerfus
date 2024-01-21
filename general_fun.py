import pandas as pd
import numpy as np
from a_star import astar_search
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


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


def path_plot(ranking, shop_map, points, base_coords):
    base = np.zeros(ranking.shape[1])
    base[:2] = base_coords
    ranking = np.append([base], ranking, axis=0)

    shelves = np.argwhere(shop_map == 1)
    entrance = np.argwhere(shop_map == 2)
    exit = np.argwhere(shop_map == 3)
    bread = np.argwhere(shop_map == 4)
    meat = np.argwhere(shop_map == 5)

    fig, ax = plt.subplots()

    ax.scatter(points[:, 0], points[:, 1], c='red', s=5)
    for ix in range(ranking.shape[0] - 1):
        path = astar_search(shop_map, tuple(map(int, ranking[ix, :2])), tuple(map(int, ranking[ix + 1, :2])))
        path = np.array(path)
        plt.plot(path[:, 0], path[:, 1], '--', c='#1f77b4')
    ax.scatter(ranking[:, 0], ranking[:, 1])
    ax.scatter(shelves[:, 0], shelves[:, 1], c='lightblue', marker='s', s=26)
    ax.scatter(entrance[:, 0], entrance[:, 1], c='green', marker='s', s=26)
    ax.scatter(exit[:, 0], exit[:, 1], c='red', marker='s', s=26)
    ax.scatter(bread[:, 0], bread[:, 1], c='grey', marker='s', s=26)
    ax.scatter(meat[:, 0], meat[:, 1], c='orange', marker='s', s=26)

    for i in range(ranking.shape[0]):
        plt.annotate(i, tuple(ranking[i, :2]))

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

    return fig
