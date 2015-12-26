from django import forms
from django.core.exceptions import ValidationError

from weblatex.models import Song, lyrics_as_tex, Booklet, BookletEntry
from weblatex.engine import pdflatex, TexException


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
                'order': self['order_%d' % song.pk],
                'song': song,
                'twocolumn': self['twocolumn_%d' % song.pk],
            })
        return s

    def add_entry(self, i, entry):
        self.fields['order_%d' % entry.song.pk] = forms.IntegerField(
            initial=i + 1, required=False)
        self.fields['twocolumn_%d' % entry.song.pk] = forms.BooleanField(
            initial=entry.twocolumn, required=False)
        self._songs.append(entry.song)

    def add_song(self, song):
        self.fields['order_%d' % song.pk] = forms.IntegerField(
            initial=None, required=False)
        self.fields['twocolumn_%d' % song.pk] = forms.BooleanField(
            initial=False, required=False)
        self._songs.append(song)

    def _save_m2m(self):
        super(BookletForm, self)._save_m2m()
        entries = []
        for s in Song.objects.all():
            order = self.cleaned_data.get('order_%d' % s.pk)
            twocolumn = self.cleaned_data.get('twocolumn_%d' % s.pk)
            if order is not None:
                entries.append(
                    BookletEntry(booklet=self.instance,
                                 song=s,
                                 order=order,
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
