from django.conf.urls import patterns, include, url
from .views import InputView, RenderView

urlpatterns = patterns('',
    url(r'^$', InputView.as_view()),
    url(r'^render.pdf$', RenderView.as_view(), name='render_view'),
)
