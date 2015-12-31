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
        return reverse('front')


class BookletRender(DetailView):
    model = Booklet

    def get(self, *args, **kwargs):
        return render_pdf(self.get_object().as_tex())


class BookletSongs(UpdateView):
    form_class = BookletForm
    template_name = 'weblatex/booklet.html'
    queryset = Booklet.objects

    def get_success_url(self):
        return reverse('front')


class Front(TemplateView):
    template_name = 'weblatex/front.html'

    def get_context_data(self, **kwargs):
        context_data = super(Front, self).get_context_data(**kwargs)
        context_data['songs'] = Song.objects.all()
        context_data['booklets'] = Booklet.objects.all()
        return context_data


class SongCreate(CreateView):
    form_class = SongForm
    template_name = 'weblatex/song_form.html'

    def get_success_url(self):
        return reverse('front')


class SongUpdate(UpdateView):
    form_class = SongForm
    template_name = 'weblatex/song_form.html'
    queryset = Song.objects

    def get_success_url(self):
        return reverse('front')
