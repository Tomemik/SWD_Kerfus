import heapq
import pandas as pd
import numpy as np
import openpyxl
import alg_topsis as top
from tabulate import tabulate


def manhattan_distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def astar_search(grid, start, goal):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Possible movement directions: right, left, down, up

    def is_valid_move(x, y):
        return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0

    def reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)
        return path

    open_set = []  # Priority queue to store nodes to be explored
    heapq.heappush(open_set, (0, start))  # Initial node with priority 0
    came_from = {}  # Dictionary to store the parent node for each node
    g_score = {start: 0}  # Dictionary to store the cost from start to each node

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if is_valid_move(neighbor[0], neighbor[1]):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    priority = tentative_g_score + manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (priority, neighbor))
                    came_from[neighbor] = current

    return None  # No path found


def change_distance(table, distances, point, points_ref):
    for idx, el in enumerate(table[:, :2]):
        if (el == point).all():
            idx_to_del = idx

    print(table[idx_to_del], tuple(point), idx_to_del)
    table[:, -1] = distances[idx_to_del]
    table = np.delete(table, idx_to_del, 0)
    distances = np.delete(distances, idx_to_del, 0)
    distances = np.delete(distances, idx_to_del, 1)
    points_ref = np.delete(points_ref, idx_to_del, 0)

    return table, distances, points_ref


def topsis_n_points(table_original, weights, search_min, points_ref, n):
    table_current = np.copy(table_original)
    distances_current = np.copy(distance_each_other)
    points_ref_current = np.copy(points_ref)
    path = np.array([[0, 0, 0, 0, 0, 0, 0]])
    for _ in range(n):
        res = top.find_best(table_current[:, 2:], weights, search_min, list(zip(table_current[:, 0], table_current[:, 1])))
        path = np.concatenate((path, [res]), axis=0)
        table_current, distances_current, points_ref_current = change_distance(table_current, distances_current, res[:2], points_ref_current)

    return path[1:]

df1 = pd.read_excel('path.xlsx', usecols='B:BE', skiprows=0, nrows=29)
arr = df1.values.T

df2 = pd.read_excel('punkty.xlsx', usecols='B:F', skiprows=0, nrows=54)
points = df2.values

points_ref = [(x, y) for x, y in points[:, :2]]

distance_each_other = np.zeros((points.shape[0], points.shape[0]))
distance_base = np.zeros(points.shape[0])


base_coords = (55, 2)

for idx1 in range(points.shape[0]):
    path = astar_search(arr, tuple(points[idx1, :2]), base_coords)
    if path:
        distance_base[idx1] = len(path) - 1

    for idx2 in range(idx1, points.shape[0]):
        path = astar_search(arr, tuple(points[idx1, :2]), tuple(points[idx2, :2]))
        if path:
            distance_each_other[idx1, idx2] = len(path) - 1


distance_each_other = distance_each_other + distance_each_other.T
distance_base = np.resize(distance_base, (54, 1))

points = np.concatenate((points, distance_base), axis=1)
#print(points)

weights = np.array([0.15, 0.2, 0.3, 0.35])

kerfus = topsis_n_points(points, weights, [1, 1, 0, 0], points_ref, 10)

kerfus_tab = [["lp", "x", "y", "ci", "popularność", "szerokość przejazdu", "przeszkadzanie", "odległość"]]

for i, el in enumerate(kerfus):
    kerfus_tab = np.append(kerfus_tab, [np.append(i+1, el)], axis=0)

print(tabulate(kerfus_tab, headers="firstrow"))
