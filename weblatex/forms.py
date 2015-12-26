from django import forms
from django.core.exceptions import ValidationError

from weblatex.models import Song, lyrics_as_tex
from weblatex.engine import pdflatex, TexException


class BookletForm(forms.Form):
    songs = forms.ModelMultipleChoiceField(Song.objects.all())


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ('name', 'lyrics')

    def clean_lyrics(self):
        data = lyrics_as_tex(
            self.cleaned_data['lyrics'], self.cleaned_data['name'])

        try:
            pdflatex(data)
        except TexException as e:
            raise ValidationError(str(e))

        return self.cleaned_data['lyrics']
