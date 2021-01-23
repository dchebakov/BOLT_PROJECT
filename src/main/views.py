import json
import math
import os
import re

import scipy.stats as ss
from main.tasks.economics import *
from main.tasks.numericalanalysis import *
from main.tasks.analyticgeometry import *
from main.tasks.complexanalysis import *
from main.tasks.diffequation import *
from main.tasks.diffgeometry import *
from main.tasks.functionalanalysis import *
from main.tasks.linearalgebra import *
from main.tasks.mathanalysis import *
from main.tasks.mathstatistics import *
from main.tasks.probabilitytheory import *
from main.tasks.stochasticprocesstheory import *
from main.tasks.technopark import *
from django.conf import settings as st
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistrationForm, SettingsForm, CommentForm
from .models import UserProfile, News, Section, Task, Comment, Thanks

COUNT_POSTS_ON_PAGE = 4
COUNT_TOP_TAGS = 5
COUNT_BEST_MEMBERS = 3


def get_profile(request):
    profile = None
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
    return profile


def get_default_data(request):
    '''стандартные данные для всех страниц'''
    return {'profile': get_profile(request),
            'sections': Section.objects.all(), 'form': login(request),
            'last_comments': Comment.objects.all().order_by('-date_created')[:10]
            }


def paginate(query_set, request):
    '''фукнция пагинации'''
    paginator = Paginator(query_set, COUNT_POSTS_ON_PAGE)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return posts


def login(request):
    '''функция для получения формы авторизации и её обработки'''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            if user and user.is_active:
                auth.login(request, form.get_user())
                form = 'login'
    else:
        form = None
        if not request.user.is_authenticated:
            form = AuthenticationForm()
    return form


def section(request, section_title):
    try:
        tasks = Task.objects.filter(section=Section.objects.get(slug=section_title))
    except Task.DoesNotExist:
        tasks = None

    return render(request, 'search.html', dict({'tasks': tasks}, **get_default_data(request)))


def task(request, id):
    try:
        task = Task.objects.get(pk=int(id))
    except Task.DoesNotExist:
        raise Http404

    try:
        return globals()[task.function_name](request)
    except KeyError:
        raise Http404


def main(request):
    default_data = get_default_data(request)
    if default_data['form'] == 'login':
        return redirect(main)
    return render(request, 'index.html',
                  dict({'news': paginate(News.objects.get_new(), request)},
                       **default_data))


def signup(request):
    if request.user.is_authenticated:
        return redirect(settings)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            profile = UserProfile.objects.create(
                user=user,
                avatar=form.cleaned_data['avatar']
            )
            profile.save()
            auth.login(request, profile.user)
            return redirect(main)
    else:
        form = RegistrationForm()

    return render(request, 'signup.html', {'form': form,
                                           'sections': Section.objects.all()})


def logout(request):
    auth.logout(request)
    return redirect(main)


def settings(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        if request.method == 'POST':
            form = SettingsForm(request.POST, request.FILES)
            if form.is_valid():
                user = request.user
                if form.cleaned_data['username']:
                    user.username = form.cleaned_data['username']
                if form.cleaned_data['email']:
                    user.email = form.cleaned_data['email']
                if form.cleaned_data['first_name']:
                    user.first_name = form.cleaned_data['first_name']
                user.save()
                profile = UserProfile.objects.get(user=User.objects.get(pk=user.id))
                if form.cleaned_data['avatar']:
                    profile.avatar = form.cleaned_data['avatar']
                profile.save()
                return redirect(settings)
        else:
            form = SettingsForm()
            form.set_default_value(request.user)
        return render(request, 'settings.html', {'user': request.user,
                                                 'form': form,
                                                 'profile': profile,
                                                 'sections': Section.objects.all(),
                                                 'last_comments': Comment.objects.all().order_by('-date_created')[:5]})


def search(request):
    terms = request.GET.get('terms')
    tasks = Task.objects.filter(title__icontains=terms)
    if len(tasks) == 0:
        tasks = None
        terms = 'Nothing was found'
    else:
        posts = paginate(tasks, request)

    default_data = get_default_data(request)
    if default_data['form'] == 'login':
        return redirect(main)

    return render(request, 'search.html', dict({'tasks': tasks,
                                                'title': terms},
                                               **default_data))


def comment(request, id):
    try:
        task = Task.objects.get(pk=id)
    except Task.DoesNotExist:
        return redirect(main)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                user=UserProfile.objects.get(user=request.user),
                text=form.cleaned_data['text'],
                task=Task.objects.get(pk=id)
            )
    return redirect(task)


