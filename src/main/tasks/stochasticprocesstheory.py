import math
from bisect import bisect, bisect_left
from scipy.stats import chi2, norm, t
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
import numpy as np
from sympy import Symbol, Function, latex, integrate, diff, symbols, simplify, N
from scipy.integrate import odeint
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, function_exponentiation, \
implicit_application
import re
import json
import os

import time

ROUNDING_NUMBER = 2
ERR = 'Введенные данные не прошли проверку на стохастичность'


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True

def matrix2latex(lst):
    if type(lst[0]) == type(lst):
        return r'\begin{{pmatrix}} {} \end{{pmatrix}}'.format(
            r' \\ '.join([(str.join(' & ', (str(round(el, ROUNDING_NUMBER)) for el in row))) for row in lst]))
    else:
        return r'\begin{{pmatrix}} {} \end{{pmatrix}}^T'.format(
            ' & '.join([str(round(el, 2)) for el in lst]))


def round_list(lst):
    return list(map(lambda x: round(x, ROUNDING_NUMBER + 3), lst))


def stochastic_validity(lst):
    if type(lst[0]) == type(lst):
        for row in lst:
            if sum(row) != 1:
                return False
            for el in row:
                if not (0 <= el <= 1):
                    return False
    else:
        if sum(lst) != 1:
            return False
        for el in lst:
            if not (0 <= el <= 1):
                return False
    return True


@task_decorate
def stochasticprocesstheoryEx1(request):
    MAX_STEP = 500

    step = request.GET.get('step')
    rows = request.GET.get('rows')
    values = request.GET.get('valuesm')
    valuesv = request.GET.get('valuesv')

    if not check_args(rows, values, valuesv, step) \
            or float(rows) < 1:
        return {'is_valid': False}

    rows = int(rows)
    try:
        step = int(step)
    except ValueError:
        return {'is_valid': False}

    if not 0 <= step <= MAX_STEP:
        return {'err': 'Введите другое значение шага', 'is_valid': False}

    values = values.split(' ')
    valuesv = valuesv.split(' ')
    values.remove('')

    matrix = []
    for _ in range(rows):
        row = []
        for _ in range(rows):
            try:
                row.append(float(values.pop(0)))
            except ValueError:
                return {'is_valid': False}
        matrix.append(row)

    if not stochastic_validity(matrix):
        return {'err': ERR, 'is_valid': False}

    vector = []
    for _ in range(rows):
        try:
            vector.append(float(valuesv.pop(0)))
        except ValueError:
            return {'is_valid': False}

    if not stochastic_validity(vector):
        return {'err': ERR, 'is_valid': False}

    matrix_np = np.matrix(matrix)
    matrix_np = matrix_np.transpose()
    vector_np = np.matrix(vector)
    vector_np = vector_np.transpose()

    answers_in_steps = []
    data = [vector]
    for i in range(step):
        matrix_pow_np = np.linalg.matrix_power(matrix_np, i + 1)
        cur_answer = list(map(float, matrix_pow_np * vector_np))
        data.append(cur_answer)
        answers_in_steps.append(matrix2latex(cur_answer))

    final = np.linalg.matrix_power(matrix_np, MAX_STEP) * vector_np
    index = [i for i in range(step + 1)]
    data = [round_list(list(el)) for el in zip(*data)]

    return {'matrix': matrix2latex(matrix), 'vector': matrix2latex(vector), 'ans': answers_in_steps, 'step': step,
            'final': matrix2latex(final.tolist()), 'index': index, 'data': data, 'is_valid': True}


