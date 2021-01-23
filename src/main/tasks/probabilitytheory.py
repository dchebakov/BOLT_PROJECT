from django.shortcuts import render
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm
from scipy.stats import norm, uniform, binom, poisson, gamma as gmm
import numpy as np
from sympy import *
import re


def comments(request, task):
    is_like = True
    if request.user.is_authenticated:
        is_like = Thanks.objects.filter(task=task,
                                        user=UserProfile.objects.get(user=request.user)).exists()

    return dict({'comments': Comment.objects.filter(task=task),
                 'comment_form': CommentForm(), 'is_like': is_like},
                **views.get_default_data(request))


def task_decorate(function):
    def wrapper(request):
        task = Task.objects.get(function_name=function.__name__)
        solve = function(request)
        return render(request, 'task.html',
                      dict({'template': 'solutions/' + task.section.slug + '/' +
                                        function.__name__ + '.html',
                            'task': task, 'solve': solve},
                           **comments(request, task)))

    return wrapper


def check_args(*args):
    '''Общая проверка'''
    for arg in args:
        if not arg or not isint(arg):
            return False
    return True


def isint(s):
    '''Проверка на int'''
    try:
        int(s)
        return True
    except ValueError:
        return False


def permutations(n, k=None):
    """return the number of such k-permutations of n without repetition, P(n,k)"""
    if k is None:
        k = n
    if 0 <= k <= n:
        return math.factorial(n) // math.factorial(n - k)
    else:
        return 0


def combinations(n, k):
    """return the number of k-combinations of an n-set, C(n,k)"""
    if 0 <= k <= n:
        return permutations(n, k) // permutations(k, k)
    else:
        return 0


def multiplication(*args):
    res = 1
    for arg in args:
        res *= arg
    return res


def bernoulli(gen, k_gen, n, k):
    p = k_gen / gen
    q = 1 - p
    return combinations(n, k) * p ** k * q ** (n - k)


def from_exp_to_tex_number(number):
    if round(number, 4) == 0:
        parts_of_number = str(number).split("e-")
        return "{0} \cdot 10^{{{1}}}".format(
            round(float(parts_of_number[0]) / 10, 2), 1 - int(parts_of_number[1])
        )
    else:
        return round(number, 5)


@task_decorate
def probabilitytheoryEx1(request):
    def calc_prob(x):
        return round(x / 36, 3)

    N = request.GET.get('N')
    if not check_args(N):
        return {'is_valid': False}

    N = int(N)
    a, b, c = 0, 0, 0
    for i in range(1, 7):
        for j in range(1, 7):
            if i + j <= N:
                a += 1
            if i * j <= N:
                b += 1
            if N != 0 and (i * j) % N == 0:
                c += 1
    solve = {'N': N, 'a': a, 'ans_a': calc_prob(a), 'b': b, 'ans_b': calc_prob(b), 'c': c,
             'ans_c': calc_prob(c), 'is_valid': True}

    return solve


@task_decorate
def probabilitytheoryEx2(request):

    n1 = request.GET.get('n1')
    n2 = request.GET.get('n2')
    n3 = request.GET.get('n3')
    n4 = request.GET.get('n4')
    m1 = request.GET.get('m1')
    m2 = request.GET.get('m2')
    m3 = request.GET.get('m3')
    m4 = request.GET.get('m4')

    if not check_args(n1, n2, n3, n4, m1, m2, m3, m4):
        return {'is_valid': False}

    n = int(n1), int(n2), int(n3), int(n4)
    m = int(m1), int(m2), int(m3), int(m4)

    if sum(m) > sum(n):
        return {'is_valid': False}

    """Без возвращения"""
    N = combinations(sum(n), sum(m))
    M = multiplication(*(combinations(x, y) for x, y in zip(n, m)))
    P_without = M / N

    """С возвращением"""
    p = [i / sum(n) for i in n]
    p_mult = multiplication(*[p[i] ** j for i, j in enumerate(m)])
    k = multiplication(*(permutations(mi) for mi in m))
    P_with = permutations(sum(m)) / k * p_mult

    solve = {
        'n1': n1, 'n2': n2, 'n3': n3, 'n4': n4,
        'm1': m1, 'm2': m2, 'm3': m3, 'm4': m4,
        'N': N, 'M': M, 'P_without': round(P_without, 3),
        'n': sum(n), 'm': sum(m), 'p1': round(p[0], 3),
        'p2': round(p[1], 3), 'p3': round(p[2], 3), 'p4': round(p[3], 3),
        'P_with': round(P_with, 3), 'is_valid': True,
    }
    return solve