def thanks(request):
    if request.method == 'POST':
        Thanks.objects.create(
            task=Task.objects.get(pk=request.POST['taskid']),
            user=UserProfile.objects.get(user=request.user)
        ).like()
        task = Task.objects.get(pk=request.POST['taskid'])
        return HttpResponse(json.dumps({'rating': task.rating}), content_type='application/json')

    return redirect(main)


def success(request):
    return render(request, 'success.html',
                  {'success': 'Спасибо! В ближайшее время мы проверим решение и опубликуем его на сайте!',
                   'user': request.user,
                   'profile': get_profile(request),
                   'sections': Section.objects.all(),
                   'last_comments': Comment.objects.all().order_by('-date_created')[:5]})


def utility(request):
    if request.method == 'GET':
        return render(request, 'utility.html', get_default_data(request))
    else:
        content = json.loads(request.body.decode('utf-8'))
        case = content['case']
        res = 'err'
        if case == 'quantile':
            dist_type = content['type']
            freedom1 = float(content['freedom1'])
            freedom2 = float(content['freedom2'])
            level = float(content['level'])

            if dist_type == 'norm':
                res = ss.norm.ppf(level)
            elif dist_type == 't':
                res = ss.t.ppf(level, freedom1)
            elif dist_type == 'exp':
                res = ss.expon.ppf(level, freedom1)
            elif dist_type == 'chi2':
                res = ss.chi2.ppf(level, freedom1)
            elif dist_type == 'f':
                res = ss.f.ppf(level, freedom1, freedom2)

        elif case == 'laplace':
            laplace_type = content['type']
            argument = float(content['argument'])

            if laplace_type == 'laplace-int-0':
                res = ss.norm.cdf(argument) - 0.5
            elif laplace_type == 'laplace-int-inf':
                res = 1 - ss.norm.cdf(argument)
            elif laplace_type == 'laplace-int-from-inf':
                res = ss.norm.cdf(argument)
            elif laplace_type == 'laplace-diff':
                res = math.exp(- argument ** 2 / 2) / math.sqrt(2 * math.pi)

        elif case == 'sample':
            sample_type = content['type']
            m_for_norm = float(content['m_for_norm'])
            d_for_norm = float(content['d_for_norm'])
            lambda_for_exp = float(content['lambda_for_exp'])
            a_for_uniform = float(content['a_for_uniform'])
            b_for_uniform = float(content['b_for_uniform'])
            sample_volume = int(content['volume'])

            if sample_volume < 1:
                return HttpResponse('err', content_type='application/json')

            if sample_type == 'norm':
                res = ss.norm.rvs(loc=m_for_norm, scale=d_for_norm, size=sample_volume)
            elif sample_type == 'exp':
                if lambda_for_exp <= 0:
                    return HttpResponse('err', content_type='application/json')
                res = ss.expon.rvs(scale=1 / lambda_for_exp, size=sample_volume)
            elif sample_type == 'uniform':
                res = ss.uniform.rvs(loc=a_for_uniform, scale=(b_for_uniform - a_for_uniform), size=sample_volume)

            if res != 'err':
                res = ', '.join(str(round(e, 2)) for e in res)

        elif case == 'markov':
            state = int(content['state'])
            if state < 1:
                return HttpResponse('err', content_type='application/json')

            vectors = [list(ss.uniform.rvs(loc=0, scale=1, size=state - 1)) for i in range(state + 1)]
            matrix = []
            for el in vectors:
                el.extend([1, 0])
                el.sort()
                row = []
                for i in range(state):
                    row.append(el[i + 1] - el[i])
                matrix.append(row)
            res = r'\begin{{pmatrix}} {} \end{{pmatrix}}^T'.format(
                ' & '.join([str(round(el, 2)) for el in matrix.pop(0)]))

            def matrix2latex(lst):
                return r'\begin{{pmatrix}} {} \end{{pmatrix}}'.format(
                    r' \\ '.join([(str.join(' & ', (str(round(el, 2)) for el in row))) for row in lst]))

            res += ' \\\\ A = ' + matrix2latex(matrix)

        return HttpResponse(res, content_type='application/json')


def about_us(request):
    return render(request, 'aboutus.html', get_default_data(request))


def test(request):
    return render(request, '404.html')
