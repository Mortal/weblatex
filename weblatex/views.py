from __future__ import division, absolute_import, unicode_literals

from django.views.generic import (
    TemplateView, View, FormView, CreateView, UpdateView, DetailView)

from django.core.urlresolvers import reverse

from weblatex.forms import BookletForm, SongForm
from weblatex.engine import render_pdf
from weblatex.models import Song, Booklet


class BookletCreate(CreateView):
    form_class = BookletForm
    template_name = 'weblatex/booklet.html'

    def get_success_url(self):
        return reverse('booklet_update', kwargs={'pk': self.object.pk})


class BookletRender(DetailView):
    model = Booklet

    def post(self, *args, **kwargs):
        return render_pdf(self.get_object().as_tex())


class BookletUpdate(UpdateView):
    form_class = BookletForm
    template_name = 'weblatex/booklet.html'
    queryset = Booklet.objects

    def get_success_url(self):
        return reverse('booklet_update', kwargs={'pk': self.object.pk})


class InputView(TemplateView):
    template_name = 'weblatex/input.html'


class RenderView(View):
    def post(self, request):
        return render_pdf(self.request.POST['data'])


class SongCreate(CreateView):
    form_class = SongForm
    template_name = 'weblatex/song_form.html'

    def get_success_url(self):
        return reverse('booklet')


class SongUpdate(UpdateView):
    form_class = SongForm
    template_name = 'weblatex/song_form.html'
    queryset = Song.objects

    def get_success_url(self):
        return reverse('booklet')