@task_decorate
def probabilitytheoryEx3(request):

    n = request.GET.get('n')
    l = request.GET.get('l')
    m = request.GET.get('m')
    k = request.GET.get('k')

    if not check_args(n, l, m, k):
        return {'is_valid': False}

    n = int(n)
    l = int(l)
    m = int(m)
    k = int(k)

    if m > n:
        return {'is_valid': False}

    """БЕЗ ВОЗВРАЩЕНИЙ"""
    """Число способов выбрать m билетов из n"""
    N = combinations(n, m)
    """число способов выбрать l выигрышных билета (из k
    выигрышных) и еще m-l невыигрышных (из n-k)"""
    M = combinations(k, l) * combinations(n - k, m - l)
    P_without = M / N

    """С ВОЗВРАТОМ"""
    """по формуле Берпнулли:"""
    P_with = bernoulli(n, k, m, l)

    solve = {
        'n': n, 'l': l, 'm': m, 'k': k,
        'm_minus_l': m - l, 'n_minus_k': n - k,
        'N': N, 'M': M, 'P_without': round(P_without, 3),
        'P_with': round(P_with, 3), 'is_valid': True,
    }

    return solve


@task_decorate
def probabilitytheoryEx4(request):
    N = request.GET.get('N')
    K = request.GET.get('K')
    if not check_args(N, K):
        return {'is_valid': False}

    N = int(N)
    K = int(K)

    if N <= 0 or K <= 0 or N >= K:
        return {'is_valid': False}

    P = (K - 1) ** N
    A = math.factorial(K - 1) / math.factorial(K - 1 - N)

    solve = {'K': K, 'N': N, 'P': P, 'A': A, 'ans_a': round(A / P, 3), 'ans_b': round(1 - A / P, 3), 'is_valid': True}

    return solve


@task_decorate
def probabilitytheoryEx5(request):

    k = request.GET.get('k')
    if not check_args(k):
        return {'is_valid': False}
    k = int(k)

    if k <= 2:
        return {'is_valid': False}

    solve = {
        'k': k, 'P': round((k - 2) / k, 3),
        'k_minus_1': k - 1, 'is_valid': True,
    }

    return solve


@task_decorate
def probabilitytheoryEx6(request):

    T1 = request.GET.get('T1')
    T2 = request.GET.get('T2')
    t = request.GET.get('t')

    if not check_args(T1, T2, t):
        return {'is_valid': False}

    T1, T2, t = int(T1), int(T2), int(t)



    if T2 <= T1 or T2 < 0 or T1 < 0 or t <= 0:
        return {'is_valid': False}

    T = T2 - T1  # сторона квадрата

    if t > T:
        return {'is_valid': False}

    S = T ** 2  # площадь квадрата
    S1 = 1 / 2 * (T - 10) ** 2  # площадь верхнего треугольника
    S2 = 1 / 2 * (T - t) ** 2  # площадь нижнего треугольника

    P = 1 - (S1 + S2) / S
    _P = 1 - P

    solve = {
        'T1': T1, 'T2': T2, 'T': T,
        't': t, 'P': round(P, 3),
        'not_P': round(_P, 3), 'is_valid': True,
    }

    return solve


@task_decorate
def probabilitytheoryEx7(request):

    S1 = request.GET.get('S1')
    S2 = request.GET.get('S2')
    R = request.GET.get('R')

    try:
        S1, S2, R = float(S1), float(S2), float(R)
    except ValueError:
        return {'is_valid': False}
    except TypeError:
        return {'is_valid': False}

    if S1 < 0 or S2 < 0 or R <= 0:
        return {'is_valid': False}

    if S2 + S1 > math.pi * R ** 2:
        return {'is_valid': False}

    P = (S1 + S2) / (math.pi * R ** 2)

    solve = {
        'S1': S1, 'S2': S2, 'R': R ** 2,
        'P': round(P, 3), 'is_valid': True,
    }

    return solve