@task_decorate
def stochasticprocesstheoryEx2(request):
    TIME_MAX = 100  # max time value for solving ODE
    TIME_STEP = 0.2
    TIME_GRAPH = 5  # max time value for plotting

    NUMBER_OF_NODES = request.GET.get('nn')
    NUMBER_OF_EDGES = request.GET.get('ne')
    edges = request.GET.get('edg')
    values = request.GET.get('values')

    if not check_args(NUMBER_OF_NODES, NUMBER_OF_EDGES, edges, values):
        return {'is_valid': False}

    try:
        edges = [float(s) for s in edges.split()]
        NUMBER_OF_NODES = int(NUMBER_OF_NODES)
        NUMBER_OF_EDGES = int(NUMBER_OF_EDGES)
    except ValueError:
        return {'is_valid': False}

    if len(edges) / 3 != float(NUMBER_OF_EDGES):
        return {'is_valid': False}

    values = values.split(' ')

    vector = []
    for _ in range(NUMBER_OF_NODES):
        try:
            vector.append(float(values.pop(0)))
        except ValueError:
            return {'is_valid': False}

    if not stochastic_validity(vector):
        return {'err': ERR, 'is_valid': False}

    edges = [list(el) for el in zip(*[iter(edges)] * 3)]

    H = np.zeros((NUMBER_OF_NODES, NUMBER_OF_NODES))  # infinitesimal matrix
    for node in range(1, NUMBER_OF_NODES + 1):
        for edge in edges:
            if edge[0] == node:
                H[node - 1][node - 1] -= edge[2]
            if edge[1] == node:
                H[node - 1][int(edge[0] - 1)] += edge[2]

    vector_np = np.array(vector)
    t = Symbol('t')
    p = [Function('p%d' % i) for i in range(1, NUMBER_OF_NODES + 1)]  # list of pi = sympy.Function('pi')
    pt = np.matrix([el(t) for el in p]).transpose()  # pi(t)
    right = (H * pt).tolist()  # right part of ODE-system (matrix)
    eq = [latex(right[i][0]) for i in range(NUMBER_OF_NODES)]  # right part of ODE-system (strings)

    normalization = latex(sum(pt).tolist()[0][0])

    def f(p, t):
        return np.dot(H, p)

    time = np.linspace(0, TIME_MAX, TIME_MAX / TIME_STEP + 1)
    data = odeint(f, vector_np, time).tolist()
    final = data[-1]
    data = [round_list(list(el)) for el in zip(*data[:int(TIME_GRAPH / TIME_STEP + 1)])]  # data for plotting
    time = time[:int(TIME_GRAPH / TIME_STEP + 1)]  # time for plotting

    return {'H': matrix2latex(H.tolist()), 'eq': eq, 'vector': matrix2latex(vector), 'data': data,
            'time': round_list(time.tolist()), 'final': matrix2latex(final), 'edges': edges, 'nn': NUMBER_OF_NODES,
            'normalization': normalization,
            'is_valid': True}

@task_decorate
def stochasticprocesstheoryEx3(request):
    start_time = time.time()

    rows = request.GET.get('rows')
    values = request.GET.get('valuesm')
    valuesv = request.GET.get('valuesv')
    fun = request.GET.get('fun')
    print("ALL DATA GET: ", time.time() - start_time)
    start_time = time.time()

    if not check_args(rows, values, valuesv) \
            or float(rows) < 1:
        return {'is_valid': False}

    rows = int(rows)

    values = values.split(' ')
    valuesv = valuesv.split(' ')
    values.remove('')

    matrix = []
    for _ in range(rows):
        row = []
        for _ in range(rows):
            try:
                row.append(float(values.pop(0)))
            except ValueError:
                return {'is_valid': False}
        matrix.append(row)


    vector = []
    for _ in range(rows):
        try:
            vector.append(float(valuesv.pop(0)))
        except ValueError:
            return {'is_valid': False}

    DU = matrix[0].copy().pop(0)
    DV = matrix[1].copy().pop(1)
    cov = matrix[0].copy().pop(1)
    MU = vector.copy().pop(0)
    MV = vector.copy().pop(1)
    u ,v, t, t1, t2, s = symbols('u v t t1 t2 s')
    Datafun = []
    fun = parse_expr(fun)
    Datafun.append((fun))
    Dfun = diff(fun,t)
    Datafun.append((Dfun))
    Nfun = fun+Dfun
    Datafun.append((Nfun))
    Ifun = fun.subs(t,s)
    Ifun = integrate(Ifun, (s, 0, t))
    Datafun.append((Ifun))
    print("MAIN: ", time.time() - start_time)

    return {'f' : fun ,'Df' : Dfun ,'Nf' : Nfun , 'If' : Ifun,'Datafun' : Datafun, 'matrix': matrix2latex(matrix), 'vector': matrix2latex(vector),'DU' : DU,'DV' : DV,
            'cov' : cov,'MU' : MU,'MV' : MV,'is_valid': True}

'''
@task_decorate
def stochasticprocesstheoryEx4(request):
    k = request.GET.get('k')
    if not k:
        return {'is_valid': False}

    tau = symbols('tau')
    k = parse_expr(k)
    # возвращаем словарь с ответом
    return {'k': k, 'is_valid': True}'''
