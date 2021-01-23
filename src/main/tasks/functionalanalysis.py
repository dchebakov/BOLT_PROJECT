import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
import numpy as np
from sympy.parsing.sympy_parser import parse_expr
import re


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True


@task_decorate
def functionalanalysisEx1(request):
    ROUNDING_NUMBER = 2

    rows = request.GET.get('rows')
    columns = request.GET.get('columns')
    values = request.GET.get('values')

    if not check_args(rows, columns, values) \
            or float(rows) <= 1 \
            or float(columns) <= 1:
        return {'is_valid': False}

    rows = int(rows)
    columns = int(columns)
    values = values.split(' ')

    if len(values) != rows * columns:
        return {'is_valid': False}

    matrix = []
    for _ in range(rows):
        row = []
        for _ in range(columns):
            try:
                row.append(float(values.pop(0)))
            except ValueError:
                return {'is_valid': False}

        matrix.append(row)

    matrix_transp = list(zip(*matrix))

    matrix_np = np.matrix(matrix)
    matrix_transp_np = np.matrix(matrix_transp)

    B = matrix_transp_np * matrix_np
    eig, v = np.linalg.eig(B)
    max_eig = max(abs(x) for x in eig)
    B = B.tolist()

    eucl_norm = np.sqrt(max_eig)
    abs_matrix = np.abs(matrix_np).tolist()
    cheb_norm = round(max(sum(row) for row in abs_matrix), ROUNDING_NUMBER)

    def matrix2latex(lst):
        return r'\begin{{pmatrix}} {} \end{{pmatrix}}'.format(
            r' \\ '.join([(str.join(' & ', (str(round(el, ROUNDING_NUMBER)) for el in row))) for row in lst]))

    def chebnorm2latex(lst):
        return r'\left | {} \right |'.format(
            r'\right | , \left |'.join(
                [(str.join(' + ', (str(round(el, ROUNDING_NUMBER)) + 'x^' + str(i + 1) for i,el in enumerate(row))))
                 for row in lst]))

    return {'rows': rows, 'columns': columns, 'matrix': matrix2latex(matrix), 'cheb': chebnorm2latex(matrix),
            'cheb_norm': round(cheb_norm, ROUNDING_NUMBER), 'matrix_transp': matrix2latex(matrix_transp),
            'B': matrix2latex(B),
            'eig': str.join(', ', [str(round(x, ROUNDING_NUMBER)) for x in eig]),
            'max_eig': round(max_eig, ROUNDING_NUMBER), 'eucl_norm': round(eucl_norm, ROUNDING_NUMBER),
            'is_valid': True}