@task_decorate
def probabilitytheoryEx8(request):
    k1 = request.GET.get('k1')
    k2 = request.GET.get('k2')
    if not check_args(k1, k2):
        return {'is_valid': False}

    k1 = int(k1)
    k2 = int(k2)

    if k1 < 0 or k2 < 0 or k1 > 100 or k2 > 100:
        return {'is_valid': False}

    P1 = round(k1 / 100, 3)
    P2 = round(k2 / 100, 3)

    P = round(P1 * P2, 3)
    Pa = round(1 - P, 3)
    Pb = round((1 - P1) * (1 - P2), 3)
    Pc = round(P1 * (1 - P2) + P2 * (1 - P1), 3)

    solve = {'k1': k1, 'k2': k2, 'P1': P1, 'P2': P2, 'P': P, 'Pa': Pa, 'Pb': Pb, 'Pc': Pc, 'is_valid': True}

    return solve


@task_decorate
def probabilitytheoryEx9(request):

    p1 = request.GET.get('p1')
    p2 = request.GET.get('p2')
    n1 = request.GET.get('n1')
    n2 = request.GET.get('n2')

    if not check_args(n1, n2):
        return {'is_valid': False}

    p1, p2, n1, n2 = float(p1), float(p2), int(n1), int(n2)

    if not 0 <= p1 <= 1 or not 0 <= p2 <= 1:
        return {'is_valid': False}

    if n1 <= 0 or n2 <= 0:
        return {'is_valid': False}

    """Сначала найдем вероятности промаха для каждого стрелка:"""
    q1 = 1 - p1
    q2 = 1 - p2

    """Чтобы цель не была поражена, первый стрелок должен промахнуться все n1 раз
    (вероятность q1^n1), второй стрелок должен промахнуться n2 раза (вероятность
    q2^n2), так как выстрелы стрелков независимы, искомая вероятность, что цель
    не будет поражена, равна:"""
    P = q1 ** n1 * q2 ** n2

    solve = {
        "p1": p1, "p2": p2, "n1": n1, "n2": n2,
        "q1": round(q1, 3), "q2": round(q2, 3),
        "P": round(P, 3), 'is_valid': True,
    }

    return solve


@task_decorate
def probabilitytheoryEx10(request):
    k = request.GET.get('k')

    if not check_args(k):
        return {'is_valid': False}

    k = int(k)

    if k <= 0:
        return {'is_valid': False}

    """Вероятность выпадения герба и решки одинаковы, p = q = 0,5"""
    p = 0.5

    """вероятность того, что А выиграет до k броска равна сумме вероятностей того,
    что А выиграет на 1 броске, на 2 броске, …, на k-1 броске"""
    P_A1 = 0
    for i in range(1, k):
        P_A1 += p ** (2 * i - 1)

    """вероятность того, что А выиграет не позднее k броска равна сумме
    вероятности того, что А выиграет до k броска и что А выиграет на k броске"""
    P_A2 = P_A1 + p ** (2 * k - 1)

    """вероятность того, что B выиграет до k броска равна сумме
    вероятности того, что B выиграет до k броска"""
    P_B1 = 0
    for i in range(1, k):
        P_B1 += p ** (2 * i)

    """вероятность того, что B выиграет не позднее k броска равна сумме
    вероятности того, что B выиграет до k броска и что B выиграет на k броске"""
    P_B2 = P_B1 + p ** (2 * k)

    """Чтобы найти вероятность выигрыша игрока А при сколь угодно долгой игре,
    нужно положить k → ∞. По формуле суммы бесконечно убывающей геометрической
    прогрессии получаем:"""
    P_A3 = 1 / 2 * 1 / (1 - 1 / 4)
    """и для игрока B:"""
    P_B3 = 1 - P_A3

    solve = {
        'P_A1': round(P_A1, 3), 'P_B1': round(P_B1, 3),
        'P_A2': round(P_A2, 3), 'P_B2': round(P_B2, 3),
        'P_A3': round(P_A3, 3), 'P_B3': round(P_B3, 3),
        'k': k, 'k_1': k - 1, 'dk_2': 2 * k - 2, 'dk_3': 2 * k - 3,
        'dk_1': 2 * k - 1, 'dk': 2 * k, 'is_valid': True,
    }

    return solve


@task_decorate
def probabilitytheoryEx11(request):
    m = request.GET.get('m')

    if not check_args(m):
        return {'is_valid': False}

    m = int(m)

    if m <= 0:
        return {'is_valid': False}

    """число различных последовательностей извлечения шаров."""
    N = permutations(m)
    """только одна последовательность соответствует извлечению в порядке 1, 2, ...,"""
    P_A = 1 / N

    """число различных последовательностей извлечения шаров, имеющих хотя бы одну неподвижную
    точку (то есть имеющих хотя бы одно совпадение номера шара и номера извлечения)."""
    M_B = sum([
        (-1) ** (i + 1) * combinations(m, i) * permutations(m - i)
        for i in range(1, m + 1)
    ])
    P_B = M_B / N

    """Событие C противоположно событию B , поэтому вероятность"""
    P_C = 1 - P_B

    solve ={
        "m": m, "M_B": M_B, "P_A": from_exp_to_tex_number(P_A),
        "P_B": round(P_B, 3), "P_C": round(P_C, 3), 'is_valid': True
    }

    return solve


