from __future__ import division, absolute_import, unicode_literals

import re

from django.db import models

from weblatex.fields import PageField


def lyrics_as_tex(lyrics):
    lyrics = re.sub(r'\r+\n?', '\n', lyrics)
    lyrics = re.sub(r'^ +| +$', '', lyrics, 0, re.M)
    result = []
    paragraphs = re.split(r'\n\n+', lyrics)
    result.append(r'\begin{enumerate}')
    for p in paragraphs:
        lines = p.splitlines()
        result.append(r'\item %s' % '\\\\\n'.join(lines))
    result.append(r'\end{enumerate}')
    return ''.join('%s\n' % l for l in result)


class Song(models.Model):
    name = models.CharField(max_length=100)
    lyrics = models.TextField()

    def __str__(self):
        return self.name


class Booklet(models.Model):
    songs = models.ManyToManyField(Song, through='BookletEntry')

    def as_tex(self):
        songs = []
        for e in self.bookletentry_set.all():
            position = PageField.parse_position(e.position)
            position = tuple((x1 or 1, x2 or 1) for x1, x2 in position)
            songs.append((page, position, e))
        songs.sort()
        songs = []
        for e in self.bookletentry_set.all():
            song_tex = lyrics_as_tex(e.song.lyrics)
            if e.twocolumn:
                song_tex = r'\begin{multicols}{2}%s\end{multicols}' % song_tex
            songs.append(r'\chapter{%s}%s\clearpage' % (e.song.name, song_tex))
        return '\n'.join(songs)


class BookletEntry(models.Model):
    booklet = models.ForeignKey(Booklet)
    song = models.ForeignKey(Song)
    page = models.IntegerField()
    position = models.CharField(blank=True, max_length=50)

    twocolumn = models.BooleanField()

    class Meta:
        ordering = ['booklet', 'page', 'position']
