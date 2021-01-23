from scipy.interpolate import lagrange
from scipy.integrate import cumtrapz, simps
import numpy as np
from sympy import *


from .probabilitytheory import task_decorate, check_args


def cheb_grid(a, b, k):
    """Чебышевская сетка на [a; b]"""
    return [1 / 2 * (a + b) + 1 / 2 * (b - a) * np.cos((2 * i - 1) * np.pi / 2 / k) for i in range(1, k + 1)]


@task_decorate
def numericalanalysisEx6(request):
    """Для заданной на отрезке гладкой функции (см. Таблицу 1, n - номер группы) и равномерной сетки Ak, где k = 20,
    используя квадратурные формулы прямоугольников, трапеций и парабол, приближённо вычислить интеграл на отрезке [0; 2]
    Прокомментировать приближённые результаты, сравнивая их с аналитически вычисленным значением интеграла. Кроме того,
    приближённо вычислить интеграл L(x) - интерполяционный полином Лагранжа для сеточной функции B10 - чебышёвская сетка
    на отрезке [0; 2].►"""
    a = request.GET.get('a')
    b = request.GET.get('b')
    n = request.GET.get('n')
    c = request.GET.get('c')

    if not check_args(a, b, c, n):
        return {'is_valid': False}
    a, b, c, n = int(a), int(b), int(c), int(n)
    x = Symbol("x")

    """отрезок [start; end]"""
    start = 0
    end = 2

    k = 20  # число разбиений (табуляция)

    expr = ((a + 52 - n) * x ** 4 + (b - 52 + n) * x ** 2 + c) / ((x + 1) * (x ** 2 + 1))  # выражение sympy
    f = lambdify(x, expr)  # выражение для численных расчетов
    expr_str = latex(expr)
    fracs = latex(apart(expr, x))
    """Квадратурная формула прямоугольников"""
    def recktangular(f, grid):
        stp = grid[1] - grid[0]
        integral = [f(grid[i]) * stp for i in range(0, len(grid))]
        return sum(integral)

    tau = np.linspace(start, end, num=k + 1)  # равномерная сетка
    theta = np.linspace(start + (end - start) / 2 / k, end - (end - start) / 2 / k, num=k)  # центральная сетка
    y = f(tau)  # значения функции на сетке tau

    chebx = np.array(cheb_grid(start, end, 11))
    cheby = f(chebx)
    poly = lagrange(chebx, cheby)  # полином Лагранжа для функции f на чебышевской сетке (k = 10)

    trap_f = cumtrapz(y, tau, initial=0)[-1]
    simp_f = simps(y, tau)
    rect_f = recktangular(f, theta)

    trap_l = cumtrapz(poly(tau), tau, initial=0)[-1]
    simp_l = simps(poly(tau), tau)
    rect_l = recktangular(poly, theta)
    expr_int = integrate(expr, (x, start, end))  # символьный результат интегрирования
    expr_int_str = printing.latex(expr_int)  # символьный результат интегрирования latex
    expr_res = expr_int.evalf()

    solve = {
        "trap_f": round(trap_f, 5), "simp_f": round(simp_f, 5), "rect_f": round(rect_f, 5),
        "trap_l": round(trap_l, 5), "simp_l": round(simp_l, 5), "rect_l": round(rect_l, 5),
        "fracs": fracs, "expr_int": expr_int_str, "res": round(expr_res, 5),
        'expr': expr_str, 'is_valid': True
    }
    return solve
