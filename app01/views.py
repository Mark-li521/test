from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from app01 import models
from app01.myform.myreg import MyReg
from utils.mypage import Pagination


# Create your views here.

def login(request):
    if request.is_ajax():
        if request.method == "POST":
            back_dic = {'code': 1000, 'msg': ''}
            username = request.POST.get('username')
            password = request.POST.get('password')
            verification = request.POST.get('verification')
            if verification.upper() == request.session.get('verification').upper():
                user_obj = auth.authenticate(username=username, password=password)
                if user_obj:
                    auth.login(request, user_obj)
                    back_dic['url'] = '/home/'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '用户名或密码错误'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '验证码错误'
            return JsonResponse(back_dic)
    return render(request, 'blog/login.html')


def register(request):
    my_reg = MyReg()
    if request.is_ajax():
        if request.method == "POST":
            back_dic = {'code': 1000, 'msg': ''}
            my_reg = MyReg(request.POST)
            if my_reg.is_valid():
                clean_data = my_reg.cleaned_data
                clean_data.pop('confirm_password')
                avatar_obj = request.FILES.get('avatar')
                if avatar_obj:
                    clean_data['avatar'] = avatar_obj
                models.User.objects.create_user(**clean_data)
                back_dic['url'] = '/login/'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = my_reg.errors
            return JsonResponse(back_dic)

    return render(request, 'blog/register.html', locals())


import random
from PIL import ImageFont, Image, ImageDraw
from io import BytesIO


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_verification(request):
    img_obj = Image.new('RGB', (230, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('static/font/111.ttf', 35)
    verification = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))

        code = random.choice([random_upper, random_lower, random_int])

        verification += code
        img_draw.text((20 + 40 * i, 0), code, get_random(), img_font)
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    print(verification)

    request.session['verification'] = verification

    return HttpResponse(io_obj.getvalue())


def home(request):
    article_list = models.Article.objects.all()
    page_obj = Pagination(current_page=request.GET.get('page'), all_count=article_list.count(), per_page_num=5)

    page_queryset = article_list[page_obj.start: page_obj.end]
    return render(request, 'blog/home.html', locals())


@login_required
def change_password(request):
    if request.is_ajax():
        if request.method == "POST":
            back_dic = {'code': 1000, 'msg': ''}
            old_password = request.POST.get('old_password')
            if request.user.check_password(old_password):
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                if new_password == confirm_password:
                    back_dic['url'] = '/home/'
                    request.user.set_password(new_password)
                    request.user.save()
                else:
                    back_dic['code'] = 10001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
            return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/login/')


@login_required
def change_avatar(request):
    if request.is_ajax():
        if request.method == "POST":
            back_dic = {'code': 1000, 'msg': ''}
            avatar = request.FILES.get('avatar')
            if avatar:
                request.user.avatar = avatar
                request.user.save()
                back_dic['msg'] = '修改头像成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '你没有上传头像，不要瞎点'
            return JsonResponse(back_dic)


def site(request, username, **kwargs):
    user_obj = models.User.objects.filter(username=username)
    if not user_obj:
        return render(request, '404.html')
    article_list = models.Article.objects.filter(blog__user__username=username)
    if kwargs:
        conditions = kwargs.get('conditions')
        params = kwargs.get('params')
        if conditions == 'category':
            article_list = article_list.filter(category__pk=params)
            if not article_list:
                return render(request, '404.html')
        elif conditions == 'tag':
            article_list = article_list.filter(tags__pk=params)
            if not article_list:
                return render(request, '404.html')
        elif conditions == 'achieve':
            year, month = params.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
            if not article_list:
                return render(request, '404.html')
        else:
            return render(request, '404.html')
    page_obj = Pagination(current_page=request.GET.get('page'), all_count=article_list.count(), per_page_num=5)

    page_queryset = article_list[page_obj.start: page_obj.end]

    return render(request, 'blog/site.html', locals())


def p(request, username, article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article_id=article_id)
    return render(request, 'blog/p.html', locals())


import json
from django.db.models import F


def up_and_down(request):
    if request.is_ajax():
        if request.method == "POST":
            back_dic = {'code': 1000, 'msg': ''}
            is_up = request.POST.get('is_up')
            is_up = json.loads(is_up)
            article_id = request.POST.get('article_id')

            if request.user.is_authenticated():
                article_obj = models.Article.objects.filter(pk=article_id).first()
                if not article_obj.blog.user == request.user:
                    is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                    if not is_click:
                        if is_up:
                            models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                            back_dic['msg'] = '点赞成功'
                        else:
                            models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                            back_dic['msg'] = '点踩成功'
                        models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                    else:
                        back_dic['code'] = 1001
                        if is_click.first().is_up:
                            back_dic['msg'] = '你已经点过赞了'
                        else:
                            back_dic['msg'] = '你已经点过踩了'
                else:
                    back_dic['code'] = 1002
                    if is_up:
                        back_dic['msg'] = '不可以给自己点赞'
                    else:
                        back_dic['msg'] = '不可以给自己点踩'
            else:
                back_dic['code'] = 1003
                back_dic['msg'] = '请先<a href="/login/">登陆</a>'
            return JsonResponse(back_dic)


def submit_comment(request):
    if request.is_ajax():
        if request.method == "POST":
            parent_id = request.POST.get('parent_id')
            content = request.POST.get('content')
            article_id = request.POST.get('article_id')
            back_dic = {'code': 1000, 'msg': ''}
            if content:
                models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                models.Comment.objects.create(article_id=article_id, user=request.user, content=content,
                                              parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '不要瞎点'

            return JsonResponse(back_dic)


@login_required
def back_stage(request):
    category_list = models.Category.objects.filter(blog__user=request.user)
    article_list = models.Article.objects.filter(blog__user=request.user)
    return render(request, 'back/back_stage.html', locals())


from bs4 import BeautifulSoup


def add_essays(request):
    category_list = models.Category.objects.filter(blog__user=request.user)
    tag_list = models.Tag.objects.filter(blog__user=request.user)
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_lis = request.POST.getlist('tag')
        soup = BeautifulSoup(content, 'lxml')
        h5_list = soup.find_all()
        for tag in h5_list:
            if tag.name == 'script':
                tag.decompose()

        content = str(soup)
        desc = soup.get_text()[0:150] + '...'
        article_obj = models.Article.objects.create(title=title, desc=desc, content=content, blog=request.user.blog,
                                                    category_id=category_id)
        tag_obj_list = []
        for tag in tag_lis:
            tag_obj_list.append(models.Article2Tag(article=article_obj, tag_id=tag))
        models.Article2Tag.objects.bulk_create(tag_obj_list)
        return redirect('/back_stage/')
    return render(request, 'back/add_essays.html', locals())
