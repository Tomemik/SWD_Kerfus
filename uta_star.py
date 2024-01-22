import numpy as np
from general_fun import get_point_from_xlsx, path_plot, change_distance
import alg_topsis
from tabulate import tabulate


def best(a, mm):
    ideal = []
    aideal = []
    mn = np.min(a, axis=0)
    mx = np.max(a, axis=0)
    for i in range(len(mm)):
        if mm[i]:
            ideal.append(mx[i])
            aideal.append(mn[i])
        else:
            ideal.append(mn[i])
            aideal.append(mx[i])
    return np.array([ideal, aideal])


def steps(lm, st):
    row = []
    for i in range(len(st)):
        col = []
        for j in range(np.max(st)+1):
            if j <= (st[i]):
                step = lm[0][i] - ((lm[0][i]-lm[1][i])/st[i])*j
                val = 1/len(st) - ((1/len(st))/st[i])*j
            else:
                step = np.NaN
                val = np.NaN

            col.append([step, val])
        row.append(col)
    return np.array(row)


def usability_fun(us, mm):
    norm = np.sum(us[:,0,1])
    us[:,:,1] /= norm

    row = []
    for i in range(len(us)):
        col = []
        for j in range(len(us[0])-1):
            if mm[i]:
                a = (us[i][-j - 1][1] - us[i][-j - 2][1]) / (us[i][-j - 1][0] - us[i][-j - 2][0])
                b = us[i][-j - 1][1] - (a * us[i][-j - 1][0])
            else:
                a = (us[i][j][1] - us[i][j + 1][1]) / (us[i][j][0] - us[i][j + 1][0])
                b = us[i][j][1] - (a * us[i][j][0])
            col.append([a, b])
        row.append(col)
    return np.array(row)


def ranking(fun, p, us):
    rank = []
    for k in range(len(p)):
        val = []
        for i in range(len(us)):
            for j in range(len(us[0]) - 1):
                if us[i][j][0] <= p[k][i] <= us[i][j+1][0]:
                    val.append(fun[i][j][0] * p[k][i] + fun[i][j][1])
                elif us[i][j][0] >= p[k][i] >= us[i][j+1][0]:
                    val.append(fun[i][-j - 1][0] * p[k][i] + fun[i][-j -1][1])

        rank.append(np.sum(val))
    return np.array(rank)


def uta_n_points(shop_map, base_coords, points, user_steps, points_ref, distance_each_other, usability, n):
    table_current = np.copy(points)
    distances_current = np.copy(distance_each_other)
    points_ref_current = np.copy(points_ref)
    path = np.array([[0, 0, 0, 0, 0, 0, 0]])
    choices = [np.zeros((6, 7))]

    for _ in range(n):
        print(_)
        rank = np.resize(ranking(usability, table_current[:, 2:], user_steps), (len(points_ref_current), 1))
        choice = np.insert(table_current, [2], rank, axis=1)
        choice = choice[choice[:, 2].argsort()[::-1]]
        choice = choice[:5]
        res = choice[0]
        path = np.append(path, [res], axis=0)
        choices = np.append(choices,
            [np.append([["x", "y", "ci", "popularność", "szerokość przejazdu", "przeszkadzanie", "odległość"]], choice, axis=0)],
            axis=0)

        table_current, distances_current, points_ref_current = change_distance(table_current, distances_current,
                                                                               res[:2], points_ref_current)

    fig = path_plot(path[1:], shop_map, points, base_coords)

    lp = np.resize(range(1, n+1), (n, 1))
    path = np.append(lp, path[1:], axis=1)
    path = np.append([["lp", "x", "y", "ci", "popularność", "szerokość przejazdu", "przeszkadzanie", "odległość"]], path, axis=0)

    return path, choices[1:], fig