import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
from sympy import diff, latex, simplify, Symbol, expand
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, function_exponentiation, \
    implicit_application
from sympy.diffgeom.rn import R2
from sympy.diffgeom import metric_to_Christoffel_1st, metric_to_Christoffel_2nd, TensorProduct
from itertools import product
import re


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True


@task_decorate
def diffgeometryEx1(request):
    xi1 = request.GET.get('xi1')
    xi2 = request.GET.get('xi2')
    eta1 = request.GET.get('eta1')
    eta2 = request.GET.get('eta2')

    if not check_args(xi1, xi2, eta1, eta2):
        return {'is_valid': False}

    xi11 = re.sub(r'\^', '**', str(xi1))
    xi22 = re.sub(r'\^', '**', str(xi2))
    eta11 = re.sub(r'\^', '**', str(eta1))
    eta22 = re.sub(r'\^', '**', str(eta2))
    x = [Symbol('x'), Symbol('y')]

    transformations = standard_transformations + (function_exponentiation, implicit_application,)
    try:
        xi = [parse_expr(xi11, transformations=transformations), parse_expr(xi22, transformations=transformations)]
        eta = [parse_expr(eta11, transformations=transformations), parse_expr(eta22, transformations=transformations)]
    except:
        return {'is_valid': False}

    phi = [0, 0]
    for i in range(2):
        for a in range(2):
            phi[i] += (xi[a] * diff(eta[i], x[a]) - eta[a] * diff(xi[i], x[a]))
        phi[i] = latex(phi[i])

    solve = {'phi1': phi[0], 'phi2': phi[1], 'xi1': xi1, 'xi2': xi2, 'eta1': eta1, 'eta2': eta2, 'is_valid': True}

    return solve


@task_decorate
def diffgeometryEx2(request):
    typesym = request.GET.get('typesym')
    metric_input = request.GET.get('metric')

    if not check_args(typesym, metric_input):
        return {'is_valid': False}

    def get_unique(lst):
        lst = set(lst)
        lst = list(lst)
        lst.sort()
        return lst

    def replace_in_metric(m, lst1, lst2):
        for i in range(len(lst1)):
            m = m.replace(lst1[i], lst2[i])
        return m

    TP = TensorProduct
    R = [R2.x, R2.y]
    dR2 = [TP(R2.dx, R2.dx), TP(R2.dy, R2.dy)]
    dR = (TP(R2.dx, R2.dy) + TP(R2.dy, R2.dx)) / 2

    metric = re.sub(r'\^', '**', str(metric_input))
    metric = re.sub(r'd\*s\*\*2=', '', metric)

    # get vars from string-metric
    variables = re.findall(r'd\*(\w+)', metric)
    variables = get_unique(variables)
    # get differentials from string-metric and replace 'd*x' to 'dx'
    zamena_diff = re.findall(r'd\*\w+', metric)
    zamena_diff = get_unique(zamena_diff)

    zamena_diff_new = [el.replace('*', '') for el in zamena_diff]

    metric = replace_in_metric(metric, zamena_diff, zamena_diff_new)
    # get differentials at the 2 power
    diffs2 = re.findall(r'd\w+\*\*2', metric)
    diffs2 = get_unique(diffs2)
    # get differentials 'dx*dy' and replace to 'dxdy'
    diffs_diff = re.findall(r'd\w+\*d\w+', metric)
    diffs_diff = get_unique(diffs_diff)

    diffs_diff_new = [el.replace('*', '') for el in diffs_diff]

    metric = replace_in_metric(metric, diffs_diff, diffs_diff_new)
    # get sympy-eval from string-metric
    transformations = standard_transformations + (function_exponentiation, implicit_application,)
    try:
        metric_sym = parse_expr(metric, transformations=transformations)
    except:
        return {'is_valid': False}

    metric_input = latex(metric_sym)
    # replace variables to 'R2.x' and "R2.y'
    metric_sym = replace_in_metric(metric_sym, variables, R)
    # replace differentials at the 2 power to 'TP(dx, dx)' and 'TP(dy, dy)'
    metric_sym = replace_in_metric(metric_sym, diffs2, dR2)
    # replace 'dxdy' to 'TP(dx, dy)'
    for el in diffs_diff_new:
        metric_sym = metric_sym.replace(el, dR)
    metric_sym = expand(metric_sym)
    #generate metric-matrix
    metric_matrix = [latex(metric_sym.coeff(TP(a, b))) for a in [R2.dx, R2.dy] for b in [R2.dx, R2.dy]]

    if typesym == '1':
        try:
            Christoffel = simplify(metric_to_Christoffel_1st(metric_sym))
        except ValueError:
            return {'is_valid': False}

    elif typesym == '2':
        try:
            Christoffel = simplify(metric_to_Christoffel_2nd(metric_sym))
        except ValueError:
            return {'is_valid': False}

    else:
        return {'is_valid': False}

    Christoffel = list(Christoffel)
    # replace 'R2.x,y' to variables
    index = list(map(''.join, product('12', repeat=3)))
    answer = [('_{%s,%s%s}=' if typesym == '1' else '^%s_{ \ %s%s}=') % (index[i][0], index[i][1], index[i][2]) +
              latex(el.subs([(R[i], variables[i]) for i in range(len(variables))], simultaneous=True))
              for i, el in enumerate(Christoffel)]

    return {'answer': answer, 'metric': metric_input, 'typesym': typesym, 'metric_matrix': metric_matrix, 'is_valid': True}
