from django import forms

from weblatex.models import Song


class BookletForm(forms.Form):
    songs = forms.ModelMultipleChoiceField(Song.objects.all())