@task_decorate
def probabilitytheoryEx12(request):
    n1 = request.GET.get('n1')
    n2 = request.GET.get('n2')

    if not check_args(n1, n2):
        return {'is_valid': False}

    n1, n2 = int(n1), int(n2)

    if (n1 < 0) or (n2 < 0) or not (0 <= n1 + n2 <= 1000):
        return {'is_valid': False}

    p1, p2, p3 = n1 / 1000, n2 / 1000, (1000 - n1 - n2) / 1000
    p = p1 * 0.06 + p2 * 0.05 + p3 * 0.04

    solve = {
        "p": round(p, 4), "p1": p1, "p2": p2,
        "p3": p3, "n1": n1, "n2": n2,
        "n3": 1000 - n1 - n2, "is_valid": True,
    }

    return solve


@task_decorate
def probabilitytheoryEx13(request):
    N1 = request.GET.get('N1')
    M1 = request.GET.get('M1')
    N2 = request.GET.get('N2')
    M2 = request.GET.get('M2')
    K = request.GET.get('K')

    if not check_args(N1, N2, M1, M2, K):
        return {'is_valid': False}

    N1, N2, M1, M2, K = int(N1), int(N2), int(M1), int(M2), int(K)

    if N1 < 0 or N2 < 0 or M1 < 0 or M2 < 0 or K < 0 or N1 + M1 < K:
        return {'is_valid': False}

    H = [(K - i, i) for i in range(K + 1)]
    P = [round(combinations(N1, H[i][0]) * combinations(M1, H[i][1]) /
         combinations(N1 + M1, K), 3) for i in range(K + 1)]
    H1 = [(N2 + d[0], M2 + d[1]) for d in H]
    P_H = [round(d[0] / sum(d), 3) for d in H1]

    res = sum([P[i] * P_H[i] for i in range(K + 1)])
    solve = {
        "is_valid": True, "P": round(res, 3),
        "Hi": H, "H1i": H1, "Pi": P,
        "PHi": P_H, "N1M1": N1 + M1,
        "N1": N1, "M1": M1, "K": K, "sum": zip(P_H, P)
    }

    return solve


@task_decorate
def probabilitytheoryEx14(request):
    k = request.GET.get('k')
    l = request.GET.get('l')
    m = request.GET.get('m')
    n = request.GET.get('n')

    if not check_args(k, m, l, n):
        return {'is_valid': False}

    k, m, l, n = int(k), int(m), int(l), int(n)

    if k < 0 or m < 0 or l < 0 or n < 0 or k + l < m or k + l < n:
        return {'is_valid': False}

    H = [(m - i, i) for i in range(m + 1)]
    P = [round(combinations(k, H[i][0]) * combinations(l, H[i][1]) /
         combinations(k + l, m), 3) for i in range(m + 1)]
    H1 = [(k - d[0], l + d[0]) for d in H]
    P_H = [round(combinations(d[0], n) / combinations(k + l, n), 3) for d in H1]

    res = sum([P[i] * P_H[i] for i in range(m + 1)])
    solve = {
        "is_valid": True, "P": round(res, 3),
        "Hi": H, "H1i": H1, "Pi": P,
        "PHi": P_H, "kl": k + l, "n": n,
        "k": k, "l": l, "m": m, "sum": zip(P_H, P)
    }

    return solve


