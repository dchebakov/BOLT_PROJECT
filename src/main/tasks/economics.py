import math
from django.shortcuts import render
from ..models import Task, Section
from .. import views
from ..models import Task, Section, Comment, Thanks, UserProfile
from ..forms import CommentForm

from .probabilitytheory import task_decorate, comments
import re


def check_args(*args):
    """Проверка на float"""
    for arg in args:
        if not arg:
            return False
        try:
            float(arg)
        except ValueError:
            return False
    return True


def in_per(num):
    """Перевод в проценты"""
    return round(num * 100, 1)


def rnd(number):
    return round(number, 3)


@task_decorate
def economicsEx1(request):
    osn_k = request.GET.get('osn-k')
    d = request.GET.get('d')
    r = request.GET.get('r')
    f_pl = request.GET.get('f-pl')
    ob_k = request.GET.get('ob-k')
    ch = request.GET.get('ch')
    k_o = request.GET.get('k-o')

    if not check_args(osn_k, d, r, f_pl, ob_k, ch, k_o):
        return {'is_valid': False}

    osn_k = float(osn_k)
    d = float(d)
    r = float(r)
    f_pl = float(f_pl)
    ob_k = float(ob_k)
    ch = int(ch)
    k_o = float(k_o)

    profit = d - r
    assets = osn_k + ob_k
    r_act = profit / assets
    sk = assets - k_o
    r_sk = profit / sk
    r_pr = profit / d
    kpl = ob_k / k_o
    ook = d / osn_k
    r_osk = profit / osn_k
    srm = osn_k / ch
    r_obk = profit / ob_k
    k_ob = d / ob_k
    t_ob = f_pl / k_ob
    v = d / ch

    solve = {'osn_k': osn_k, 'd': d, 'r': r, 'f_pl': f_pl, 'ob_k': ob_k, 'ch': ch, 'k_o': k_o, 'profit': rnd(profit),
             'assets': rnd(assets), 'sk': rnd(sk), 'kpl': rnd(kpl), 'ook': rnd(ook), 'srm': rnd(srm), 'k_ob': rnd(k_ob),
             't_ob': rnd(t_ob), 'v': rnd(v), 'r_act': rnd(r_act), 'r_sk': rnd(r_sk), 'r_pr': rnd(r_pr),
             'r_osk': rnd(r_osk), 'r_obk': rnd(r_obk), 'r_act_per': in_per(r_act), 'r_sk_per': in_per(r_sk),
             'r_pr_per': in_per(r_pr), 'r_osk_per': in_per(r_osk), 'r_obk_per': in_per(r_obk), 'is_valid': True}
    return solve


@task_decorate
def economicsEx2(request):
    n = request.GET.get('n')
    k = request.GET.get('k')
    f_pl = request.GET.get('f-pl')
    N = request.GET.get('N')

    if not check_args(n, k, f_pl, N):
        return {'is_valid': False}

    n = int(n)
    k = int(k)
    f_pl = float(f_pl)
    N = float(N)

    i_n_per = 14 + n
    i_n = i_n_per / 100
    c_n_mln = k * n
    c_n = c_n_mln * 1000
    S = 2 * n
    S_n = n
    t_t = n
    t_tekhn = t_t / 2
    T_kd_prts = 4 * n
    T_real = 5 * n
    A_per = 0.1

    K_nz = (S_n + S) / (2 * S)
    F_np = S * N * K_nz * T_kd_prts / f_pl
    F_z = S_n * N * (t_t + t_tekhn) / f_pl
    F_pp = S * N * T_real / f_pl
    ob_k = F_np + F_z + F_pp

    C = [c_n]
    A = [0]
    PP = []
    for k in range(1, 7):
        A.append(A[k - 1] + C[k - 1] * A_per)
        C.append(c_n - A[k])
        PP.append(0.14 * (ob_k + C[k]) + (A[k] - A[k - 1]))

    A_0 = PP[-1] * ((1 + i_n) ** 3 - 1) / i_n / (1 + i_n) ** 3

    solve = {'n': n, 'k': k, 'f_pl': f_pl, 'N': N, 'i_n': i_n, 'i_n_per': i_n_per, 'c_n': c_n, 'c_n_mln': c_n_mln,
             't_tekhn': t_tekhn, 'T_kd_prts': T_kd_prts, 'T_real': T_real, 'S': S, 'K_nz': rnd(K_nz), 'F_np': rnd(F_np),
             'F_z': rnd(F_z), 'F_pp': rnd(F_pp), 'ob_k': rnd(ob_k), 'C': [rnd(el) for el in C],
             'A': [rnd(el) for el in A], 'PP': [rnd(el) for el in PP], 'A_0': rnd(A_0), 'is_valid': True}

    return solve


@task_decorate
def economicsEx3(request):
    i = request.GET.get('i')
    zk = request.GET.get('zk')
    sk = request.GET.get('sk')
    price_a = request.GET.get('price-a')
    price_b = request.GET.get('price-b')
    nds_a = request.GET.get('nds-a')
    nds_b = request.GET.get('nds-b')
    vol_a = request.GET.get('vol-a')
    vol_b = request.GET.get('vol-b')

    if not check_args(i, zk, sk, price_a, price_b, nds_a, nds_b, vol_a, vol_b):
        return {'is_valid': False}

    i = float(i)
    zk = float(zk)
    sk = float(sk)
    price_a = float(price_a)
    price_b = float(price_b)
    nds_a = float(nds_a)
    nds_b = float(nds_b)
    vol_a = float(vol_a)
    vol_b = float(vol_b)

    assets = sk + zk
    profit = assets * i / 100
    price_a_without_nds = price_a / (100 + nds_a) * 100
    price_b_without_nds = price_b / (100 + nds_b) * 100
    d = price_a_without_nds * vol_a + price_b_without_nds * vol_b
    r = d - profit

    solve = {'i': i, 'zk': zk, 'sk': sk, 'price_a': price_a, 'price_b': price_b, 'nds_a': nds_a, 'nds_b': nds_b,
             'vol_a': vol_a, 'vol_b': vol_b, 'profit': rnd(profit), 'assets': rnd(assets), 'd': rnd(d), 'r': rnd(r),
             'price_a_without_nds': rnd(price_a_without_nds), 'price_b_without_nds': rnd(price_b_without_nds),
             'is_valid': True}

    return solve
