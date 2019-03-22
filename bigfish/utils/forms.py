# encoding: utf-8

"""
@author: h3l
@contact: xidianlz@gmail.com
@file: forms.py
@time: 2017/7/15 20:40
"""
# -*- coding: utf-8 -*-

from django import forms


class FileForm(forms.Form):
    file = forms.FileField()