@task_decorate
def probabilitytheoryEx15(request):
    m1 = request.GET.get('m1')
    m2 = request.GET.get('m2')
    m3 = request.GET.get('m3')
    n1 = request.GET.get('n1')
    n2 = request.GET.get('n2')
    n3 = request.GET.get('n3')
    j = request.GET.get('j')

    if not check_args(m1, m2, m3, n1, n2, n3, j):
        return {'is_valid': False}

    m1, m2, m3, n1, n2, n3, j = int(m1), int(m2), int(m3), int(n1), int(n2), int(n3), int(j)

    if m1 + m2 + m3 != 100 or not 0 <= m1 <= 100 or not 0 <= m2 <= 100 or not 0 <= m3 <= 100:
        return {'is_valid': False}

    if not 0 <= n1 <= 100 or not 0 <= n2 <= 100 or not 0 <= n3 <= 100 or j > 3 or j < 1:
        return {'is_valid': False}

    H = [1, 2, 3]  # группа гипотез
    P = [p / 100 for p in (m1, m2, m3)]  # вероятности гипотез
    P_H = [p / 100 for p in (n1, n2, n3)]  # вероятности априорных событий
    res = sum([P[i] * P_H[i] for i in range(3)])  # полная вероятность
    P_Hj = P[j - 1] * P_H[j - 1]
    P_res = P_Hj / res  # вероятность того, что изделие выпущено j-ым заводом

    solve = {
        "is_valid": True, "P": round(res, 3), 'P_Hj': round(P_Hj, 3),
        "Hi": H, "Pi": P, "PHi": P_H, 'j': j, 'res': round(P_res, 3),
    }

    return solve


@task_decorate
def probabilitytheoryEx16(request):
    """Монета бросается до тех пор, пока герб не выпадает n раз. Определить вероятность того,
     что цифра выпадет m раз. (при n=6, m=5 --> p=0.123)"""
    n = request.GET.get('n')
    m = request.GET.get('m')

    if not check_args(n, m):
        return {'is_valid': False}

    m, n = int(m), int(n)

    if m < 0 or n <= 0:
        return {'is_valid': False}

    P = bernoulli(2, 1, n + m - 1, m) / 2  # Вероятности выпадения герба и цифры одинаковы и равны 1/2

    solve = {
        "is_valid": True, "part": n + m -1, "n_1": n - 1,
        "m": m, "last": m + n, "n": n, "P": round(P, 3),
    }
    return solve


@task_decorate
def probabilitytheoryEx17(request):
    """Вероятность выигрыша в лотерею на один билет равна p. Куплено n билетов. Найти наивероятнейшее число
    выигравших билетов и соответствующую вероятность. (при p=0.3, n=15 --> k = 4 ; 0.219)"""
    p = request.GET.get('p')
    n = request.GET.get('n')

    if not check_args(n):
        return {'is_valid': False}

    n = int(n)

    try:
        p = float(p)
    except (ValueError, TypeError):
        return {'is_valid': False}
    q = 1 - p
    if n <= 0 or not 0 < p < 1 or n * p - q < 0:
        return {'is_valid': False}

    left, right = round(n * p - q, 3), round(n * p + p, 3)
    if math.ceil(left) == math.floor(right):
        count = 1
        k = math.ceil(left)
        P = round(bernoulli(1, p, n, k), 3)
        solve = {
            'n': n, 'p': p, 'q': q, 'k': k,
            'count': count, 'P': P, 'left': left,
            'right': right, 'n_k': n - k, 'is_valid': True,
        }
    else:
        count = 2
        k = (int(left), int(right))
        P = (round(bernoulli(1, p, n, k[0]), 3), round(bernoulli(1, p, n, k[1]), 3))
        res = list(zip(k, P))
        n_k = [n - k[0], n - k[1]]
        solve = {
            'n': n, 'p': p, 'q': q, 'count': count, 'left': left,
            'right': right, 'n_k': n_k, 'res': res, 'is_valid': True,
        }

    return solve


@task_decorate
def probabilitytheoryEx18(request):
    """На каждый лотерейный билет с вероятностью p1 может выпасть крупный выигрыш, с вероятностью p2 - мелкий выигрыш
    и с вероятностью p3 билет может оказаться без выигрыша, ∑pi = 1. Куплено n билетов. Определить вероятность
    получения n1 крупных выигрышей и n2 мелких. (n=15, n1=2; n2 =2; p1=0,15; p2=0,2 --> 0.065)"""
    n1 = request.GET.get('n1')
    n2 = request.GET.get('n2')
    n = request.GET.get('n')
    p1 = request.GET.get('p1')
    p2 = request.GET.get('p2')

    if not check_args(n, n1, n2):
        return {'is_valid': False}

    n, n1, n2 = int(n), int(n1), int(n2)
    if n <= 0 or n1 < 0 or n2 < 0 or n1 + n2 > n:
        return {'is_valid': False}
    n3 = n - n1 - n2
    try:
        p1, p2 = float(p1), float(p2)
    except (ValueError, TypeError):
        return {'is_valid': False}

    if 0 <= p1 <= 1 and 0 <= p2 <= 1 and 0 <= p1 + p2 <= 1:
        p3 = 1 - p1 - p2
    else:
        return {'is_valid': False}

    P = math.factorial(n) / (math.factorial(n1) * math.factorial(n2) * math.factorial(n3)) *\
        p1 ** n1 * p2 ** n2 * p3 ** n3

    solve = {
        'is_valid': True, 'n': n, 'n1': n1, 'n2': n2, 'n3': n3,
        'p1': p1, 'p2': p2, 'p3': round(p3, 3), 'P': round(P, 3),
    }

    return solve


