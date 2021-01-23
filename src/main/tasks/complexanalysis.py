import math
from django.shortcuts import render
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import re
from .probabilitytheory import task_decorate


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg:
            return False
    return True
