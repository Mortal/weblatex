from __future__ import division, absolute_import, unicode_literals

from django import forms
from django.core.exceptions import ValidationError

from weblatex.models import Song, lyrics_as_tex, Booklet, BookletEntry
from weblatex.engine import pdflatex, TexException
from weblatex.fields import PageField


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
            })
        return s

    def add_entry(self, i, entry):
        self.add_song_fields(entry.song, page=entry.page,
                             position=entry.position,
                             twocolumn=entry.twocolumn)

    def add_song(self, song):
        self.add_song_fields(song, page=None, twocolumn=False)

    def add_song_fields(self, song, page, position, twocolumn):
        self.fields['page_%d' % song.pk] = forms.IntegerField(
            initial=page, required=False)
        self.fields['position_%d' % song.pk] = PageField(
            initial=position, required=False)
        self.fields['twocolumn_%d' % song.pk] = forms.BooleanField(
            initial=twocolumn, required=False)
        self._songs.append(song)

    def _save_m2m(self):
        super(BookletForm, self)._save_m2m()
        entries = []
        for s in Song.objects.all():
            page = self.cleaned_data.get('page_%d' % s.pk)
            position = self.cleaned_data.get('position_%d' % s.pk)
            twocolumn = self.cleaned_data.get('twocolumn_%d' % s.pk)
            if page:
                position_str = PageField.position_to_str(position)
                entries.append(
                    BookletEntry(booklet=self.instance,
                                 song=s,
                                 page=page,
                                 position=position_str,
                                 twocolumn=twocolumn))
        self.instance.bookletentry_set.all().delete()
        BookletEntry.objects.bulk_create(entries)


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ('name', 'lyrics')

    def clean_lyrics(self):
        data = lyrics_as_tex(self.cleaned_data['lyrics'])

        try:
            pdflatex(data)
        except TexException as e:
            raise ValidationError(str(e))

        return self.cleaned_data['lyrics']
