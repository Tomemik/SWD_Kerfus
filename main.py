import heapq
import pandas as pd
import numpy as np
import openpyxl


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


def change_distance(table, distances, point):
    table[:, -1] = distances[point]


df1 = pd.read_excel('path.xlsx', usecols='B:BE', skiprows=0, nrows=29)
arr = df1.values.T

df2 = pd.read_excel('punkty.xlsx', usecols='B:F', skiprows=0, nrows=54)
points = df2.values

distance_each_other = np.zeros((points.shape[0], points.shape[0]))
distance_base = np.zeros(points.shape[0])

base_coords = (55, 2)


for idx1 in range(points.shape[0]):
    path = astar_search(arr, (points[idx1, 0], points[idx1, 1]), base_coords)
    if path:
        distance_base[idx1] = len(path) - 1

    for idx2 in range(idx1, points.shape[0]):
        path = astar_search(arr, (points[idx1, 0], points[idx1, 1]), (points[idx2, 0], points[idx2, 1]))
        if path:
            distance_each_other[idx1, idx2] = len(path) - 1

distance_each_other = distance_each_other + distance_each_other.T

distance_dict = {}
for idx in range(points.shape[0]):
    distance_dict[(points[idx, 0], points[idx, 1])] = distance_each_other[idx]

distance_base = np.resize(distance_base, (54, 1))

points = np.concatenate((points, distance_base), axis=1)
print(points)

change_distance(points, distance_dict, (7, 7))
print(points)

