#! /usr/bin/env python3
# _*_coding:utf_8 _*_
"""
    Author:Markli

    #  2019/11/8,10:34
"""

from django.template import Library
from django.db.models import Count
from django.db.models.functions import TruncMonth
from app01.models import *

register = Library()


@register.inclusion_tag('blog/sidebar.html')
def sidebar(username):
    user_obj = User.objects.filter(username=username).first()
    blog = user_obj.blog
    category_list = Category.objects.filter(blog=blog).annotate(num=Count('article__pk'))
    tag_list = Tag.objects.filter(blog=blog).annotate(num=Count('article__pk'))
    date_list = Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(num=Count('pk'))
    return locals()
