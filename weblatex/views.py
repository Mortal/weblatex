from __future__ import division, absolute_import, unicode_literals

from django.views.generic import (
    TemplateView, View, FormView, CreateView, UpdateView, DetailView)

from django.forms.utils import ErrorList

from django.http import HttpResponse

from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from weblatex.forms import BookletForm, SongForm, SongUploadForm
from weblatex.engine import render_pdf, render_tex
from weblatex.models import Song, Booklet


class BookletCreate(CreateView):
    form_class = BookletForm
    template_name = 'weblatex/booklet.html'

    def get_success_url(self):
        return reverse('front')


class BookletRender(DetailView):
    model = Booklet

    def get(self, request, *args, **kwargs):
        return render_pdf(self.get_object().as_tex(),
                          page_size='a5paper',
                          font_size='10pt')


class BookletRenderSource(DetailView):
    model = Booklet

    def get(self, request, *args, **kwargs):
        return HttpResponse(
            render_tex(self.get_object().as_tex()),
            content_type='text/plain; charset=utf8')


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


class SongUpload(TemplateView):
    template_name = 'weblatex/song_upload_form.html'

    def get(self, request):
        return self.render_to_response(self.get_context_data())

    def post(self, request):
        forms = []
        for f in request.FILES.getlist('file'):
            forms.append(SongUploadForm({}, {'file': f}))
        if all(f.is_valid() for f in forms):
            for f in forms:
                f.save()
            return redirect(reverse('front'))
        else:
            errors = []
            for f in forms:
                errors += list(f.errors.get('file', []))
                errors += list(f.non_field_errors())
            return self.render_to_response(self.get_context_data(
                errors=ErrorList(errors)))


class SongUpdate(UpdateView):
    form_class = SongForm
    template_name = 'weblatex/song_form.html'
    queryset = Song.objects

    def get_success_url(self):
        return reverse('front')
