import numpy as np

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
                    val.append(fun[i][-j -1][0] * p[k][i] + fun[i][-j -1][1])

        rank.append(np.sum(val))
    return np.array(rank)



points = np.array([[5.1, 20, 10499],
                   [3.1, 17, 4049],
                   [4.5, 4, 4549],
                   [3.7, 9.5, 2699]])

minmax = [1, 1, 0] # 1- max, 0- min

limits = best(points, minmax) 
print(limits)

user_steps_count = [2, 2, 3] # użytkowinik wybiera na ile chce podizelić przedziałów każdy parametr

default_steps = steps(limits, user_steps_count) # przedziały z wagami wygenerowane automatycznie pokazujemy użytkownikowi
print(default_steps)

user_steps = default_steps # przedziały z wagami zmienione przez użytkownika
user_steps[0][1][1] = 0.18
user_steps[1][1][1] = 0.18
user_steps[2][1][1] = 0.28
user_steps[2][2][1] = 0.14
print(user_steps)

usability = usability_fun(user_steps, minmax)
print(usability)

print(ranking(usability, points, user_steps))








