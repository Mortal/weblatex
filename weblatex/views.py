from __future__ import division, absolute_import, unicode_literals

from django.views.generic import TemplateView, View, FormView, CreateView, UpdateView

from django.core.urlresolvers import reverse

from weblatex.forms import BookletForm, SongForm
from weblatex.engine import render_pdf
from weblatex.models import Song


class Booklet(FormView):
    form_class = BookletForm
    template_name = 'weblatex/booklet.html'

    def form_valid(self, form):
        data = '\n'.join(song.as_tex() for song in form.cleaned_data['songs'])
        return render_pdf(data)


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