@task_decorate
def probabilitytheoryEx19(request):
    N = request.GET.get('N')
    M = request.GET.get('M')
    P = request.GET.get('P')

    if not check_args(N, M):
        return {'is_valid': False}
    if not P:
        return {'is_valid': False}

    P = re.sub(',', '.', str(P))
    N = int(N)
    M = int(M)
    try:
        P = float(P)
    except ValueError:
        return {'is_valid': False}

    if N <= 0 or M <= 0 or M >= N or P < 0 or P > 1:
        return {'is_valid': False}

    lam = N * P
    lam_m = lam ** M
    e_lam = math.exp(-lam).real
    m_fact = math.factorial(M)
    Pa = round(lam_m * e_lam / m_fact, 6)

    solve = {'Pa': Pa, 'N': N, 'M': M, 'P': P, 'lam': lam, 'is_valid': True}

    return solve


@task_decorate
def probabilitytheoryEx20(request):
    """Вероятность наступления некоторого события в каждом из n независимых испытаний равна p.
    Определить вероятность того, что число m наступлений события удовлетворяет неравенству k1 ≤ m ≤ k2.
    (n=100; p=0,7; k1 = 65; k2 = 75 --> 0.7242.)"""
    k1 = request.GET.get('k1')
    k2 = request.GET.get('k2')
    n = request.GET.get('n')
    p = request.GET.get('p')

    if not check_args(k1, k2, n):
        return {'is_valid': False}
    k1, k2, n = int(k1), int(k2), int(n)
    try:
        p = float(p)
    except (ValueError, TypeError):
        return {'is_valid': False}
    if k1 > k2 or not 0 <= k1 <= n or not 0 <= k2 <= n or not 0 < p < 1:
        return {'is_valid': False}

    q = 1 - p
    f_arg1 = round((k1 - n * p) / math.sqrt(n * p * q), 2)
    f_arg2 = round((k2 - n * p) / math.sqrt(n * p * q), 2)
    plus = False
    f1 = round(norm.cdf(f_arg1) - 0.5, 4)
    f2 = round(norm.cdf(f_arg2) - 0.5, 4)
    P = round(f2 - f1, 4)
    if f1 < 0:
        plus = True
        f1 = -f1

    solve = {
        'is_valid': True, 'k1': k1, 'k2': k2, 'n': n,
        'p': p, 'q': q, 'arg1': f_arg1, 'arg2': f_arg2,
        'f1': f1, 'f2': f2, 'P': P, 'plus': plus,
    }
    return solve


@task_decorate
def probabilitytheoryEx21(request):
    """Дана плотность распределения f(x) случайной величины ξ. Найти параметр γ,
    математическое ожидание, дисперсию, функцию распределения случайной величины ξ, вероятность выполнния
    неравенства x1 < ξ < x2."""
    x1 = request.GET.get('x1')
    x2 = request.GET.get('x2')
    a = request.GET.get('a')
    b = request.GET.get('b')
    uniform_type = request.GET.get('type')
    if not check_args(uniform_type) and uniform_type not in ('1', '2', '3', '4'):
        return {'is_valid': False}
    try:
        a, b, x1, x2 = float(a), float(b), float(x1), float(x2)
    except (ValueError, TypeError):
        return {'is_valid': False}

    if x2 < x1:
        return {'is_valid': False}

    def uniform_type_1(a, b, x1, x2):
        γ = b
        f = 1 / (γ - a)
        mean = uniform.mean(a, b - a)
        var = uniform.var(a, b - a)
        p = uniform.cdf(x2, a, b - a) - uniform.cdf(x1, a, b - a)
        return γ, mean, var, p, f, a, b

    def uniform_type_2(a, b, x1, x2):
        γ = (a * b - 1) / a
        f = a
        a = γ
        mean = uniform.mean(a, b - a)
        var = uniform.var(a, b - a)
        p = uniform.cdf(x2, a, b - a) - uniform.cdf(x1, a, b - a)
        return γ, mean, var, p, f, a, b

    def uniform_type_3(a, b, x1, x2):
        γ = f = 1 / (b - a)
        mean = uniform.mean(a, b - a)
        var = uniform.var(a, b - a)
        p = uniform.cdf(x2, a, b - a) - uniform.cdf(x1, a, b - a)
        return γ, mean, var, p, f, a, b

    def uniform_type_4(a, b, x1, x2):
        γ = 1 / a
        f = a
        a = (a * b - 1) / (2 * a)
        b = a + γ
        mean = uniform.mean(a, b - a)
        var = uniform.var(a, b - a)
        p = uniform.cdf(x2, a, b - a) - uniform.cdf(x1, a, b - a)
        return γ, mean, var, p, f, a, b

    distributions = {
        '1': uniform_type_1,
        '2': uniform_type_2,
        '3': uniform_type_3,
        '4': uniform_type_4,
    }
    γ, mean, var, p, f, a, b = distributions[uniform_type](a, b, x1, x2)
    solve = {
        'type': uniform_type, 'a': round(a, 2), 'b': round(b, 2),
        'x1': x1, 'x2': x2, 'gamma': round(γ, 2), 'mean': round(mean, 2),
        'mean2': round(var + mean ** 2, 2), 'var': round(var, 2),
        'p': round(p, 2), 'f': round(f, 2), 'is_valid': True,
    }
    return solve


