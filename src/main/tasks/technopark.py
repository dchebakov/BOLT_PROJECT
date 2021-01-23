import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
import re


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True


def isint(s):
    '''Проверка на int'''
    try:
        int(s)
        return True
    except ValueError:
        return False


@task_decorate
def technoparkEx1(request):
    def exchange_3(sum, count, monets):
        if sum < 0:
            return count
        elif sum == 0:
            return count + 1
        count += exchange_2(sum, 0, monets[1::])
        sum -= monets[0]
        return exchange_3(sum, count, monets)

    def exchange_2(sum, count, monets):
        if sum < 0:
            return count
        elif sum == 0:
            return count + 1
        if sum % monets[1] == 0:
            count += 1
        return exchange_2(sum - monets[0], count, monets)

    sum = request.GET.get('sum')
    monets_input = request.GET.get('monets')

    if not check_args(sum, monets_input):
        return {'is_valid': False}
    if not isint(sum):
        return {'is_valid': False}

    try:
        monets = [int(v) for v in filter(None, re.split("[, ]+", monets_input))]
    except ValueError:
        return {'is_valid': False}

    sum = int(sum)
    if sum > 500:
        return {'is_valid': False}

    if len(monets) == 2:
        answer = exchange_2(sum, 0, monets)
    elif len(monets) == 1:
        answer = 1
    elif len(monets) == 3:
        answer = exchange_3(sum, 0, monets)
    else:
        return {'is_valid': False}
    solve = {'answer': answer, 'sum': sum, 'monets': str.join(', ', [str(x) for x in monets]), 'is_valid': True}
    return solve


@task_decorate
def technoparkEx2(request):
    w = request.GET.get('w')
    p = request.GET.get('p')
    W = request.GET.get('W')

    if not check_args(w, p, W):
        return {'is_valid': False}

    W = int(W)

    try:
        w = [0] + [int(v) for v in filter(None, re.split("[, ]+", w))]
        p = [0] + [int(v) for v in filter(None, re.split("[, ]+", p))]
    except ValueError:
        return {'is_valid': False}

    N = len(w) - 1
    if N != (len(p) - 1):
        return {'is_valid': False}

    A = [[0 for _ in range(W + 1)] for j in range(N + 1)]

    for k in range(1, N + 1):
        for s in range(1, W + 1):
            if s >= w[k]:
                A[k][s] = max(A[k - 1][s], A[k - 1][int(s - w[k])] + p[k])
            else:
                A[k][s] = A[k - 1][s]

    ans = []

    def findAns(k, s):
        if A[k][s] == 0:
            return
        if A[k - 1][s] == A[k][s]:
            findAns(k - 1, s)
        else:
            findAns(k - 1, s - w[k])
            ans.append(k)

    findAns(N, W)

    max_weight = max_cost = 0
    for i in ans:
        max_weight += w[i]
        max_cost += p[i]

    return {'answer': str.join(', ', [str(x) for x in ans]), 'max_weight': max_weight, 'max_cost': max_cost,
            'w': str.join(', ', [str(x) for x in w if x != 0]), 'p': str.join(', ', [str(x) for x in p if x != 0]),
            'W': W, 'is_valid': True}
