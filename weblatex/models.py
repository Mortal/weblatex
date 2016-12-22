from __future__ import division, absolute_import, unicode_literals

import io
import os
import re
import itertools

from django.db import models

from weblatex.fields import PositionField
from weblatex import layout


class Song(models.Model):
    name = models.CharField(max_length=100)
    attribution = models.CharField(max_length=200, blank=True)
    lyrics = models.TextField()

    def __str__(self):
        return self.name


class Booklet(models.Model):
    songs = models.ManyToManyField(Song, through='BookletEntry')
    front_text = models.TextField(blank=True)
    front_image = models.FileField(blank=True)
    contents = models.BooleanField(default=True)

    def layout_song(self, entries):
        (pos, entry), = entries
        return layout.Song(
            entry.song.name,
            entry.song.attribution if entry.attribution else '',
            entry.song.lyrics, entry.twocolumn)

    def layout_rows(self, entries, index):
        def key(x):
            return x[0][index][0]

        t = layout.Rows

        def rec(x):
            return self.layout_cols(x, index)

        if len(entries) == 1:
            return self.layout_song(entries)
        if len(set(map(key, entries))) == 1:
            return rec(entries)
        return t([rec(list(g))
                  for _, g in itertools.groupby(entries, key=key)])

    def layout_cols(self, entries, index):
        def key(x):
            return x[0][index][1]

        t = layout.Cols

        def rec(x):
            return self.layout_rows(x, index+1)

        if len(entries) == 1:
            return self.layout_song(entries)
        if len(set(map(key, entries))) == 1:
            return rec(entries)
        return t([rec(list(g))
                  for _, g in itertools.groupby(entries, key=key)])

    def as_tex(self):
        layout_pages = []
        all_entries = self.bookletentry_set.all()
        all_entries = all_entries.order_by('page', 'position', 'song')
        pages = itertools.groupby(all_entries, key=lambda e: e.page)
        for page, entries in pages:
            entries = ((PositionField.parse_position(e.position), e)
                       for e in entries)
            layout_pages.append(layout.Page(
                self.layout_rows(list(entries), 0)))
        buf = io.StringIO()
        if self.front_text:
            buf.write(self.front_text + '\n')
        if self.front_image:
            filename = os.path.basename(self.front_image.name)
            buf.write('\\noindent\\includegraphics[width=%s\\textwidth]{%s}\n' %
                      ('0.5' if self.front_text else '1', filename))
        if self.front_text or self.front_image:
            buf.write('\\thispagestyle{empty}\\clearpage\n')
        if self.contents:
            buf.write('\\tableofcontents\\clearpage\n')
        for p in layout_pages:
            p.render(buf)
        return buf.getvalue()

    def get_files(self):
        if self.front_image:
            return ((os.path.basename(self.front_image.name),
                     self.front_image),)
        return ()


class BookletEntry(models.Model):
    booklet = models.ForeignKey(Booklet)
    song = models.ForeignKey(Song)
    page = models.IntegerField()
    position = models.CharField(blank=True, max_length=50)

    twocolumn = models.BooleanField()
    attribution = models.BooleanField(default=True)

    class Meta:
        ordering = ['booklet', 'page', 'position']


class UploadedSong(models.Model):
    song = models.ForeignKey(Song)
    source = models.BinaryField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.song)