@task_decorate
def probabilitytheoryEx22(request):
    x1 = request.GET.get('x1')
    x2 = request.GET.get('x2')
    a = request.GET.get('a')
    b = request.GET.get('b')
    c = request.GET.get('c')

    try:
        a, b, c, x1, x2 = float(a), float(b), float(c), float(x1), float(x2)
    except (ValueError, TypeError):
        return {'is_valid': False}

    if x2 < x1 or a >= 0:
        return {'is_valid': False}

    gamma = math.exp((b ** 2 - 4 * c * a) / (4 * a)) * math.sqrt(-a / math.pi)
    pdf = norm(-b / (2 * a), math.sqrt(-1 / (2 * a)))
    mean = pdf.mean()
    var = pdf.var()
    f1 = round(pdf.cdf(x1) - 0.5, 3)
    f2 = round(pdf.cdf(x2) - 0.5, 3)
    p = round(f2 - f1, 3)
    x = np.linspace(mean - var - 2, mean + var + 2, num=50)
    y_pdf = pdf.pdf(x)
    y_cdf = pdf.cdf(x)
    solve = {
        "gamma": round(gamma, 3), "mean": round(mean, 3), "var": round(var, 3),
        "p": p, "a": a, "b": "{:+}".format(b), "c": "{:+}".format(c), "f1": f1,
        "f2": f2, "x": list(x), "pdf": list(y_pdf), "cdf": list(y_cdf),
        "var_kv": round(np.sqrt(var), 3), "x1": x1, "x2": x2, 'is_valid': True,
    }
    return solve


@task_decorate
def probabilitytheoryEx23(request):
    n = request.GET.get('n')
    p = request.GET.get('p')
    a = request.GET.get('a')
    type = request.GET.get('type')

    if not type:
        return {'is_valid': False}

    def binomial_distribution(*args):
        try:
            n, p = int(args[0]), float(args[1])
        except (ValueError, TypeError):
            return {'is_valid': False}
        if n<=0 or not 0 < p < 1:
            return {'is_valid': False}
        t = Symbol('t')
        mean, var = binom.stats(n, p)
        cf = (1 - p + p*exp(I*t))**n
        d_cf = diff(cf, t)
        dd_cf = diff(d_cf, t)
        mean2 = round(float(lambdify(t, -dd_cf)(0)), 2)
        return {
            'n': n, 'p': p, 'q': round(1-p, 2), 'mean': round(float(mean), 2), 'mean2': mean2,
            'var': round(float(var), 2), 'g': latex(cf), 'g1': latex(d_cf), 'g2': latex(dd_cf),
            'type': type, 'is_valid': True,
            }

    def pascal_distribution(*args):
        try:
            a = float(args[2])
        except (ValueError, TypeError):
            return {'is_valid': False}
        if not 0 < a < 1:
            return {'is_valid': False}
        t = Symbol('t')
        mean, var, mean2 = a, round(a*(a+1), 2), round(a*(2*a+1), 2)
        cf = 1 / (1 + a*(1-exp(I*t)))
        d_cf = diff(cf, t)
        dd_cf = diff(d_cf, t)
        return {
            'a': a, 'plus_a': 1+a, 'mean': mean, 'mean2': mean2, 'var': var, 'g': latex(cf),
            'g1': latex(d_cf), 'g2': latex(dd_cf), 'type': type, 'is_valid': True,
        }

    def poisson_distribution(*args):
        try:
            a = float(args[2])
        except (ValueError, TypeError):
            return {'is_valid': False}
        if not 0 < a < 1:
            return {'is_valid': False}
        t = Symbol('t')
        mean, var = poisson.stats(a)
        cf = exp(a * (exp(I*t)-1))
        d_cf = diff(cf, t)
        dd_cf = diff(d_cf, t)
        mean2 = round(float(lambdify(t, -dd_cf)(0)), 2)
        return {
            'a': a, 'mean': mean, 'mean2': mean2, 'var': var,
            'g': latex(nsimplify(cf, tolerance=0.1)),
            'g1': latex(nsimplify(d_cf, tolerance=0.1)),
            'g2': latex(nsimplify(dd_cf, tolerance=0.1)),
            'type': type, 'is_valid': True,
        }

    distributions = {
        '1': binomial_distribution,
        '2': pascal_distribution,
        '3': poisson_distribution,
    }

    return distributions[type](n, p, a)


