import math
from bisect import bisect, bisect_left
from scipy.stats import chi2, norm, t
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re
import json


def pirson_answer(w, wkr, nadezhnost):
    if w < wkr:
        return "Наблюдаемое значение статистики Пирсона меньше критического значения, гипотеза принимается с надежностью \(" + str(
            nadezhnost) + "\)."
    else:
        return "Наблюдаемое значение статистики Пирсона больше критического значения, гипотеза отклоняется с надежностью \(" + str(
            nadezhnost) + "\)."


def rnd(number):
    return round(number, 2)


@task_decorate
def mathstatisticsEx1(request):
    numbers_input = request.GET.get('numbers')
    nadezhnost = request.GET.get('1-alpha')
    NUMBER_OF_INTERVALS = request.GET.get('razb')

    if not numbers_input or not nadezhnost:
        return {'is_valid': False}

    nadezhnost = re.sub(',', '.', str(nadezhnost))

    try:
        numbers = [float(v) for v in filter(None, re.split("[, ]+", numbers_input))]
        nadezhnost = float(nadezhnost)
    except ValueError:
        return {'is_valid': False}

    if nadezhnost >= 1 or nadezhnost < 0 or len(numbers) < 2:
        return {'is_valid': False}

    alpha = 1 - nadezhnost

    # data for the numbers-chart
    index = [i for i in range(1, len(numbers) + 1)]
    # data for the numbers-sort-chart
    numbers_sort = numbers.copy()
    numbers_sort.sort()
    NUMBER_OF_VALUES = len(numbers_sort)
    # data for the efr-chart
    unique_numbers = set(numbers_sort)
    unique_numbers = list(unique_numbers)
    unique_numbers.sort()
    NUMBER_OF_UNIQUE_VALUES = len(unique_numbers)

    if not NUMBER_OF_INTERVALS or int(NUMBER_OF_INTERVALS) <= 0 or int(NUMBER_OF_INTERVALS) > 100:
        if NUMBER_OF_UNIQUE_VALUES > 10:
            NUMBER_OF_INTERVALS = 10
        else:
            NUMBER_OF_INTERVALS = NUMBER_OF_UNIQUE_VALUES - 1

    NUMBER_OF_INTERVALS = int(NUMBER_OF_INTERVALS)
    if NUMBER_OF_INTERVALS == 0:
        NUMBER_OF_INTERVALS = 1

    max = unique_numbers[NUMBER_OF_UNIQUE_VALUES - 1]
    min = unique_numbers[0]

    step = (max - min) / NUMBER_OF_INTERVALS
    if step == 0:
        step = 1
    grid = [rnd(min + i * step) for i in range(NUMBER_OF_INTERVALS + 1)]

    efr = [0]
    for point_on_grid in grid:
        efr.append(rnd(bisect_left(numbers_sort, point_on_grid) / NUMBER_OF_VALUES))
    efr.extend([1, 1])

    index_efr = [min - 0.5]
    index_efr.extend(grid)
    index_efr.append(max + 0.5)
    index_efr.append(max + 1.0)

    # data for the polygon-chart
    count_on_interval = bisect(numbers_sort, grid[1])
    count_on_intervals = [count_on_interval]
    epr = [rnd(count_on_interval / NUMBER_OF_VALUES / step)]
    for i in range(1, len(grid) - 1):
        count_on_interval = bisect(numbers_sort, grid[i + 1]) - bisect(numbers_sort, grid[i])
        count_on_intervals.append(count_on_interval)
        epr.append(rnd(count_on_interval / NUMBER_OF_VALUES / step))

    index_polygon = [rnd((grid[i] + grid[i + 1]) / 2) for i in range(len(grid) - 1)]

    # Eval-distribution
    L_RAVN = 2
    ravn_a = (NUMBER_OF_VALUES * min - max) / (NUMBER_OF_VALUES - 1)
    ravn_b = (NUMBER_OF_VALUES * max - min) / (NUMBER_OF_VALUES - 1)
    ravn_levo_a = min - (max - min) * (1 - alpha ** (1 / NUMBER_OF_VALUES))
    ravn_pravo_b = max + (max - min) * (1 - alpha ** (1 / NUMBER_OF_VALUES))

    if ravn_a == ravn_b:
        return {'is_valid': False}

    if (ravn_a - ravn_levo_a) > (min - ravn_a):
        ravn_apm = ravn_a - ravn_levo_a
    else:
        ravn_apm = min - ravn_a

    if (ravn_b - max) > (ravn_pravo_b - ravn_b):
        ravn_bpm = ravn_b - max
    else:
        ravn_bpm = ravn_pravo_b - ravn_b

    ravn_p = [(grid[i + 1] - grid[i]) / (ravn_b - ravn_a) for i in range(NUMBER_OF_INTERVALS)]

    ravn_w = 0
    for i in range(NUMBER_OF_INTERVALS):
        ravn_w += (count_on_intervals[i]) ** 2 / NUMBER_OF_VALUES / ravn_p[i]
    ravn_w -= NUMBER_OF_VALUES
    ravn_w = abs(ravn_w)
    ravn_wkr = chi2.ppf(nadezhnost, NUMBER_OF_INTERVALS - 1 - L_RAVN)
    ravn_answer = pirson_answer(ravn_w, ravn_wkr, nadezhnost)

    # Exp-distribution
    L_POKAZ = 1
    pokaz_x = 0
    for i in range(NUMBER_OF_INTERVALS):
        pokaz_x += count_on_intervals[i] * index_polygon[i]
    pokaz_x = pokaz_x / NUMBER_OF_VALUES
    pokaz_lambda = 1 / pokaz_x

    pokaz_levo_lambda = float(pokaz_lambda * (1 - norm.ppf(1 - alpha / 2) / sqrt(NUMBER_OF_VALUES)))
    pokaz_pravo_lambda = float(pokaz_lambda * (1 + norm.ppf(1 - alpha / 2) / sqrt(NUMBER_OF_VALUES)))

    if (pokaz_lambda - pokaz_levo_lambda) > (pokaz_pravo_lambda - pokaz_lambda):
        pokaz_lambdapm = pokaz_lambda - pokaz_levo_lambda
    else:
        pokaz_lambdapm = pokaz_pravo_lambda - pokaz_lambda

    pokaz_p = [math.exp(-pokaz_lambda * grid[i]) - math.exp(-pokaz_lambda * grid[i + 1]) for i in
               range(NUMBER_OF_INTERVALS)]

    pokaz_w = 0
    for i in range(NUMBER_OF_INTERVALS):
        pokaz_w += (count_on_intervals[i]) ** 2 / NUMBER_OF_VALUES / pokaz_p[i]
    pokaz_w -= NUMBER_OF_VALUES
    pokaz_w = abs(pokaz_w)
    pokaz_wkr = chi2.ppf(nadezhnost, NUMBER_OF_INTERVALS - 1 - L_POKAZ)
    pokaz_answer = pirson_answer(pokaz_w, pokaz_wkr, nadezhnost)

    # Norm-distribution
    L_NORM = 2
    norm_a = 0
    for i in range(NUMBER_OF_INTERVALS):
        norm_a += count_on_intervals[i] * index_polygon[i]
    norm_a = norm_a / NUMBER_OF_VALUES

    norm_sigmakv = 0
    for i in range(NUMBER_OF_INTERVALS):
        norm_sigmakv += ((index_polygon[i] - norm_a) ** 2) * count_on_intervals[i]
    norm_sigmakv = norm_sigmakv / (NUMBER_OF_VALUES - 1)
    norm_sigma = math.sqrt(norm_sigmakv)

    norm_levo_a = float(
        norm_a - math.sqrt(norm_sigmakv) / sqrt(NUMBER_OF_VALUES) * t.ppf(1 - alpha / 2, NUMBER_OF_VALUES - 1))
    norm_pravo_a = float(
        norm_a + math.sqrt(norm_sigmakv) / sqrt(NUMBER_OF_VALUES) * t.ppf(1 - alpha / 2, NUMBER_OF_VALUES - 1))
    norm_levo_sigmakv = float((NUMBER_OF_VALUES - 1) * norm_sigmakv / chi2.ppf(1 - alpha / 2, NUMBER_OF_VALUES - 1))
    norm_pravo_sigmakv = float((NUMBER_OF_VALUES - 1) * norm_sigmakv / chi2.ppf(alpha / 2, NUMBER_OF_VALUES - 1))
    norm_levo_sigma = math.sqrt(norm_levo_sigmakv)
    norm_pravo_sigma = math.sqrt(norm_pravo_sigmakv)

    if (norm_a - norm_levo_a) > (norm_pravo_a - norm_a):
        norm_apm = norm_a - norm_levo_a
    else:
        norm_apm = norm_pravo_a - norm_a

    if (norm_sigma - norm_levo_sigma) > (norm_pravo_sigma - norm_sigma):
        norm_sigmapm = norm_sigma - norm_levo_sigma
    else:
        norm_sigmapm = norm_pravo_sigma - norm_sigma

    norm_zi = [(grid[i] - norm_a) / math.sqrt(norm_sigmakv) for i in range(1, NUMBER_OF_INTERVALS)]
    norm_Fzi = [norm.cdf(zi) - 0.5 for zi in norm_zi]
    norm_Fzi.append(0.5)
    norm_Fzi.reverse()
    norm_Fzi.append(-0.5)
    norm_Fzi.reverse()

    norm_p = [norm_Fzi[i + 1] - norm_Fzi[i] for i in range(NUMBER_OF_INTERVALS)]

    norm_w = 0
    for i in range(NUMBER_OF_INTERVALS):
        norm_w += (count_on_intervals[i]) ** 2 / NUMBER_OF_VALUES / norm_p[i]
    norm_w -= NUMBER_OF_VALUES
    norm_w = abs(norm_w)
    norm_wkr = chi2.ppf(nadezhnost, NUMBER_OF_INTERVALS - 1 - L_NORM)
    norm_answer = pirson_answer(norm_w, norm_wkr, nadezhnost)

    return {'numbers': numbers, 'index': index, 'numbers_sort': numbers_sort, 'efr': efr, 'index_efr': index_efr,
            'epr': epr, 'index_polygon': index_polygon, 'grid': grid, 'unique_numbers': unique_numbers,
            'count_on_intervals': count_on_intervals, 'step': rnd(step), 'numberOfValues': NUMBER_OF_VALUES,
            'numberOfIntervals': NUMBER_OF_INTERVALS, 'min': min, 'max': max, 'nadezhnost': nadezhnost,
            'l_ravn': L_RAVN, 'l_pokaz': L_POKAZ, 'l_norm': L_NORM,

            'ravn_a': rnd(ravn_a), 'ravn_b': rnd(ravn_b), 'ravn_levo_a': rnd(ravn_levo_a),
            'ravn_pravo_b': rnd(ravn_pravo_b),
            'ravn_p': ravn_p, 'ravn_w': rnd(ravn_w), 'ravn_wkr': rnd(ravn_wkr), 'ravn_answer': ravn_answer,
            'ravn_apm': rnd(ravn_apm), 'ravn_bpm': rnd(ravn_bpm),

            'pokaz_x': rnd(pokaz_x), 'pokaz_lambda': rnd(pokaz_lambda), 'pokaz_p': pokaz_p,
            'pokaz_w': rnd(pokaz_w), 'pokaz_wkr': rnd(pokaz_wkr),
            'pokaz_answer': pokaz_answer, 'pokaz_levo_lambda': rnd(pokaz_levo_lambda),
            'pokaz_pravo_lambda': rnd(pokaz_pravo_lambda), 'pokaz_lambdapm': rnd(pokaz_lambdapm),

            'norm_a': rnd(norm_a), 'norm_sigmakv': rnd(norm_sigmakv), 'norm_levo_a': rnd(norm_levo_a),
            'norm_pravo_a': rnd(norm_pravo_a), 'norm_levo_sigmakv': rnd(norm_levo_sigmakv),
            'norm_pravo_sigmakv': rnd(norm_pravo_sigmakv),
            'norm_zi': norm_zi, 'norm_Fzi': norm_Fzi, 'norm_p': norm_p, 'norm_w': rnd(norm_w),
            'norm_wkr': rnd(norm_wkr), 'norm_answer': norm_answer, 'norm_sigma': rnd(norm_sigma),
            'norm_levo_sigma': rnd(norm_levo_sigma), 'norm_pravo_sigma': rnd(norm_pravo_sigma),
            'norm_sigmapm': rnd(norm_sigmapm), 'norm_apm': rnd(norm_apm),

            'is_valid': True}
