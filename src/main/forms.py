import os
import re
from django import forms
from django.conf import settings as st
from django.contrib import admin
from django.contrib.auth.models import User

from .models import UserProfile, Task


class SettingsForm(forms.Form):
    username = forms.CharField(required=False, label='Логин')
    email = forms.EmailField(required=False, max_length=100, label="E-mail")
    first_name = forms.CharField(required=False, max_length=30, label='Ваше имя')
    avatar = forms.ImageField(required=False, label='Аватар')

    def clean_username(self):
        username = self.cleaned_data['username']
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('Пользователь уже существует.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        if avatar and avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Слишком большой размер картинки ( > 2mb)")
        return avatar

    def set_default_value(self, user):
        self.fields.get('username').widget = forms.TextInput(attrs={'placeholder': user.username})
        self.fields.get('email').widget = forms.TextInput(attrs={'placeholder': user.email})
        self.fields.get('first_name').widget = forms.TextInput(attrs={'placeholder': user.first_name})


class RegistrationForm(forms.Form):
    username = forms.CharField(required=True, label='Логин')
    email = forms.EmailField(required=True, max_length=100, label="E-mail")
    first_name = forms.CharField(max_length=30, label='Ваше имя')
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)),
        label="Пароль")
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)),
        label="Повторите пароль")
    avatar = forms.ImageField(required=False, label='Аватар')

    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError('Пользователь уже существует.')

    def clean_email(self):
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError('Пользователь уже существует.')

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        if avatar and avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Слишком большой размер картинки ( > 2mb)")
        return avatar

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError('Пароли не совпадают.')
        return self.cleaned_data


class CommentForm(forms.Form):
    text = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введите комментарий', 'class': 'form-control'}),
        required=True
    )


class SectionForm(forms.Form):
    sections = [('probabilitytheory', 'Теория вероятности'),
                ('complexanalysis', 'ТФКП'),
                ('diffgeometry', 'Дифференциальная геометрия'),
                ('diffequation', 'Дифференциальные уравнения'),
                ('functionalanalysis', 'Функциональный анализ'),
                ('mathanalysis', 'Математический анализ'),
                ('linearalgebra', 'Линейная алгебра'),
                ('analyticgeometry', 'Аналитическая геометрия')]
    title = forms.CharField(required=True,
                            label='Условие задачи',
                            widget=forms.Textarea(
                                attrs={'rows': 5, 'placeholder': 'Введите условие задачи', 'class': 'form-control'}))

    section = forms.ChoiceField(choices=sections, label='Раздел', required=True)
    function_name = forms.CharField(required=True,
                                    label='Имя функции',
                                    widget=forms.TextInput(
                                        attrs={'placeholder': 'Введите условие задачи', 'class': 'form-control'}))