@task_decorate
def probabilitytheoryEx24(request):
    a = request.GET.get('a')
    b = request.GET.get('b')
    type = request.GET.get('type')

    if not type:
        return {'is_valid': False}

    def uniform_distribution(*args):
        try:
            a, b = float(args[0]), float(args[1])
        except (ValueError, TypeError):
            return {'is_valid': False}
        if b < a:
            a, b = b, a
        elif b == a:
            return {'is_valid': False}
        t = Symbol('t')
        mean, var = uniform.stats(loc=a, scale=b-a, moments='mv')
        cf = (exp(I*t*b) - exp(I*t*a)) / (I*t*(b-a))
        d_cf = diff(cf, t)
        dd_cf = diff(d_cf, t)
        mean2 = uniform.moment(2, loc=a, scale=b-a)
        return {
            'a': a, 'b': b, 'mean': round(float(mean), 2), 'mean2': round(mean2, 2), 'b_minus_a': b - a,
            'var': round(float(var), 2),
            'g': latex(nsimplify(cf, tolerance=0.1)),
            'g1': latex(nsimplify(d_cf, tolerance=0.1)),
            'g2': latex(nsimplify(dd_cf, tolerance=0.1)),
            'type': type, 'is_valid': True,
            }

    def gamma_distribution(*args):
        try:
            a, b = float(args[0]), float(args[1])
        except (ValueError, TypeError):
            return {'is_valid': False}
        if not a > 0 or not b > 0:
            return {'is_valid': False}
        t = Symbol('t')
        mean, var = gmm.stats(b, scale=1/a, moments='mv')
        cf = nsimplify((1-I*t/a)**(-b), tolerance=1e-2)
        d_cf = diff(cf, t)
        dd_cf = diff(d_cf, t)
        mean2 = round(gmm.moment(2, b, scale=1/a), 2)
        return {
            'a': a, 'b': b, 'b_minus': round(b-1, 2), 'b_plus': round(b+1, 2), 'mean': mean, 'mean2': mean2,
            'var': var, 'g': latex(cf), 'g1': latex(d_cf), 'g2': latex(dd_cf), 'type': type, 'is_valid': True,
        }

    def norm_distribution(*args):
        try:
            a, b = float(args[0]), float(args[1])
        except (ValueError, TypeError):
            return {'is_valid': False}
        if not b > 0:
            return {'is_valid': False}
        t = Symbol('t')
        mean, var, mean2 = a, b, norm.moment(2, loc=a, scale=sqrt(b))
        cf = exp(I*a*t-b*t**2/2)
        d_cf = diff(cf, t)
        dd_cf = diff(d_cf, t)
        return {
            'a': a, 'b': b, 'mean': mean, 'mean2': mean2, 'var': var,
            'g': latex(nsimplify(cf, tolerance=0.1)),
            'g1': latex(nsimplify(d_cf, tolerance=0.1)),
            'g2': latex(nsimplify(dd_cf, tolerance=0.1)),
            'type': type, 'is_valid': True,
        }

    distributions = {
        '1': uniform_distribution,
        '2': gamma_distribution,
        '3': norm_distribution,
    }

    return distributions[type](a, b)
