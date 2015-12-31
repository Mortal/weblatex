"""weblatex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
# from django.conf.urls import include
from django.contrib import admin
from weblatex.views import (
    BookletCreate, BookletSongs, BookletRender,
    SongCreate, SongUpdate,
    Front,
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', Front.as_view(), name='front'),
    url(r'^booklet/add/$', BookletCreate.as_view(), name='booklet_create'),
    url(r'^booklet/(?P<pk>\d+)/songs/$', BookletSongs.as_view(),
        name='booklet_songs'),
    url(r'^booklet/(?P<pk>\d+)/render/$', BookletRender.as_view(),
        name='booklet_render'),
    url(r'^song/(?P<pk>\d+)/$', SongUpdate.as_view(), name='song_update'),
    url(r'^song/add/$', SongCreate.as_view(), name='song_create'),
]
