import math


def heuristica_euclidian(outro, goal):
    return math.sqrt((outro[0]-goal[0])**2+(outro[1]-goal[1])**2)


def heuristica_manhattan(atual, goal):
    return abs(goal[0] - atual[0]) + abs(goal[1] - atual[1])


def heuristica_chebyshev(atual, goal):
    return max(abs(goal[0] - atual[0]), abs(goal[1] - atual[1]))
