from __future__ import division, absolute_import, unicode_literals

import io
from collections import Counter

from django import forms
from django.core.exceptions import ValidationError

from weblatex.models import Song, Booklet, BookletEntry, UploadedSong
from weblatex import layout
from weblatex.engine import pdflatex, render_tex, TexException
from weblatex.fields import PositionField
from weblatex.upload import parse


class BookletForm(forms.ModelForm):
    class Meta:
        model = Booklet
        fields = ()

    def __init__(self, *args, **kwargs):
        super(BookletForm, self).__init__(*args, **kwargs)
        entries = list(self.instance.bookletentry_set.all())
        entry_pk = set(e.song.pk for e in entries)
        other_songs = Song.objects.exclude(pk__in=entry_pk)
        self._songs = []
        for i, entry in enumerate(entries):
            self.add_entry(i, entry)
        for song in other_songs:
            self.add_song(song)

    @property
    def songs(self):
        s = []
        for song in self._songs:
            s.append({
                'page': self['page_%d' % song.pk],
                'position': self['position_%d' % song.pk],
                'song': song,
                'twocolumn': self['twocolumn_%d' % song.pk],
                'attribution': self['attribution_%d' % song.pk],
            })
        return s

    def add_entry(self, i, entry):
        self.add_song_fields(
            entry.song, page=entry.page,
            position=entry.position,
            twocolumn=entry.twocolumn,
            attribution=entry.attribution,
        )

    def add_song(self, song):
        self.add_song_fields(
            song, page=None, position=None, twocolumn=False,
            attribution=True,
        )

    def add_song_fields(self, song, page, position, twocolumn, attribution):
        self.fields['page_%d' % song.pk] = forms.IntegerField(
            initial=page, required=False)
        self.fields['position_%d' % song.pk] = PositionField(
            initial=position, required=False)
        self.fields['twocolumn_%d' % song.pk] = forms.BooleanField(
            initial=twocolumn, required=False)
        self.fields['attribution_%d' % song.pk] = forms.BooleanField(
            initial=attribution, required=False)
        self._songs.append(song)

    def _save_m2m(self):
        super(BookletForm, self)._save_m2m()
        entries = []
        for s in Song.objects.all():
            page = self.cleaned_data.get('page_%d' % s.pk)
            position = self.cleaned_data.get('position_%d' % s.pk)
            twocolumn = self.cleaned_data.get('twocolumn_%d' % s.pk)
            attribution = self.cleaned_data.get('attribution_%d' % s.pk)
            if page:
                position_str = PositionField.position_to_str(position)
                entries.append(
                    BookletEntry(booklet=self.instance,
                                 song=s,
                                 page=page,
                                 position=position_str,
                                 twocolumn=twocolumn,
                                 attribution=attribution))
        self.instance.bookletentry_set.all().delete()
        BookletEntry.objects.bulk_create(entries)

    def clean(self):
        x = []
        for song in self._songs:
            page = self.cleaned_data['page_%d' % song.pk]
            position = self.cleaned_data['position_%d' % song.pk]
            if page:
                x.append((page, position))
        c = Counter(x)
        for song in self._songs:
            page = self.cleaned_data['page_%d' % song.pk]
            position = self.cleaned_data['position_%d' % song.pk]
            if c[page, position] > 1:
                self.add_error('position_%d' % song.pk,
                               '%s: Duplicate position' % song.name)


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ('name', 'attribution', 'lyrics')

    def clean_lyrics(self):
        d = self.cleaned_data
        filename = 'lyrics.tex'
        song = layout.Song(d['name'], d['attribution'], filename).read()
        files = [(filename, layout.Lyrics(d['lyrics']).read())]

        try:
            pdflatex(render_tex(song), files=files)
        except TexException as e:
            raise ValidationError(str(e))

        return self.cleaned_data['lyrics']


class SongUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        f = self.cleaned_data['file'].read()
        return parse(f), f  # Might raise ValidationError

    def save(self):
        song, source = self.cleaned_data['file']
        song.save()
        uploaded_song = UploadedSong(song=song, source=source)
        uploaded_song.save()
