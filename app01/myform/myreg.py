#! /usr/bin/env python3
# _*_coding:utf_8 _*_
"""
    Author:Markli

    #  2019/11/8,9:00
"""
from django.forms import *

from app01.models import User


class MyReg(Form):
    username = CharField(min_length=3, max_length=9, label='用户名：',
                         error_messages={
                             'min_length': '用户名不短于3位',
                             'max_length': '用户名不长于3位',
                             'required': '用户名不为空',
                         }, widget=widgets.TextInput(attrs={'class': 'form-control'}))

    password = CharField(min_length=3, max_length=9, label='密码：',
                         error_messages={
                             'min_length': '密码不短于3位',
                             'max_length': '密码不长于3位',
                             'required': '密码不为空',
                         }, widget=widgets.PasswordInput(attrs={'class': 'form-control'}))

    confirm_password = CharField(min_length=3, max_length=9, label='确认密码：',
                                 error_messages={
                                     'min_length': '确认密码不短于3位',
                                     'max_length': '确认密码不长于3位',
                                     'required': '确认密码不为空',
                                 }, widget=widgets.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            self.add_error('username', '用户名已存在')
        return username

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not password == confirm_password:
            self.add_error('confirm_password', '两次密码不一致')
        return self.cleaned_data
