"""BBS2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views
from django.views.static import serve
from BBS2 import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),

    url(r'^media/(?P<path>.*)', serve, {'document_root':settings.MEDIA_ROOT}),


    url(r'^login/', views.login),
    url(r'^register/', views.register),
    url(r'^get_verification/', views.get_verification),
    url(r'^change_password/', views.change_password),
    url(r'^change_avatar/', views.change_avatar),
    url(r'^logout/', views.logout),
    url(r'^up_and_down/', views.up_and_down),
    url(r'^submit_comment/', views.submit_comment),
    url(r'^back_stage/', views.back_stage),
    url(r'^add_essays/', views.add_essays),



    url(r'^home/', views.home),
    url(r'^(?P<username>\w+)/$', views.site),
    url(r'^(?P<username>\w+)/(?P<conditions>category|tag|achieve)/(?P<params>.+)/', views.site),
    url(r'^(?P<username>\w+)/p/(?P<article_id>\d+)/', views.p),
]
