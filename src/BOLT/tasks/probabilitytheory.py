import math
from django.shortcuts import render
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

import re


def comments(request, task):
    is_like = True
    if request.user.is_authenticated():
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
    p = []
    for i in n:
        p.append(i / sum(n))
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

    try:
        P = 1 - 2 / k
    except ZeroDivisionError:
        return {'is_valid': False}

    solve = {
        'k': k, 'P': round(P, 3),
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

    if T2 <= T1:
        return {'is_valid': False}

    T = T2 - T1  # сторона квадрата
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

    if S2 + S1 > math.pi * R ** 2:
        return {'is_valid': False}

    P = (S1 + S2) / (math.pi * R ** 2)

    solve = {
        'S1': S1, 'S2': S2, 'R': R,
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
        "q1": q1, "q2": q2, "P": round(P, 3), 'is_valid': True,
    }

    return solve


@task_decorate
def probabilitytheoryEx10(request):
    k = request.GET.get('k')

    if not check_args(k):
        return {'is_valid': False}

    k = int(k)

    """Вероятность выпадения герба и решки одинаковы, p = q = 0,5"""
    p = 0.5
    q = 1 - p

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
        'P_A1': round(P_A1, 3), 'P_A2': round(P_A2, 3), 'P_A3': round(P_A3, 3),
        'P_B1': round(P_B1, 3), 'P_B2': round(P_B2, 3), 'P_B3': round(P_B3, 3),
        'dk': 2 * k, 'is_valid': True, 'dk_minus_3': 2 * k - 3, 'k_minus_1': k - 1,
        'dk_minus_2': 2 * k - 2, 'dk_minus_1': 2 * k - 1, 'k': k,
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
